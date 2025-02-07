from pathlib import Path
import shutil

from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex
from PySide6.QtGui import QStandardItem, QStandardItemModel

from ppl_tools.gui.airtable_upload.common import TranscriptState
from ppl_tools.scripts.airtable_upload import get_interview_code


class InterviewRecordModel(QAbstractListModel):
    RECORD_DATA_ROLE = Qt.ItemDataRole.UserRole

    def __init__(self, parent=None):
        super().__init__(parent)
        self._records = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._records)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._records)):
            return None

        record = self._records[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return get_interview_code(record)
        elif role == self.RECORD_DATA_ROLE:
            return record
        return None

    def setRecords(self, records):
        self.beginResetModel()
        self._records = records
        self.endResetModel()

    def getRecord(self, index):
        if 0 <= index < len(self._records):
            return self._records[index]
        return None

    def findRecordByInterviewCode(self, interview_code):
        for record in self._records:
            if get_interview_code(record) == interview_code:
                return record
        return None

    def clear(self):
        self.beginResetModel()
        self._records.clear()
        self.endResetModel()


class TranscriptModel(QStandardItemModel):

    FILE_PATH_ROLE = Qt.ItemDataRole.UserRole
    MATCHES_ROLE = Qt.ItemDataRole.UserRole + 1

    def __init__(self):
        super().__init__()
        self.setHorizontalHeaderLabels(['Transcripts'])

        self._setup_state_items()


    def _setup_state_items(self):
        """
        Set up top-level items within the tree view component
        corresponding to the various states a transcript can be in.
        """
        self.states_to_item: dict[TranscriptState, QStandardItem] = {}
        for state in TranscriptState:
            item = QStandardItem(state.value)
            item.setEditable(False)

            self.states_to_item[state] = item

            self.appendRow(item)

    def add_transcript(self, file_path: Path, state: TranscriptState):
        transcript_item = QStandardItem(file_path.name)
        transcript_item.setData(file_path, self.FILE_PATH_ROLE)
        transcript_item.setEditable(False)
        self.states_to_item[state].appendRow(transcript_item)
        return transcript_item

    def get_transcript_state(self, transcript_item: QStandardItem) -> TranscriptState | None:
        parent = transcript_item.parent()
        for state, item in self.states_to_item.items():
            if item == parent:
                return state
        return None

    def set_transcript_state(self, transcript_item: QStandardItem, new_state: TranscriptState):
        # remove the row from its current parent
        current_parent = transcript_item.parent()
        item = current_parent.takeRow(transcript_item.row())
        new_parent = self.states_to_item[new_state]
        # add it to the new parent
        new_parent.appendRow(item)

        # Disable the item if it's in a final state
        if new_state in [
            TranscriptState.FLAGGED,
            TranscriptState.NO_MATCHES_FOUND,
            TranscriptState.UPLOADED,
            TranscriptState.FAILED_TO_PROCESS,
            ]:
            transcript_item.setEnabled(False)

        # move the transcript file in the filetree if necessary
        current_path = Path(transcript_item.data(role=self.FILE_PATH_ROLE))

        # Define subfolder names
        subfolders = {
            TranscriptState.FLAGGED: "flagged_transcripts",
            TranscriptState.NO_MATCHES_FOUND: "no_matches_found",
            TranscriptState.UPLOADED: "uploaded_transcripts",
            TranscriptState.FAILED_TO_PROCESS: "failed_to_process"
        }
        
        # Move file if necessary
        if new_state in subfolders:
            subfolder = current_path.parent / subfolders[new_state]
            subfolder.mkdir(exist_ok=True)
            new_path = subfolder / current_path.name
            shutil.copy(str(current_path), str(new_path))

    def get_transcripts_in_state(self, state: TranscriptState) -> list[QStandardItem]:
        item = self.states_to_item[state]
        return [item.child(i) for i in range(item.rowCount())]

    def get_state_item_index(self, state: TranscriptState) -> QModelIndex:
        return self.indexFromItem(self.states_to_item[state])

    def clear_transcripts(self):
        for state in TranscriptState:
            item = self.states_to_item[state]
            item.removeRows(0, item.rowCount())

    def get_item_by_path(self, path: Path) -> QStandardItem | None:
        """
        Retrieve the QStandardItem corresponding to the given file path.
        """
        for state in TranscriptState:
            state_item = self.states_to_item[state]
            for row in range(state_item.rowCount()):
                item = state_item.child(row)
                if item.data(self.FILE_PATH_ROLE) == path:
                    return item
        return None  # Return None if no matching item is found
