'''
This module defines the error handling.
'''
from dataclasses import dataclass
from functools import cache

def print_error(text):
    '''
    Prints the text to the console in red color. And marks that an error has
    been encounterd during the application execution
    '''
    # Mark that an error has been encountered
    get_error_handler().found_errors = True
    # Print the error
    text = str(text)
    for t in text.split('\n'):
        print("\033[91m {}\033[00m".format(t))

class ContentGuideGenerationError(Exception):
    '''
    Exception used to handle the content guide generator errors.
    '''


@dataclass
class ErrorHandler():
    break_on_warnings: bool = False
    found_errors: bool = False

@cache
def get_error_handler():
    '''ErrorHandler singleton.'''
    return ErrorHandler()
