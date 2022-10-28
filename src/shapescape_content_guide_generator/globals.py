'''
Global variables shared across the generator
'''
from functools import cache
from pathlib import Path

from sqlite_bedrock_packs import Database

BP_PATH = Path("BP")
RP_PATH = Path("RP")
DATA_PATH = Path("data/content_guide_generator")

@cache
def get_db():
    '''
    Returns the database with info about the packs.
    '''
    db = Database.create()
    db.load_rp(RP_PATH, include=['sound_definitions'])
    # db.load_bp(BP_PATH)  # bp is not used
    return db