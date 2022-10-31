'''
This module is used for getting information from Mcfunction files.
'''
from typing import NamedTuple
from pathlib import Path
import re

# Local imports
from .errors import ContentGuideGenerationError, print_error
from .globals import AppConfig
from .utils import filter_paths

# Helper pattern for matching coordinates (int or float, format used by
# Minecraft)
CRDS_PATTERN = r'+(-?(?:[0-9]+)+(?:\.[0-9]*)?)'

# The pattern that matches the beginning of the tp command and captures the
# coordinates
TP_COMMAND_PATTERN = re.compile(
    r'tp(?: @[seap](?:\[.+\])?)? '
    f'{CRDS_PATTERN} {CRDS_PATTERN} {CRDS_PATTERN}')


def _get_crds_from_tp_command(command: str) -> None | tuple[float, float, float]:
    '''
    Gets the coordinates from /tp command and returns coordinates. It only
    gets the beginning needed to extract coordinates, so if the commmand isn't
    completely correct it still might work as longs as there are non-relative
    and non-local coordinates in it.

    It returns None if function fails to extract coordinates.

    :param command: the string with the command
    :returns: tuple of floats with the coordinates or None
    '''
    if match := TP_COMMAND_PATTERN.match(command):
        return (match[1], match[2], match[3])
    return None


def _doc_comment_split(content: str) -> tuple[str, str]:
    '''
    Takes a string with content of a Mcfunction file and splits it into two
    parts, the first one contains the top comment of the file, and the second
    one contains the rest of the file.

    :param content: text of the Mcfunction file

    :returns: tuple of two strings - doc comment and the rest of the file
    '''
    lines = content.split('\n')
    split = 0
    for line in lines:
        if not line.startswith('#'):
            break
        split += 1
    return '\n'.join(lines[:split]), '\n'.join(lines[split:])


def _get_first_command(content: str) -> str | None:
    '''
    Gets the first command from the content of the Mcfunction file. Returns
    the first line whichi isn't blank or a comment. If there is no such line,
    returns None.

    :param content: text of the Mcfunction file

    :returns: the first command
    '''
    for line in content.split('\n'):
        if line != "" and not line.startswith('#'):
            return line
    return None


def _get_text_from_comment(content: str) -> str | None:
    '''
    Removes the comment characters from the beginning of each line. If every
    non-empty line starts with '# ', then it also removes the first space.

    The function expects that every line starts with '#', if not ValueError
    is raised.

    :param content: the content of the comment

    :returns: the content of the comment without comment characters
    '''
    if content == '':
        return None
    lines = content.split('\n')
    strip_first_space = True
    for line in lines:
        if not line.startswith('#'):
            raise ValueError("Not a comment")
        if not line.startswith('# ') and line != '#':
            strip_first_space = False
            # Don't break, because we still want to check if every line starts
            # with '#'
    output: list[str] = []
    for line in lines:
        if strip_first_space:
            output.append(line[2:])
        else:
            output.append(line[1:])
    return '\n'.join(output)


# Completion Guide
class CompletionGuidePart(NamedTuple):
    step_number: int
    step_name: str
    text: str
    mcfunction_name: str

def _parse_completion_guide_function(path: Path) -> CompletionGuidePart | None:
    '''Parse a name of a file into its parts for completion_guide()'''
    # Prepare error for later reuse
    INVALID_FORMAT_ERROR = (
        f"File {path.as_posix()} is named incorrectly for "
        "COMPLETION GUDIE generator:\n"
        "\t- The name should follow pattern <step_number>_<step_name>\n"
        "\t- <step_number> must be an integer\n"
        "\t- <step_name> must be a snake_case string\n"

    )
    # Parse the name
    name = path.stem
    if ' ' in name:
        print_error(
            f"File {path.as_posix()} is named incorrectly for "
            "COMPLETION GUIDE generator:\n"
            "\t- The name uses spaces instead of underscores"
        )
        return None
    split_name = name.split('_')
    if len(split_name) < 2:
        print_error(INVALID_FORMAT_ERROR)
        return None
    try:
        step_number = int(split_name[0])
    except ValueError:
        print_error(INVALID_FORMAT_ERROR)
        return None
    step_name = ' '.join(split_name[1:]).capitalize()
    doc_comment, _ = _doc_comment_split(path.read_text())
    text = _get_text_from_comment(doc_comment)
    if text is None:
        print_error(
            f"File {path.as_posix()} is named incorrectly for "
            "COMPLETION GUIDE generator:\n"
            "\t- The file has no doc comment"
        )
        return None
    mcfunction_name = path.relative_to(
        AppConfig.get().bp_path / 'functions').with_suffix('').as_posix()
    return CompletionGuidePart(step_number, step_name, text, mcfunction_name)


def completion_guide(
        search_patterns: str | list[str],
        exclude_patterns: str | list[str] | None = None) -> str:
    '''
    Generates: DESIGN -> Design -> Completion Guide

    This functions generates text based on functions from:
    BP/functions/guide/test/{step number}_{step name}

    It takes the text from the top comments of the functions anc combines it
    together.
    '''
    functions_path = AppConfig.get().bp_path / 'functions'
    filtered_paths = filter_paths(
        functions_path, search_patterns, exclude_patterns)

    completion_guide_parts: list[CompletionGuidePart] = []
    for path in filtered_paths:
        part = _parse_completion_guide_function(path)
        if part is None:
            continue
        completion_guide_parts.append(part)
    completion_guide_parts = sorted(completion_guide_parts)
    result: list[str] = []
    for part in completion_guide_parts:
        result.append(f'### {part.step_number} - {part.step_name}')
        result.append(part.text + '\n')
        result.append(
            f"You can complete this step using: "
            f"`function {part.mcfunction_name}`\n")
    return '\n'.join(result)

# Info from warp functions
def warp(
        search_patterns: str | list[str],
        exclude_patterns: str | list[str] | None = None) -> str:
    '''
    Generates text from a warp functions that follow specific pattern.
    
    This function can be used for two things:
    - DESIGN -> Navigation -> Key Locations
    - DESIGN -> Navigation -> Landmarks

    The text is generated from the top comments of the functions. The file
    is expected to be in the following format:
    ```
    # {description}
    {tp command}
    ```
    Function uses file name to generate the title, description to provide the
    description and tp command to extract the teleport command coordinates.

    :param search_pattern: the glob pattern used for searching the files in
        BP/functions folder.
    :returns: 
    '''
    functions_path = AppConfig.get().bp_path / 'functions'
    filtered_paths = filter_paths(
        functions_path, search_patterns, exclude_patterns)


    result: list[str] = []
    for path in filtered_paths:
        error_header = (
            f"File {path.as_posix()} has invalid format to summarize using"
            " warp() function.\n"
        )
        # name = " ".join(path.stem.split("_")).capitalize()
        doc_comment, commands = _doc_comment_split(path.read_text())
        doc_comment = _get_text_from_comment(doc_comment)
        if doc_comment is None:
            print_error(error_header + "\t- The file has no doc comment.")
            continue
        first_command = _get_first_command(commands)
        if first_command is None:
            print_error(
                error_header +
                "\t- No commands found (expected tp command below "
                "documentation commmet)")
            continue
        crds = _get_crds_from_tp_command(first_command)
        if crds is None:
            print_error(
                error_header +
                "\t- Unable to extract coordinates from the first command\n"
                "\t- The first command should be a /tp command with "
                "global coordinates")
            continue
        doc_comment = doc_comment.replace("\n", " ")
        result.append(f'- {doc_comment} ({crds[0]} {crds[1]} {crds[2]})')
    return '\n'.join(result)
