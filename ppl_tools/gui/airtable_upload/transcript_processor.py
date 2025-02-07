import logging
from pathlib import Path
from typing import List, Tuple

from pyairtable.api.types import RecordDict

from ppl_tools.gui.airtable_upload.common import TranscriptAction, TranscriptState
from ppl_tools.scripts.airtable_upload import (
    add_new_transcript, get_existing_transcript, find_matching_records
)

# Set up logger
logger = logging.getLogger(__name__)

class TranscriptProcessor:
    def __init__(self, api_table, max_retries=3):
        self.api_table = api_table
        self.max_retries = max_retries

        logger.info("TranscriptProcessor initialized with API table")

    def process_single_transcript(
        self,
        path: Path
        ) -> Tuple[Path, List[RecordDict], bool] | None:
        """
        Process a single transcript with retries.
        Returns a tuple: (path, matches, exact_found)
        """
        logger.info(f"Processing transcript: {path}")
        for attempt in range(self.max_retries):
            try:
                matches, exact_found = find_matching_records(self.api_table, path)
                logger.info(f"Found {len(matches)} matches for {path}. Exact match: {exact_found}")
                return path, matches, exact_found
            except Exception as e:
                logger.error(f"Error processing transcript {path}: {str(e)}", exc_info=True)
                if attempt == self.max_retries - 1:
                    raise # Re-raise exception if all retries are exhausted.

    def determine_transcript_state(
        self,
        matches: List[RecordDict],
        exact_found: bool
        ) -> Tuple[TranscriptState, bool]:
        """
        Determine the state of a transcript based on processing results.
        Returns a tuple: (TranscriptState, should_disable)
        """
        if exact_found and not get_existing_transcript(matches[0]):
            logger.info("Exact match found with no existing transcript. State: UPLOADED")
            return TranscriptState.UPLOADED, True
        elif not matches:
            logger.info("No matches found. State: NO_MATCHES_FOUND")
            return TranscriptState.NO_MATCHES_FOUND, True
        else:
            logger.info("Matches found, needs attention. State: NEEDS_ATTENTION")
            return TranscriptState.NEEDS_ATTENTION, False

    def prepare_transcript(
        self,
        current_transcript: str,
        existing_transcript: str | None,
        action: TranscriptAction | None
        ) -> str:
        """
        Prepare the final transcript text based on the existing transcript and the chosen action.
        """
        logger.info(f"Preparing transcript with action: {action}")
        if not existing_transcript:
            logger.info("No existing transcript. Using current transcript.")
            return current_transcript

        if action == TranscriptAction.APPEND:
            logger.info("Appending current transcript to existing transcript")
            return "\n".join((existing_transcript, current_transcript))
        elif action == TranscriptAction.PREPEND:
            logger.info("Prepending current transcript to existing transcript")
            return "\n".join((current_transcript, existing_transcript))
        elif action == TranscriptAction.OVERWRITE:
            logger.info("Overwriting existing transcript with current transcript")
            return current_transcript
        else:
            logger.error(f"Invalid action: {action}")
            raise ValueError(f"Invalid action: {action}")

    def upload_transcript(
        self,
        record: RecordDict,
        transcript: str
        ):
        """
        Upload a transcript to Airtable.
        Returns None if successful, or an error message if failed.
        """
        logger.info(f"Attempting to upload transcript for record: {record.get('id')}")
        for attempt in range(self.max_retries):
            try:
                add_new_transcript(self.api_table, record, transcript)
                logger.info(f"Successfully uploaded transcript for record: {record.get('id')}")
            except Exception as e:
                logger.error(f"Failed to upload transcript for record {record.get('id')}: {str(e)}", exc_info=True)
                if attempt == self.max_retries - 1:
                    raise # re-raise exception

    @staticmethod
    def get_transcript_text(transcript_path: Path) -> str:
        """
        Read the transcript text from a file.
        """
        logger.info(f"Reading transcript text from file: {transcript_path}")
        try:
            text = transcript_path.read_text(encoding='utf-8')
            logger.info(f"Successfully read transcript from {transcript_path}")
            return text
        except Exception as e:
            logger.error(f"Failed to read transcript from {transcript_path}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def validate_transcript(transcript_text: str) -> bool:
        """
        Validate the transcript text.
        """
        words = transcript_text.split()
        is_valid = len(words) > 10
        logger.info(f"Validating transcript. Word count: {len(words)}. Is valid: {is_valid}")
        return is_valid
