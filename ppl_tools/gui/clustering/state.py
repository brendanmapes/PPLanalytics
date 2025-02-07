from typing import Optional

import numpy as np
import pandas as pd

class ClusteringState:
    """
    Manages the state of the clustering process, including input data and results.

    This class encapsulates all data related to the clustering process, providing
    methods to set and retrieve data at various stages of the analysis.
    """
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.text_data: Optional[list[str]] = None
        self.embeddings: Optional[np.ndarray] = None
        self.probs: Optional[np.ndarray] = None
        self.dists: Optional[np.ndarray] = None
        self.assignments: Optional[np.ndarray] = None

    def set_data(self, df: pd.DataFrame, text_column: str) -> None:
        """
        Sets the input DataFrame and extracts the text data.

        Args:
            df (pd.DataFrame): The input DataFrame containing the data to be clustered.
            text_column (str): The name of the column in df containing the text data.

        Raises:
            KeyError: If the specified text_column does not exist in the DataFrame.
        """
        if text_column not in df.columns:
            raise KeyError(f"Column '{text_column}' not found in the DataFrame.")
        self.df = df
        self.text_data = df[text_column].tolist()

    def set_embeddings(self, embeddings: np.ndarray) -> None:
        """
        Sets the embeddings created from the text data.

        Args:
            embeddings (np.ndarray): The embeddings array.

        Raises:
            ValueError: If the number of embeddings doesn't match the number of text entries.
        """
        if self.text_data is None:
            raise ValueError("Text data is not set. Call set_data() before set_embeddings().")
        if len(embeddings) != len(self.text_data):
            raise ValueError("Number of embeddings does not match the number of text entries.")
        self.embeddings = embeddings

    def set_clustering_results(self, probs: np.ndarray, dists: np.ndarray, assignments: np.ndarray) -> None:
        """
        Sets the results of the clustering process and updates the DataFrame.

        Args:
            probs (np.ndarray): The probabilities associated with each cluster assignment.
            dists (np.ndarray): The distances of each point to its assigned cluster center.
            assignments (np.ndarray): The cluster assignments for each data point.

        Raises:
            ValueError: If the DataFrame is not set or if the lengths of the input arrays
                        do not match the number of rows in the DataFrame.
        """
        if self.df is None:
            raise ValueError("DataFrame is not set. Call set_data() before set_clustering_results().")
        if len(probs) != len(self.df) or len(dists) != len(self.df) or len(assignments) != len(self.df):
            raise ValueError("Length of clustering results does not match the number of rows in the DataFrame.")

        self.probs = probs
        self.dists = dists
        self.assignments = assignments
        self.df['probs'] = self.probs.tolist()
        self.df['dists'] = self.dists.tolist()
        self.df['assignments'] = self.assignments

    def clear(self) -> None:
        """
        Resets all attributes to their initial state.
        """
        self.__init__()
