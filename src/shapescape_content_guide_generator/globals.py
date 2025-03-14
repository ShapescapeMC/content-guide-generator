'''
Global variables shared across the generator
'''
from __future__ import annotations
from functools import cache
from pathlib import Path
from dataclasses import dataclass

from sqlite_bedrock_packs import Database

@dataclass
class AppConfig:
    '''
    AppConfig is a singleton with configuration of the app. It lets avoid
    using global variables which I consider less readable and harder to
    debug
    '''
    bp_path: Path
    rp_path: Path
    data_path: Path

    @cache
    @staticmethod
    def get() -> AppConfig:
        bp_path = Path("BP")
        rp_path = Path("RP")
        data_path = Path("data/shapescape_content_guide_generator")
        return AppConfig(bp_path, rp_path, data_path)
@cache
def get_db():
    '''
    Returns the database with info about the packs.
    '''
    db = Database.create()
    db.load_rp(AppConfig.get().rp_path, include=['sound_definitions'])
    db.load_bp(
        AppConfig.get().bp_path,
        include=[
            'entities', 'bp_items', 'loot_tables', 'trade_tables',
            'feature_rules', 'features']
    )
    return db