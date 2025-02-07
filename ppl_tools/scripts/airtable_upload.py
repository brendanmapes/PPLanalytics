import re
import requests
import shutil
import sys

from argparse import ArgumentParser
from pathlib import Path
from typing import Optional, Tuple

from pyairtable import Api, Table
from pyairtable.formulas import FIELD, FIND, match, OR, STR_VALUE
from pyairtable.api.types import RecordDict

# REDACTED
ACCESS_TOKEN = 'XXXXXX'

PPLANALYTICS_BASE_ID = 'appH3VJgBY454KCIu'
INTERVIEWS_TABLE_ID = 'tblkzqM2L3sujLUwj'
INTERVIEWS_VIEW_ID = 'viwsanb6RXoXg5LXD'

PARTICIPANT_TYPES = ['sme', 'fls', 'mop']

INTERVIEW_CODES_FIELD_ID = 'fld1qU6yB2gVho0tB'
TRANSCRIPT_FIELD_ID = 'fldrVdfgMV4TywAz9'
PROJECT_FIELD_ID = 'fldL5aGM0yLsOsSND'

def setup_api(access_token=ACCESS_TOKEN) -> tuple[Table | None, str | None]:
    api = Api(access_token)
    table = api.table(PPLANALYTICS_BASE_ID, INTERVIEWS_TABLE_ID)

    try:
        table.first()
        return table, None
    except requests.HTTPError as e:
        print(e)
        return None, 'Invalid access token! Please try again.'
    except requests.ConnectionError as e:
        print(e)
        return None, 'Unable to connect. Check your internet connection?'
    except Exception as e:
        return None, 'Unknown error! Please check your access token and try again.'


def get_args():
    p = ArgumentParser()
    p.add_argument("dir")

    return p.parse_args()

def extract_info_from_fname(fname: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    # Create a case-insensitive regex pattern for participant types
    participant_pattern = r"(" + "|".join([re.escape(pt) for pt in PARTICIPANT_TYPES]) + r")"
    # Regex pattern to match the participant type and four-digit code
    basic_pattern = re.compile(
        fr"(?P<participant_type>{participant_pattern})[_ ](?P<code>\d{{4}})",
        re.IGNORECASE
    )
    # Regex pattern to match the optional datetime string
    datetime_pattern = re.compile(r"(?P<datetime>\d{6}_\d{4})")
    # First, extract participant type and code
    basic_match = basic_pattern.search(fname)
    if basic_match:
        participant_type = basic_match.group("participant_type").upper()  # Normalize participant type to uppercase
        code = basic_match.group("code")
        # Optionally look for the datetime string
        datetime_match = datetime_pattern.search(fname)
        datetime_str = datetime_match.group("datetime") if datetime_match else None
        return participant_type, code, datetime_str
    return None, None, None

def search_exact(table: Table, fname: str) -> RecordDict | None:
    formula = match({INTERVIEW_CODES_FIELD_ID: fname})
    return table.first(formula=formula, view=INTERVIEWS_VIEW_ID, return_fields_by_field_id=True)

def remove_duplicates(dict_list: list[RecordDict]) -> list[RecordDict]:
    """Remove duplicate dicts in a list where each dict contains the key 'id'."""
    seen_ids = set()
    unique_list = []
    
    for d in dict_list:
        if d['id'] not in seen_ids:
            seen_ids.add(d['id'])
            unique_list.append(d)
    
    return unique_list

def search_fuzzy(table: Table, fname: str) -> list[RecordDict]:
    """
    Attempt to records based on fuzzy match for interview or participant codes.
    """
    # if exact match doesn't work, attempt to extract information on
    # participant type, participant code, and interview timestamp
    p_type, p_code, intvw_timestamp = extract_info_from_fname(fname)
    # if there is NO information findable in it, p_type and p_code
    # will both be None. in this case, just mark the file as needing manual review
    if p_type is None and p_code is None:
        return []
    # if some information is found, craft a series of fuzzy match strings
    # to assemble possible records that could go with this transcript
    participant_code = f'{p_type}_{p_code}'
    search_attempts = [participant_code]
    if intvw_timestamp:
        interview_code = f'{participant_code}_{intvw_timestamp}'
        search_attempts.append(interview_code)
    
    def _query(search_string):
        return FIND(STR_VALUE(search_string), FIELD(INTERVIEW_CODES_FIELD_ID))

    # execute query
    formula = OR(*map(_query, search_attempts))
    matches = table.all(formula=formula, view=INTERVIEWS_VIEW_ID, return_fields_by_field_id=True)

    # remove any duplicate results
    return remove_duplicates(matches)

def inputmenu(options, description=None):
    while True:
        print("")
        if description:
            print(description)
            print("")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        
        choice = input("\nEnter the number of your choice: ")
        
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return int(choice) - 1
        else:
            print("Invalid input. Please enter a number corresponding to the options.")

def get_record_choice(records: list[RecordDict]) -> RecordDict | None:
    """Returns user choice for record to update, or None if the user opts to add transcript manually."""
    def display_string(record):
        interview_code = record['fields'][INTERVIEW_CODES_FIELD_ID]
        project = record['fields'][PROJECT_FIELD_ID]
        return f"Interview code '{interview_code}', from project '{project}'."

    NONE_OF_THE_ABOVE_OPTION = "None of the above. I'll manually enter this transcript."
    options = [display_string(r) for r in records]
    options.append(NONE_OF_THE_ABOVE_OPTION)

    choice = inputmenu(options, description="Please choose a record to add this transcript to:")
    # if "none of the above" is selected, return None
    return records[choice] if choice < len(options) - 1 else None

def find_matching_records(table: Table, file: Path) -> tuple[list[RecordDict], bool]:
    """
    Attempt to find matching records in `table` for the transcript stored in
    `file`.

    Returns a tuple. First, is a (possibly empty) list of RecordDicts. Second is
    a boolean indicating whether an EXACT match was found. If one was found, the first list
    will contain only this exact match.
    """
    # first try to find an exact match
    if exact_match := search_exact(table, file.stem):
        return [exact_match], True

    # if not, find fuzzy matches
    return search_fuzzy(table, file.stem), False



def find_record_cli(table: Table, file: Path) -> tuple[RecordDict | None, bool]:
    """
    Given an airtable Table and a transcript file, attempt to find a matching record.
    Used ONLY when this file is run as a script. For the version used in the GUI, see
    `find_matching_records`.

    Returns:
        Tuple, where the first entry is a matching record as a RecordDict if found and selected.
        The second entry is a bool indicating whether any matching records were found.
    """

    record = search_exact(table, file.stem)
    match_found = False

    if record is not None:
        print(f'\nEXACT MATCH found for file: {file.name}')
        match_found = True
    else:
        matches = search_fuzzy(table, file.stem)
        if matches:
            print(f'\n{len(matches)} potential matching record(s) found for file: {file.name}')
            # prompt user to choose between the matches
            record = get_record_choice(matches)
            match_found = record is not None
        else:
            print(f'\nNO matching records found for file: {file.name}. Flagging for manual review.')
            record = None

    return record, match_found
    
def handle_transcript_collision(filename: str, transcript_from_file: str, existing_transcript: str):
    """
    Prompts user to decide how to handle a transcript collision.
    Returns None if user wants to manually review.
    """
    def _first_n_lines(s: str, n: int):
        return "\n".join(s.split("\n", maxsplit=n)[:-1]) + "..."
    
    N_TO_PRINT = 5

    print("\nTranscript 1: EXISTING entry ----------")
    print(_first_n_lines(existing_transcript, N_TO_PRINT))

    print(f"\nTranscript 2: entry from FILE {filename} ----------")
    print(_first_n_lines(transcript_from_file, N_TO_PRINT))

    # user's options
    APPEND = "APPEND transcript 2 AFTER transcript 1."
    PREPEND = "PREPEND transcript 2 BEFORE transcript 1."
    OVERWRITE = "OVERWRITE transcript 1, using ONLY transcript 2."
    NONE = "NONE of the above. I'll manually review and decide how to handle this."

    options = [APPEND, PREPEND, OVERWRITE, NONE]

    # results for each option
    return_vals = {
        APPEND: "\n".join((existing_transcript, transcript_from_file)),
        PREPEND: "\n".join((transcript_from_file, existing_transcript)),
        OVERWRITE: transcript_from_file,
        NONE: None
    }

    choice = inputmenu(options)

    return return_vals[options[choice]]

def get_existing_transcript(record) -> str | None:
    """
    Returns the existing value of the transcript field
    in a given record, or None if no transcript exists.
    """
    return record['fields'].get(TRANSCRIPT_FIELD_ID)

def get_interview_code(record) -> str | None:
    """
    Returns the interview code for a record.
    """
    return record['fields'].get(INTERVIEW_CODES_FIELD_ID)
    
def add_new_transcript(table: Table, record: RecordDict, transcript: str) -> str | None:
    """
    Attempts to add new transcript to the given record in the specified table.

    Returns None if successful, or a string error message if the update failed.
    """
    try:
        table.update(record['id'], {TRANSCRIPT_FIELD_ID: transcript})
    except Exception as e:
        return str(e)
    
def main(dirname: str, table: Table):
    directory = Path(dirname)
    txt_files = sorted(directory.glob("*.txt"))
    needs_manual_review = {
        'no_record_found': [],
        'user_specified': []
    }
    for file in txt_files:
        # find a matching record.
        # if multiple fuzzy matches found, prompts user to choose between them.
        # if none are found (or user picks none of the found fuzzy matches), returns None.
        record, match_found = find_record_cli(table, file)

        # if no record was found, flag file for manual review
        if not record:
            reason = 'user_specified' if match_found else 'no_record_found'
            needs_manual_review[reason].append(file)
            continue

        # now read the transcript from the file and attempt to update the matching record.
        transcript_from_file = file.read_text(encoding='utf-8')

        new_transcript_value = None

        # check if a transcript already exists
        if existing_transcript := get_existing_transcript(record):
            interview_code = get_interview_code(record)
            # check if it's the same as (or contained in) the transcript from file,
            # which means the file has already been uploaded
            if transcript_from_file in existing_transcript:
                print(f"Transcript from interview {interview_code} already uploaded! Continuing.")
                continue
            # if so, check how the user wants to handle it.
            print(f"Existing transcript entry found for interview {interview_code}! Please decide how to proceed.")
            # this will return None if the user wants to flag for manual review.
            new_transcript_value = handle_transcript_collision(file.name, transcript_from_file, existing_transcript)
        else:
            # if not, just add it.
            new_transcript_value = transcript_from_file

        # check if `new_transcript_value` is not None (which happens when the user wants to flag)
        # for manual review after a transcript collision
        if new_transcript_value:
            table.update(record['id'], {TRANSCRIPT_FIELD_ID: new_transcript_value})
        else:
            needs_manual_review['user_specified'].append(file)

    # copy manual review files to a separate folder within the dir
    target_folder = directory / 'MANUALLY REVIEW'


    print(
        'Copying files flagged for manual review or for which ' \
        f'no matches could be found to directory {target_folder}.'
        )

    no_record_target = target_folder / 'No Record Found'
    user_flagged = target_folder / 'Flagged by You'
    # Create the target folder if it doesn't exist
    no_record_target.mkdir(parents=True, exist_ok=True)
    user_flagged.mkdir(parents=True, exist_ok=True)

    def _copy(files, dest):
        for file_path in files:
            if file_path.is_file():
                shutil.copy(file_path, dest)
    
    _copy(needs_manual_review['no_record_found'], no_record_target)
    _copy(needs_manual_review['user_specified'], user_flagged)
    


if __name__ == "__main__":
    table, err = setup_api()
    if not table:
        print(err)
        sys.exit()
    args = get_args()
    directory = args.dir

    main(directory, table)

