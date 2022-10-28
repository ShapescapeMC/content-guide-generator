'''
The main module with the script
'''
from typing import Callable
from json import JSONDecodeError
import json


# Local imports
from .errors import print_error
from .entities import list_entities, summarize_entities, summarize_entities_in_tables
from .items import summarize_items, summarize_items_in_tables, list_items
from .functions import completion_guide, warp
from .sound_definitions import sound_definitions
from .globals import DATA_PATH


def _split_func_parts(func: str) -> tuple[str, list] | None:
    '''
    Splits the parts of a function written using the following format:
    function_name(arg1, arg2, argX). Returns the tuple with the name of the
    function and a list of its arguments. Returns None if the function has
    invalid format.

    :param func: the function to split
    :returns: tuple with the name of the function and a list of its arguments
    '''
    if not func.endswith(')'):
        return None
    func_name, rest = func[:-1].split('(', 1)
    # TODO - this is a hack (using JSON to parse the arguments)
    #        it should be replaced with a proper parser
    try:
        args = json.loads(f'[{rest}]')
    except JSONDecodeError:
        return None
    return func_name, args


def _parse_template(text: str) -> list[str | tuple[str, list]]:
    '''
    Parses the TEMPLATE.md file and returns its parts. A part can be either
    a string or a tuple with two elements:
    - function name
    - list of arguments

    :param text: the content of the TEMPLATE.md file
    :returns: the parts of the TEMPLATE.md file as a dictionary
    '''
    lines: list[str] = text.split('\n')
    result: list[str | tuple[str, list]] = []
    for i, line in enumerate(lines):
        if line.startswith(":generate:"):
            line = line[10:].strip()
            func_parts = _split_func_parts(line)
            if func_parts is None:
                print_error(
                    f"Invalid function format in TEMPLATE.md file.\n"
                    f"\tLine: {i + 1}\n"
                    f"\tFunction: {line}"
                )
                result.append(line)
            elif func_parts[0] not in FUNCTION_MAP:
                print_error(
                    f"Unknown function in TEMPLATE.md file.\n"
                    f"\tLine: {i + 1}\n"
                    f"\tFunction: {line}"
                )
                result.append(line)
            else:
                result.append(func_parts)
        else:
            result.append(line)
    return result


def insert(path: str):
    '''
    Returns the text from a file from content_guide_generator.
    
    It's used to insert text from a file in content_guide_generator data into
    TEMPLATE.md
    '''
    file_path = DATA_PATH / path
    return file_path.read_text()


# PARSING THE TEMPLATE
FUNCTION_MAP: dict[str, Callable] = {
    'completion_guide': completion_guide,
    'warp': warp,
    'insert': insert,
    'list_entities': list_entities,
    'summarize_entities': summarize_entities,
    'summarize_entities_in_tables': summarize_entities_in_tables,
    'sound_definitions': sound_definitions,
    'summarize_items': summarize_items,
    'summarize_items_in_tables': summarize_items_in_tables,
    'list_items': list_items,
}


def build_from_template() -> str:
    result: list[str] = []
    template_path = DATA_PATH / 'TEMPLATE.md'
    for template_part in _parse_template(template_path.read_text()):
        if isinstance(template_part, str):
            result.append(template_part)
        else:  # tuple[str, list]
            func_name, args = template_part
            result.append(FUNCTION_MAP[func_name](*args))
    return '\n'.join(result)


def main_regolith():
    result = build_from_template()
    output_path = DATA_PATH / "OUTPUT.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result, encoding='utf8')

def main_commandline():
    print("Hello world!")