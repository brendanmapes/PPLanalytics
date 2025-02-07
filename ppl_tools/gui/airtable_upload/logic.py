import functools
import logging

from pathlib import Path

import pyairtable
import pyairtable.api.types

from PySide6.QtCore import (
    QModelIndex,
    QTimer,
    QThreadPool,
    Slot
    )
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import (
    QErrorMessage,
    QFileDialog,
    QRadioButton,
    QTreeView,
    QMessageBox,
    )

from ppl_tools.gui.airtable_upload.common import TranscriptAction, TranscriptState
from ppl_tools.gui.airtable_upload.models import InterviewRecordModel, TranscriptModel
from ppl_tools.gui.airtable_upload.transcript_processor import TranscriptProcessor

from ppl_tools.gui.common import Worker

from ppl_tools.scripts.airtable_upload import (
    setup_api, get_existing_transcript
    )


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class AirtableUploadLogic:
    def __init__(self, ui):
        self.ui = ui

        # create a model for the lefthand transcript file tree
        self.transcript_model = TranscriptModel()
        # and for the record selection box
        self.record_model = InterviewRecordModel()
        self.ui.recordSelectBox.setModel(self.record_model)
        self.ui.recordSelectBox.setCurrentIndex(-1)

        self.transcript_processor: TranscriptProcessor | None = None

        self.setup_tree_view()

        # watchdog timer to check for stuck transcripts
        self.watchdog_timer = QTimer()
        self.watchdog_timer.timeout.connect(self.check_stuck_transcripts)

        # set up some global state variables

        self.api_table: pyairtable.Table | None = None
        self.transcripts_folder: Path | None = None

        self.transcripts_left_to_process: int = -1

        # flag for when the record select box is populating
        # since that throws the signal `currentIndexChanged`
        # even when we may not want to do anything.
        self.populating_record_combo_box = False

        # add some convenient class variables pointing to UI components,
        # for brevity, and also just in case the object names get changed

        self.radio_buttons: dict[TranscriptAction, QRadioButton] = {
            TranscriptAction.APPEND: self.ui.appendRadioButton,
            TranscriptAction.PREPEND: self.ui.prependRadioButton,
            TranscriptAction.OVERWRITE: self.ui.overwriteRadioButton
        }

        self.setup_radio_buttons()

        # start a thread pool so API calls don't block the main GUI event loop
        self.thread_pool = QThreadPool()

        self.setup_signals()

    def run_async(self, fn, *args, callback=None, err_callback=None):
        """
        Utility function to run a task in a separate thread.
        """
        # add extra keyword arguments that are expected to be accepted
        def add_kwargs(fn):
            def new_fn(*args, progress_callback=None, cancellation_check=None):
                return fn(*args)
            return new_fn

        worker = Worker(add_kwargs(fn), *args)

        if callback:
            worker.signals.result.connect(callback)

        def _handle_err(error_info):
            logger.error(f"Worker thread error: {error_info[1]}\n{error_info[2]}")

        worker.signals.error.connect(err_callback or _handle_err)

        self.thread_pool.start(worker)

    def set_state_row_hidden(self, state: TranscriptState, hide: bool):
        """
        Hide/show the row in the view model for the given `state`.
        """
        index = self.transcript_model.get_state_item_index(state)
        self.tree_view.setRowHidden(index.row(), index.parent(), hide)
    
    def set_state_row_enabled(self, state: TranscriptState, enable: bool):
        """
        Hide/show the row in the view model for the given `state`
        and all its children.
        """
        item = self.transcript_model.states_to_item[state]
        item.setEnabled(enable)

        for child in self.transcript_model.get_transcripts_in_state(state):
            child.setEnabled(enable)


    def setup_tree_view(self):
        self.tree_view: QTreeView = self.ui.transcriptsTreeView
        self.tree_view.setModel(self.transcript_model)

        # hide the header
        self.tree_view.header().hide()

        # hide all rows initially
        for state in TranscriptState:
            self.set_state_row_hidden(state, hide=True)

    def setup_radio_buttons(self):
        for action, radio_button in self.radio_buttons.items():
            radio_button.setText(action.value)

    def setup_signals(self):
        """
        Set up main signal/slot connections for UI components.
        """
        self.ui.folderSelectButton.clicked.connect(self.handle_folder_button_click)

        self.ui.apiKeySubmit.clicked.connect(self.connect_to_api)

        self.tree_view.selectionModel().currentChanged.connect(
            self.update_ui_for_selected_transcript)

        self.ui.recordSelectBox.currentIndexChanged.connect(self.handle_record_select)

        for radio_button in self.radio_buttons.values():
            radio_button.clicked.connect(self.enable_approve_and_flag)


        self.ui.approveButton.clicked.connect(self.handle_approve)
        self.ui.flagButton.clicked.connect(self.handle_flag)

    @Slot(object)
    def on_validation_complete(
        self,
        result: tuple[pyairtable.Table | None, str | None]
        ):
        api_table, err = result

        # Clear the 'Validating...' message
        self.ui.statusbar.clearMessage()

        if err:
            QErrorMessage.qtHandler().showMessage(err)
            self.ui.apiKeyTextEntry.setEnabled(True)
            self.ui.apiKeySubmit.setEnabled(True)
        else:
            self.api_table = api_table
            self.ui.apiKeyTextEntry.setReadOnly(True)

            self.transcript_processor = TranscriptProcessor(self.api_table)
        
            # Process transcripts if validation was successful
            self.process_transcripts()

    @Slot()
    def connect_to_api(self):
        text_entered = self.ui.apiKeyTextEntry.text()

        # Disable input and show loading indicator
        self.ui.apiKeyTextEntry.setEnabled(False)
        self.ui.apiKeySubmit.setEnabled(False)
        self.ui.statusbar.showMessage("Validating Airtable access token...")

        self.run_async(
            setup_api,
            text_entered,
            callback=self.on_validation_complete
            )

    def clear_tree_widget(self):
        """
        Remove all items from the tree widget and all references
        to those items from `self`.
        """
        # clear GUI items
        self.transcript_model.clear_transcripts()
        # hide all state rows
        for state in TranscriptState:
            self.set_state_row_hidden(state, True)
        # clear internal state variables
        self.transcripts_folder = None
        # clear process pane if anything was selected
        self.clear_process_pane()

    @Slot()
    def handle_folder_button_click(self):
        self.clear_tree_widget()
        self.pick_folder()
        self.populate_tree_widget()
        self.process_transcripts()

    @Slot()
    def pick_folder(self):
        """
        Prompt the user to pick a directory. Validates selection to force
        the directory to contain at least one .txt file.
        """
        folder = QFileDialog.getExistingDirectory()
        # check if a folder was already selected
        if not folder:
            err_msg = "Folder not selected! Try again."
            self.ui.folderDisplayText.setText(err_msg)
            return

        folder = Path(folder)
        txt_files_found = len(list(folder.glob("*.txt"))) > 0
        if txt_files_found:
            self.transcripts_folder = folder
            self.ui.folderDisplayText.setText(str(folder))
        else:
            err_msg = "No .txt transcript files found in selected folder! Try again."
            self.ui.folderDisplayText.setText(err_msg)

    @Slot()
    def populate_tree_widget(self):
        """
        Populates the tree widget with the transcript filenames.
        """
        if not self.transcripts_folder:
            logger.warning("Attempted to populate tree widget without valid transcripts folder selected. Returning.")
            return

        transcripts = list(self.transcripts_folder.glob('*.txt'))

        # Add the filenames as children of the display item
        initial_state = TranscriptState.PROCESSING if self.api_table else TranscriptState.WAITING

        # show the state row
        self.set_state_row_hidden(initial_state, hide=False)

        for t in transcripts:
            self.transcript_model.add_transcript(t, state=initial_state)

        # disable it and its children
        self.set_state_row_enabled(initial_state, enable=False)

        self.tree_view.expandAll()


    @Slot(object)
    def handle_single_transcript_result(
        self,
        result: tuple[Path, list[pyairtable.api.types.RecordDict], bool]
        ):
        path, matches, exact_found = result
        transcript_item = self.transcript_model.get_item_by_path(path)

        if transcript_item is None:
            logger.error(f"No transcript item found for path: {path}")
            return

        if not self.transcript_processor:
            logger.error(f"Transcript processor has somehow not yet been initialized.")
            return

        new_state, should_disable = self.transcript_processor.determine_transcript_state(matches, exact_found)

        logger.debug(f"Updating tree for transcript: {transcript_item.text()}")
        self.transcript_model.set_transcript_state(transcript_item, new_state)
        transcript_item.setEnabled(not should_disable)
        transcript_item.setData(matches, self.transcript_model.MATCHES_ROLE)
        self.transcripts_left_to_process -= 1

        logger.debug(f"Transcripts left to process {self.transcripts_left_to_process}")

        # if all transcripts have been processed, hide the PROCESSING
        # state row
        if self.transcripts_left_to_process == 0:
            self.set_state_row_hidden(TranscriptState.PROCESSING, hide=True)
            # very much an edge case, but possible if all had
            # exact matches or no matches: nothing will be in needs attention.
            # check for this, and respond if it happens.
            self.check_processing_complete()
        
    def handle_processing_error(self, transcript_item, error):
        logger.warning(
            f"Error processing transcript {transcript_item.text()}: {error[1]}"
            )
        self.transcript_model.set_transcript_state(
            transcript_item, TranscriptState.FAILED_TO_PROCESS
            )
        self.transcripts_left_to_process -= 1

    @Slot()
    def check_stuck_transcripts(self):
        stuck_transcripts = self.transcript_model.get_transcripts_in_state(TranscriptState.PROCESSING)
        for transcript_item in stuck_transcripts:
            logger.warning(f"Transcript stuck in processing: {transcript_item.text()}")
            self.transcript_model.set_transcript_state(transcript_item, TranscriptState.FAILED_TO_PROCESS)
        # stop the timer
        self.watchdog_timer.stop()

    def update_ui_for_processing_start(self):
        """
        Update the GUI when transcript processing begins.
        """
        # show the other states
        for state in TranscriptState:
            self.set_state_row_hidden(state, hide=False)
            # and set them all to disabled, except 'Needs Attention'
            if state != TranscriptState.NEEDS_ATTENTION:
                self.set_state_row_enabled(state, enable=False)

        # change all transcripts to the processing state
        transcript_items = self.transcript_model.get_transcripts_in_state(
            TranscriptState.WAITING
            )
        for item in transcript_items:
            self.transcript_model.set_transcript_state(
                item, TranscriptState.PROCESSING
                )

        # hide the waiting state
        self.set_state_row_hidden(TranscriptState.WAITING, hide=True)

        # show all files in the processing state
        self.tree_view.expandAll()

    @Slot()
    def process_transcripts(self):
        """
        Fetch matching records for each transcript file and move
        the corresponding tree widget items to drawers accordingly.
        """
        if not self.transcript_model.rowCount() or not self.transcript_processor:
            return

        self.update_ui_for_processing_start()

        transcript_items = self.transcript_model.get_transcripts_in_state(
            TranscriptState.PROCESSING
            )

        self.transcripts_left_to_process = len(transcript_items)

        logger.debug(f"Starting to process {self.transcripts_left_to_process} transcripts.")

        for transcript_item in transcript_items:
            path = transcript_item.data(role=self.transcript_model.FILE_PATH_ROLE)
            self.run_async(
                self.transcript_processor.process_single_transcript,
                path,
                callback=self.handle_single_transcript_result,
                err_callback=functools.partial(self.handle_processing_error, transcript_item)
                )

        # start watchdog timer to catch transcripts that failed to process
        # for whatever reason
        self.watchdog_timer.start(10000)

    def populate_record_select_box(self, transcript_item: QStandardItem):
        # clear, enable, and add placeholder text to the record select box
        self.record_model.clear()
        self.ui.recordSelectBox.clear()
        self.ui.recordSelectBox.setEnabled(True)

        matches = transcript_item.data(self.transcript_model.MATCHES_ROLE)

        self.populating_record_combo_box = True

        self.record_model.setRecords(matches)
        self.ui.recordSelectBox.setCurrentIndex(-1)
        self.ui.recordSelectBox.setPlaceholderText('Select an interview code.')

        self.populating_record_combo_box = False

    @property
    def current_transcript_item(self) -> QStandardItem | None:
        curr_index = self.tree_view.selectionModel().currentIndex()
        return self.transcript_model.itemFromIndex(curr_index)

    @property
    def current_transcript_path(self) -> Path | None:
        if self.current_transcript_item:
            filename = self.current_transcript_item.data(self.transcript_model.FILE_PATH_ROLE)
            return Path(filename)
        return None

    @Slot(QModelIndex, QModelIndex)
    def update_ui_for_selected_transcript(self, idx: QModelIndex, _: QModelIndex):
        item = self.transcript_model.itemFromIndex(idx)
        # ignore if it was from a disabled item or
        # if it was the 'needs attention' drawer item
        not_needs_attention = item != self.transcript_model.states_to_item[TranscriptState.NEEDS_ATTENTION]
        self.clear_process_pane()
        if item.isEnabled() and not_needs_attention:
            self.populate_record_select_box(item)
            # enable flag button
            self.ui.flagButton.setDisabled(False)

    def disable_deselect_radio_buttons(self):
        """
        Deselect and disable all of the append/prepend/overwrite radio buttons.
        """
        self.ui.radioButtonGroup.setExclusive(False)
        for button in self.radio_buttons.values():
            button.setChecked(False)
            button.setDisabled(True)
        self.ui.radioButtonGroup.setExclusive(True)


    def enable_approve_and_flag(self):
        """
        Enable the "Approve..." and "Flag..." UI buttons.
        """
        self.ui.approveButton.setDisabled(False)
        self.ui.flagButton.setDisabled(False)

    def clear_process_pane(self):
        """
        Clear the right-hand 'Process File' pane.
        """
        # update state variables
        # reset current_record and new_transcript values
        # update UI
        # clear record select box
        self.record_model.clear()
        self.ui.recordSelectBox.clear()
        # set it to disabled
        self.ui.recordSelectBox.setDisabled(True)
        # clear transcript viewer widgets
        self.ui.existingTranscriptFrameText.clear()
        self.ui.fromFileTranscriptFrameText.clear()
        # disable and deselect radio buttons
        self.disable_deselect_radio_buttons()
        # disable approve and flag buttons
        self.ui.approveButton.setDisabled(True)
        self.ui.flagButton.setDisabled(True)

    @Slot(str)
    def handle_record_select(self, idx: int):
        # sanity check, if there's no current transcript selected, return
        if not self.current_transcript_path:
            logger.warning('`handle_record_select` erroneously called without a transcript selected! Ignoring.')
            return

        # if the record select box is currently populating,
        # it will throw the currentIndexChanged signal, but we don't
        # want to enable buttons / display transcripts in this case.
        if self.populating_record_combo_box:
            return

        record = self.record_model.getRecord(idx)

        if not record:
            return

        existing_transcript = get_existing_transcript(record)

        if existing_transcript is not None:
            transcript_from_file = self.current_transcript_path.read_text()
            # display transcripts
            self.ui.existingTranscriptFrameText.setText(existing_transcript)
            self.ui.fromFileTranscriptFrameText.setText(transcript_from_file)

            # enable radio buttons
            for action in TranscriptAction:
                self.radio_buttons[action].setEnabled(True)

            # disable approve button
            self.ui.approveButton.setDisabled(True)
        else:
            self.enable_approve_and_flag()

    @Slot(QStandardItem, object)
    def _after_transcript_uploaded(self, transcript_item: QStandardItem, result):
        """
        Slot defining behavior after a given transcript was uploaded.
        """
        # the `result` argument will always be None. just ignore it.
        # move it visually to the uploaded section
        self.transcript_model.set_transcript_state(transcript_item, TranscriptState.UPLOADED)
        # display a message in the status bar saying it was uploaded
        file_path = transcript_item.data(role=self.transcript_model.FILE_PATH_ROLE)
        self.ui.statusbar.showMessage(
            f"The transcript from file '{file_path.name}' has been uploaded, and the file has been moved to the `uploaded_transcripts` subfolder."
            )
        # clear the process file right-hand pane
        self.clear_process_pane()
        # check if all processing is complete
        self.check_processing_complete()

    @property
    def current_action(self) -> TranscriptAction | None:
        checked_button = self.ui.radioButtonGroup.checkedButton()

        if checked_button:
            return TranscriptAction(checked_button.text())
        return None

    def check_processing_complete(self):
        transcripts_to_process = self.transcript_model.get_transcripts_in_state(TranscriptState.NEEDS_ATTENTION)
        
        if not transcripts_to_process:
            flagged_count = len(self.transcript_model.get_transcripts_in_state(TranscriptState.FLAGGED))
            no_matches_count = len(self.transcript_model.get_transcripts_in_state(TranscriptState.NO_MATCHES_FOUND))
            uploaded_count = len(self.transcript_model.get_transcripts_in_state(TranscriptState.UPLOADED))
            
            message = (
                "All transcripts have been processed!\n\n"
                f"- {uploaded_count} transcripts were successfully uploaded to Airtable.\n"
                f"- {flagged_count} transcripts were flagged for manual review and moved to the 'flagged_transcripts' folder.\n"
                f"- {no_matches_count} transcripts had no matching records and were moved to the 'no_matches_found' folder.\n\n"
                "You can now close this window or start a new batch of transcripts."
            )
            
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("Processing Complete")
            msg_box.setText(message)
            msg_box.exec()
            
            # Clear the UI.
            self.ui.folderSelectButton.setEnabled(True)
            self.ui.folderDisplayText.clear()
            self.clear_process_pane()
            self.clear_tree_widget()

    @Slot()
    def handle_approve(self):
        """
        Upload the transcript (or specified modified transcript text) to
        airtable.
        """
        if not self.current_transcript_path or not self.current_transcript_item:
            return

        if not self.transcript_processor:
            return

        curr_transcript = self.current_transcript_path.read_text()
        record = self.record_model.getRecord(self.ui.recordSelectBox.currentIndex())

        if not record:
            logger.info('no record found! returning')
            return

        existing_transcript = get_existing_transcript(record)

        new_transcript = self.transcript_processor.prepare_transcript(
            curr_transcript,
            existing_transcript,
            self.current_action
            )

        self.run_async(
            self.transcript_processor.upload_transcript,
            record, new_transcript,
            callback=functools.partial(
                self._after_transcript_uploaded,
                self.current_transcript_item
                )
            )

    @Slot()
    def handle_flag(self):
        selected_item = self.current_transcript_item
        file_path = self.current_transcript_path

        if not selected_item or not file_path:
            return

        # Create a confirmation dialog
        msg_box = QMessageBox()

        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setText(f"Are you sure you want to flag '{file_path.name}' for manual review?")
        msg_box.setInformativeText("This will move the file to a 'flagged_transcripts' subfolder.")
        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        if msg_box.exec() == QMessageBox.StandardButton.Yes:
            self.transcript_model.set_transcript_state(
                selected_item,
                TranscriptState.FLAGGED
                )
            self.clear_process_pane()

            self.ui.statusbar.showMessage(
                f"The file '{file_path.name}' has been moved to the 'flagged_transcripts' subfolder."
                )
            self.check_processing_complete()
