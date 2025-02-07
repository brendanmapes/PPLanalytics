from enum import Enum

class TranscriptAction(Enum):
    APPEND = 'Append (1 then 2)'
    PREPEND = 'Prepend (2 then 1)'
    OVERWRITE = 'Overwrite (just 2)'

class TranscriptState(Enum):
    WAITING = 'Upload Airtable key to process...'
    PROCESSING = 'Processing...'
    NEEDS_ATTENTION = 'Needs Attention'
    FLAGGED = 'Flagged for Manual Upload'
    NO_MATCHES_FOUND = 'No Matches Found'
    FAILED_TO_PROCESS = 'Failed to Process'
    UPLOADED = 'Uploaded to Airtable!'
