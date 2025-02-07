import io
import os
import re
import shutil
import sys
import tempfile

from contextlib import contextmanager
from pathlib import Path
from typing import Callable, IO

import numpy as np
import pandas as pd

from PySide6.QtCore import QObject, QThreadPool, Signal, SignalInstance, Slot
from sentence_transformers import SentenceTransformer

from ppl_tools.gui.clustering.state import ClusteringState
from ppl_tools.gui.common import Worker
from ppl_tools.scripts.cluster import ClusteringConfig, cluster, make_plot


class ProgressCapture(io.StringIO):
    """
    A custom StringIO class that captures output and emits progress updates.

    This class intercepts written strings, looks for iteration information,
    and emits progress updates through a callback function.

    Attributes:
        progress_callback (callable): A function to call with progress updates.
    """

    def __init__(self, progress_callback, cancellation_check):
        """
        Initialize the ProgressCapture.

        Args:
            progress_callback (SignalInstance): a SignalInstance to which the progress should be
                                      emitted.
            cancellation_check (Callable): a Callable returning a bool representing whether the
                                      task has been cancelled.
        """
        super().__init__()
        self.progress_callback = progress_callback
        self.cancellation_check = cancellation_check

    def write(self, s):
        """
        Write a string to the StringIO buffer and check for progress updates.

        If the string contains a percentage, extract the percentage number and
        emit it. If it contains iteration information, extract the iteration
        number and emit it as a progress update. 

        Args:
            s (str): The string to write.
        """
        chars_written = super().write(s)
        if not self.cancellation_check():
            if '%' in s:
                # Try to extract progress percentage
                match = re.search(r'(\d+)%', s)
                if match:
                    progress = int(match.group(1))
                    self.progress_callback.emit(progress)
            elif 'Iteration' in s:
                # Extract iteration for clustering progress
                match = re.search(r'Iteration (\d+)', s)
                if match:
                    iteration = int(match.group(1))
                    self.progress_callback.emit(iteration)
        return chars_written


@contextmanager
def capture_progress(
    progress_callback: SignalInstance,
    cancellation_check: Callable[[], bool]
    ):
    """
    A context manager that captures stdout and emits progress updates.

    This context manager temporarily replaces sys.stdout with a ProgressCapture
    instance, allowing it to intercept and process output for progress tracking.

    Args:
        progress_callback (SignalInstance): A SignalInstance to which progress
        updates should be emitted.

    Yields:
        ProgressCapture: The ProgressCapture instance capturing the output.

    Example:
        with capture_progress(update_progress_bar) as capture:
            run_long_process()
        # Progress bar is updated during process execution
    """
    capture = ProgressCapture(progress_callback, cancellation_check)
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = capture
    sys.stderr = capture
    try:
        yield capture
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


class ClusteringModel(QObject):
    file_loaded = Signal()
    column_set = Signal()
    model_loaded = Signal()
    embeddings_created = Signal()
    clustering_complete = Signal()
    plot_generated = Signal(str)  # Emits the path to the temporary plot file
    error_occurred = Signal(str)
    progress_updated = Signal(tuple)

    def __init__(self):
        super().__init__()
        self._csv_filename: Path | None = None
        self._df: pd.DataFrame | None = None
        self._clustering_state = ClusteringState()
        self._embedding_model: SentenceTransformer | None = None
        self._tmp_plot_file: IO | None = None

        self.thread_pool = QThreadPool()

    @property
    def df(self):
        return self._df

    @property
    def csv_filename(self):
        return self._csv_filename

    @property
    def clustering_state(self):
        return self._clustering_state

    def _handle_error(self, error_message: str):
        self.error_occurred.emit(error_message)

    def load_file(self, file_path: Path):
        try:
            self._df = pd.read_csv(file_path)
            self._csv_filename = file_path
            self.file_loaded.emit()
        except Exception as e:
            self._handle_error(f"Failed to load file: {str(e)}")

    def validate_column(self, column: str) -> bool:
        if self._df is None:
            self._handle_error("No data loaded. Please load a file first.")
            return False
        
        if column not in self._df.columns:
            self._handle_error(f"Column '{column}' not found in the data.")
            return False
        
        # Check if the column contains text data
        if not pd.api.types.is_string_dtype(self._df[column]):
            self._handle_error(f"Column '{column}' does not contain text data.")
            return False
        
        # Check if the column has a reasonable amount of text
        mean_length = self._df[column].astype(str).str.len().mean()
        if mean_length < 10:  # You can adjust this threshold
            self.error_occurred.emit(f"Column '{column}' appears to contain very short text. Please verify.")
            return False
        
        return True

    def set_text_column(self, column: str):
        if self._df is None:
            self._handle_error("Please select a CSV file before attempting to select a column.")
            return

        self.validate_column(column)

        try:
            self._clustering_state.set_data(self._df, column)
            self.column_set.emit()
        except Exception as e:
            self._handle_error(f'Failed to set text column: {str(e)}')

    def load_embedding_model(self, model_name: str):
        worker = Worker(self._load_embedding_model_task, model_name)
        worker.signals.result.connect(self._on_model_loaded)
        progress_msg = "Loading embedding model..."
        worker.signals.progress.connect(lambda v: self.progress_updated.emit((progress_msg, v)))

        self.thread_pool.start(worker)

    def _load_embedding_model_task(self, model_name: str, progress_callback, cancellation_check):
        try:
            model = SentenceTransformer(model_name)
            if not cancellation_check():
                progress_callback.emit(100)
                return model
        except Exception as e:
            self._handle_error(f"Failed to load embedding model: {str(e)}")

    def _on_model_loaded(self, model):
        if model is not None:
            self._embedding_model = model
            self.model_loaded.emit()

    def create_embeddings(self):
        if self._clustering_state.text_data is None:
            self.error_occurred.emit("No text data available. Please set a valid text column first.")
            return
        if self._embedding_model is None:
            self.error_occurred.emit("No embedding model loaded. Please load a model first.")
            return

        worker = Worker(self._create_embeddings_task)
        worker.signals.result.connect(self._on_embeddings_created)
        progress_msg = "Creating embeddings..."
        worker.signals.progress.connect(lambda v: self.progress_updated.emit((progress_msg, v)))

        self.thread_pool.start(worker)

    def _create_embeddings_task(self, progress_callback, cancellation_check):
        if self._clustering_state.text_data is None:
            self._handle_error("No text data available. Please set a valid text column first.")
            return
        if self._embedding_model is None:
            self._handle_error("No embedding model loaded. Please load a model first.")
            return
        try:
            # to avoid getting a warning printed. see this link for more:
            # https://stackoverflow.com/questions/62691279/how-to-disable-tokenizers-parallelism-true-false-warning
            os.environ["TOKENIZERS_PARALLELISM"] = "false"
            with capture_progress(progress_callback, cancellation_check):
                embeddings = self._embedding_model.encode(
                    self._clustering_state.text_data,
                    show_progress_bar=True
                )
            if not cancellation_check():
                progress_callback.emit(100)
                return np.array(embeddings)
        except Exception as e:
            self._handle_error(f"Failed to create embeddings: {str(e)}")

    @Slot(np.ndarray)
    def _on_embeddings_created(self, embeddings: np.ndarray):
        self._clustering_state.set_embeddings(embeddings)
        self.embeddings_created.emit()

    def perform_clustering(self, config: ClusteringConfig):
        worker = Worker(self._perform_clustering_task, config)
        worker.signals.result.connect(self._on_clustering_complete)
        progress_msg = "Performing clustering..."
        worker.signals.progress.connect(lambda v: self.progress_updated.emit((progress_msg, v)))

        self.thread_pool.start(worker)

    def _perform_clustering_task(self, config: ClusteringConfig, progress_callback, cancellation_check):
        if self._clustering_state.embeddings is None:
            self._handle_error("No embeddings available. Please create embeddings first.")
            return
        try:
            with capture_progress(progress_callback, cancellation_check):
                probs, dists, assignments = cluster(self._clustering_state.embeddings, config)
            if not cancellation_check():
                progress_callback.emit(100)
                return probs, dists, assignments
        except Exception as e:
            self._handle_error(f"Clustering failed: {str(e)}")

    def _on_clustering_complete(self, results):
        probs, dists, assignments = results
        self._clustering_state.set_clustering_results(probs, dists, assignments)
        self.clustering_complete.emit()

    def generate_plot(self):
        if self._df is None or self._clustering_state.text_data is None or self._clustering_state.assignments is None:
            self._handle_error("Cannot generate plot: missing data or clustering results.")
            return

        try:
            n_datapoints = len(self._clustering_state.text_data)
            # Create a temporary DataFrame with the necessary columns
            temp_df = pd.DataFrame({
                'Key Data Points': self._clustering_state.text_data,
                'Participant Code': self._df.get('Participant Code', ['Unknown'] * n_datapoints),
                'Project': self._df.get('Project', ['Unknown'] * n_datapoints)
            })

            # Create a temporary file to save the plot
            self._tmp_plot_file = tempfile.NamedTemporaryFile(
                mode='w', suffix='.html', delete=False
                )
            
            # Generate the plot
            make_plot(
                temp_df,
                self._clustering_state.embeddings,
                self._clustering_state.assignments,
                out_file=self._tmp_plot_file.name
            )

            self.plot_generated.emit(self._tmp_plot_file.name)
        except Exception as e:
            self._handle_error(f"Failed to generate plot: {str(e)}")

    def export_csv(self, path: Path) -> bool:
        if self._df is None:
            self._handle_error("No data available to export.")
            return False
        try:
            self._df.to_csv(path, index=False)
            return True
        except Exception as e:
            self._handle_error(f"Failed to export CSV: {str(e)}")
            return False

    def export_html(self, path: Path) -> bool:
        if self._tmp_plot_file is None:
            self._handle_error("No plot generated. Please generate the plot first.")
            return False
        try:
            shutil.copy(self._tmp_plot_file.name, str(path))
            return True
        except Exception as e:
            self._handle_error(f"Failed to export HTML: {str(e)}")
            return False

    def reset(self):
        self._df = None
        self._clustering_state.clear()
        self._file_path = None
        if self._tmp_plot_file:
            self._tmp_plot_file.close()
            self._tmp_plot_file = None
