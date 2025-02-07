import logging

from pathlib import Path

from PySide6.QtCore import Qt, QUrl, Slot
from PySide6.QtStateMachine import QState, QStateMachine
from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget

from ppl_tools.gui.clustering.model import ClusteringModel
from ppl_tools.gui.clustering.cluster_tab_ui import ClusterTabUI
from ppl_tools.gui.common import Worker
from ppl_tools.scripts.cluster import ClusteringConfig, ClusteringModelType, CovarianceType


logger = logging.getLogger(__name__)
fh = logging.FileHandler(Path.cwd() / 'log/cluster.log')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


class ClusterTab(QWidget):
    def __init__(self):
        super().__init__()

        self.csv_filename: Path | None = None

        self.ui = ClusterTabUI()
        self.ui.setup_ui(self)
        self.setup_ui_signals()

        self.setup_state_machine()

        self.clustering_model = ClusteringModel()
        self.setup_model_signals()

        self.clustering_config: ClusteringConfig | None = None
        self.embedding_model_type: str = ''

        self.cancellation_flag: bool = False

        self.current_task: Worker | None = None

        self.downloaded_csv: bool = False
        self.downloaded_html: bool = False

    def setup_ui_signals(self):
        self.ui.column_combo.currentIndexChanged.connect(self.handle_column_selection)
        # model options inputs --
        self.ui.advanced_checkbox.checkStateChanged.connect(self.toggle_advanced_options)
        self.ui.cluster_model_combo.currentIndexChanged.connect(self.update_model_options)
        # control pane --
        # this is a UI signal instead of a direct state transition because
        # we prompt the user to confirm with a message box if they haven't
        # downloaded the results
        self.ui.new_analysis_btn.clicked.connect(self.handle_new_analysis_clicked)
        # export options --
        self.ui.export_csv_btn.clicked.connect(self.export_csv)
        self.ui.export_html_btn.clicked.connect(self.export_html)

    def setup_model_signals(self):
        self.clustering_model.file_loaded.connect(self.file_selection_state.finished)
        self.clustering_model.column_set.connect(self.column_selection_state.finished)
        self.clustering_model.model_loaded.connect(self.loading_model_state.finished)
        self.clustering_model.embeddings_created.connect(self.creating_embeddings_state.finished)
        self.clustering_model.clustering_complete.connect(self.performing_clustering_state.finished)

        self.clustering_model.plot_generated.connect(self.display_plot)
        self.clustering_model.error_occurred.connect(self.on_error)
        self.clustering_model.progress_updated.connect(self.on_progress_updated)

    @Slot(tuple)
    def on_progress_updated(self, progress_info):
        message, value = progress_info
        self.ui.progress_label.setText(message)
        self.ui.progress_bar.setValue(value)

    def cancel_analysis(self):
        if self.current_task:
            self.current_task.cancel()

        self.cancellation_flag = True
        # Implement cancellation logic here
        self.clustering_model.thread_pool.clear()
        self.ui.results_label.setText("Clustering cancelled.")
        self.state_machine.setInitialState(self.idle_state)
        self.state_machine.start()


    def setup_state_machine(self):
        self.state_machine = QStateMachine(self)

        # Create states
        self.idle_state = QState()
        self.file_selection_state = QState()
        self.column_selection_state = QState()
        self.ready_state = QState()
        self.loading_model_state = QState()
        self.creating_embeddings_state = QState()
        self.performing_clustering_state = QState()
        self.analysis_complete_state = QState()

        # Add states to the state machine
        self.state_machine.addState(self.idle_state)
        self.state_machine.addState(self.file_selection_state)
        self.state_machine.addState(self.column_selection_state)
        self.state_machine.addState(self.ready_state)
        self.state_machine.addState(self.loading_model_state)
        self.state_machine.addState(self.creating_embeddings_state)
        self.state_machine.addState(self.performing_clustering_state)
        self.state_machine.addState(self.analysis_complete_state)

        # Set the initial state
        self.state_machine.setInitialState(self.idle_state)

        # UI-triggered transitions --
        # start file selection
        self.idle_state.addTransition(self.ui.file_btn.clicked, self.file_selection_state)
        # start analysis
        self.ready_state.addTransition(self.ui.run_btn.clicked, self.loading_model_state)
        # restart file selection
        self.file_selection_state.addTransition(self.ui.file_btn.clicked, self.file_selection_state)
        self.column_selection_state.addTransition(self.ui.file_btn.clicked, self.file_selection_state)
        self.ready_state.addTransition(self.ui.file_btn.clicked, self.file_selection_state)
        # reset for new analysis
        self.analysis_complete_state.addTransition(self.analysis_complete_state.finished, self.idle_state)

        # Task completion transitions
        self.file_selection_state.addTransition(self.file_selection_state.finished, self.column_selection_state)
        self.column_selection_state.addTransition(self.column_selection_state.finished, self.ready_state)
        self.loading_model_state.addTransition(self.loading_model_state.finished, self.creating_embeddings_state)
        self.creating_embeddings_state.addTransition(self.creating_embeddings_state.finished, self.performing_clustering_state)
        self.performing_clustering_state.addTransition(self.performing_clustering_state.finished, self.analysis_complete_state)

        # Cancellation transitions
        for state in [self.loading_model_state, self.creating_embeddings_state, self.performing_clustering_state]:
            state.addTransition(self.ui.cancel_btn.clicked, self.ready_state)

        # Connect states to functions
        self.idle_state.entered.connect(self.on_idle_state_entered)
        self.file_selection_state.entered.connect(self.on_file_selection_state_entered)
        self.column_selection_state.entered.connect(self.on_column_selection_state_entered)
        self.ready_state.entered.connect(self.on_ready_state_entered)
        self.loading_model_state.entered.connect(self.on_loading_model_state_entered)
        self.creating_embeddings_state.entered.connect(self.on_creating_embeddings_state_entered)
        self.performing_clustering_state.entered.connect(self.on_performing_clustering_state_entered)
        self.analysis_complete_state.entered.connect(self.on_analysis_complete_state_entered)

        # Start the state machine
        self.state_machine.start()

    def reset_ui(self):
        # file select pane
        self.ui.file_btn.setText('Select CSV File')
        self.ui.file_label.setText('No file selected')
        self.ui.file_label.setStyleSheet("color: gray;")
        self.ui.file_btn.setEnabled(True)
        # prep combo box
        self.ui.column_combo.clear()
        self.ui.column_combo.setEnabled(False)
        self.ui.run_btn.setEnabled(False)
        self.ui.model_options_group.setEnabled(False)
        self.ui.progress_widget.hide()
        self.ui.cancel_btn.hide()
        self.ui.new_analysis_btn.hide()
        self.ui.export_group.hide()
        # clear the web view widget
        self.ui.web_view.setHtml('')
        self.ui.web_view.hide()
        self.ui.results_label.setText("Select a file to begin.")
        self.ui.results_label.show()

    def on_idle_state_entered(self):
        # reset state variables
        self.csv_filename = None
        self.clustering_model.reset()
        self.cancellation_flag = False
        self.downloaded_csv = False
        self.downloaded_html = False
        self.reset_ui()

    def on_file_selection_state_entered(self):
        self.reset_ui()
        self.select_file()

    def on_column_selection_state_entered(self):
        # display selected CSV
        self.ui.file_label.setText(self.clustering_model.csv_filename.name)
        self.ui.file_label.setStyleSheet("color: black;")
        # change button text to reflect that a file has been selected
        self.ui.file_btn.setText('Select New CSV File')
        # enable column selection
        self.ui.column_combo.setEnabled(True)
        self.ui.column_combo.setPlaceholderText("Select a text column")
        self.ui.column_combo.clear()
        self.ui.column_combo.addItems(list(self.clustering_model.df.columns))
        self.ui.column_combo.setEnabled(True)

    def on_ready_state_entered(self):
        self.cancel_analysis()
        # UI updates --
        # enable file/column select pane
        self.ui.file_btn.setEnabled(True)
        self.ui.column_combo.setEnabled(True)
        # model options
        self.ui.model_options_group.setEnabled(True)
        # control pane
        self.ui.cancel_btn.hide()
        self.ui.run_btn.setEnabled(True)
        # results pane
        self.ui.progress_widget.hide()
        self.ui.results_label.setText("Ready to run clustering analysis.")
        self.ui.results_label.show()

    def on_loading_model_state_entered(self):
        # UI updates --
        # file/column select pane
        self.ui.file_btn.setEnabled(False)
        self.ui.column_combo.setEnabled(False)
        # model options pane
        self.set_model_options_enabled(False)
        # control pane
        self.ui.run_btn.setEnabled(False)
        self.ui.cancel_btn.show()
        # results pane
        self.ui.results_label.hide()
        self.ui.progress_widget.show()
        self.ui.progress_bar.setValue(0)
        self.ui.progress_label.setText("Loading embedding model...")

        # logic --
        self.collect_model_options()
        # logger.debug(f'Options collected: {self.options}')
        logger.debug(f'Attempting to load model...')
        self.clustering_model.load_embedding_model(self.embedding_model_type)
        # self.current_task = self.load_embedding_model()

    def on_creating_embeddings_state_entered(self):
        self.ui.results_label.hide()
        self.ui.progress_widget.show()
        self.ui.progress_bar.setValue(0)
        self.ui.progress_label.setText("Creating embeddings...")

        # self.current_task = self.create_embeddings()
        self.clustering_model.create_embeddings()

    def on_performing_clustering_state_entered(self):
        self.ui.results_label.hide()
        self.ui.progress_widget.show()
        self.ui.progress_bar.setValue(0)
        self.ui.progress_label.setText("Performing clustering...")

        # self.current_task = self.perform_clustering()
        self.clustering_model.perform_clustering(self.clustering_config)

    def collect_model_options(self):
        self.embedding_model_type = self.ui.model_combo.currentText()

        self.clustering_config = ClusteringConfig()

        self.clustering_config.n_clusters = int(self.ui.cluster_spin.value())
        self.clustering_config.max_iter = int(self.ui.max_iter_spin.value())

        weight_concentration_prior: float | None = None
        
        if self.ui.cluster_model_combo.currentText() == 'Gaussian Mixture':
            clustering_model = ClusteringModelType.GMM
            covariance_type = CovarianceType(self.ui.gm_covariance_type.currentText())
        else:
            clustering_model = ClusteringModelType.DPGMM
            covariance_type = CovarianceType(self.ui.bgm_covariance_type.currentText())
            weight_concentration_prior = self.ui.bgm_weight_concentration_prior.value()

        self.clustering_config.model_type = clustering_model
        self.clustering_config.covariance_type = covariance_type
        self.clustering_config.weight_concentration_prior = weight_concentration_prior

    def on_analysis_complete_state_entered(self):
        # UI updates --
        # export options
        self.ui.export_group.show()
        # results pane
        self.ui.progress_widget.hide()
        self.ui.results_label.setText("Analysis complete.")
        # control pane
        self.ui.cancel_btn.hide()
        self.ui.new_analysis_btn.show()
        # display cluster TSNE visualization --
        self.clustering_model.generate_plot()

    def set_model_options_enabled(self, enabled: bool):
        self.ui.model_options_group.setEnabled(enabled)
        self.ui.file_btn.setEnabled(enabled)
        self.ui.column_combo.setEnabled(enabled)

    @Slot(Qt.CheckState)
    def toggle_advanced_options(self, state):
        self.ui.advanced_group.setVisible(state == Qt.CheckState.Checked)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_path:
            file_path = Path(file_path)
            self.clustering_model.load_file(file_path)

    @Slot(int)
    def handle_column_selection(self, idx):
        if idx >= 0 and self.clustering_model.df is not None:
            column = self.ui.column_combo.currentText()
            self.clustering_model.set_text_column(column)

    def update_model_options(self):
        is_bayesian = self.ui.cluster_model_combo.currentText() == 'Bayesian Gaussian Mixture'
        self.ui.model_options_stack.setCurrentIndex(1 if is_bayesian else 0)

    @Slot(int)
    def display_load_model_progress(self, prog: int):
        self.ui.progress_bar.setValue(prog)

    @Slot(int)
    def display_embedding_progress(self, prog: int):
        self.ui.progress_bar.setValue(prog)

    @Slot(int)
    def display_clustering_progress(self, iter: int):
        if not self.clustering_config:
            return
        progress = round(100 * (iter / self.clustering_config.max_iter))
        logger.debug(f'displaying clustering progress: {progress}')
        self.ui.progress_bar.setValue(progress)

    @Slot(tuple)
    def on_error(self, error_info):
        # error_type, error_value, _ = error_info
        # QMessageBox.critical(self, "Error", f"An error occurred: {error_type.__name__}: {error_value}")
        QMessageBox.critical(self, "Error", f"An error occurred: {error_info}")
        self.ui.progress_widget.hide()
        self.ui.results_label.setText("Clustering failed. Please try again.")

        self.set_model_options_enabled(True)

    @Slot(str)
    def display_plot(self, plot_file_path: str):
        logger.debug(
            'Attempting to display following file in a QWebEngineView: ' +
            str(QUrl.fromLocalFile(plot_file_path))
            )
        self.ui.web_view.load(QUrl.fromLocalFile(plot_file_path))
        self.ui.web_view.show()

    def export_csv(self):
        if self.csv_filename is None:
            logger.error('No csv filename.')
            return
        # CSV export
        default_out_dir = self.csv_filename.parent
        fname = '[Clustered] ' + self.csv_filename.name

        out_path, _ = QFileDialog.getSaveFileName(
            dir=str(default_out_dir / fname),
            filter='CSV Files (*.csv)'
            )
        if out_path:
            success = self.clustering_model.export_csv(Path(out_path))
        else:
            success = False
        self.downloaded_csv = success


    def export_html(self):
        if self.csv_filename is None:
            logger.error('No csv filename.')
            return
        # CSV export
        default_out_dir = self.csv_filename.parent
        fname = '[Visualization] ' + self.csv_filename.stem + '.html'

        out_path, _ = QFileDialog.getSaveFileName(
            dir=str(default_out_dir / fname),
            filter='HTML Files (*.html)'
            )
        success = self.clustering_model.export_html(Path(out_path))
        if out_path:
            success = self.clustering_model.export_html(Path(out_path))
        else:
            success = False
        self.downloaded_html = success

    def handle_new_analysis_clicked(self):
        start_new_analysis = True

        # prompt to confirm
        if not self.downloaded_html or not self.downloaded_csv:
            start_new_analysis = self.confirm_new_analysis()

        # if confirmed (or both results files downloaded), start new analysis
        if start_new_analysis:
            self.analysis_complete_state.finished.emit()

    def confirm_new_analysis(self) -> bool:
        msg_box = QMessageBox()

        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setText(f"Are you sure you want to start a new analysis without saving?")
        msg_box.setInformativeText(
            "This will delete anything (cluster assignments or visualization) you didn't explicitly export."
            )
        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        return msg_box.exec() == QMessageBox.StandardButton.Yes
