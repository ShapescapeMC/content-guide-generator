'''
This module contains logic used for gathering and presenting the information
about items.
'''
from __future__ import annotations

from typing import NamedTuple, Literal
from pathlib import Path
from functools import cache
from json import JSONDecodeError
import json

from sqlite_bedrock_packs.better_json_tools import load_jsonc, SKIP_LIST

# Local imports
from .utils import filter_paths
from .errors import print_error
from .globals import BP_PATH


PlayerFacingSelector = Literal['player_facing', 'non_player_facing', 'all']
'''
In the functions that filter items by player facing property it's used to select
player-facing only items, non-player-facing only items or all items.
'''

class ItemProperties(NamedTuple):
    identifier: str
    description: str
    player_facing: bool

    @cache
    @staticmethod
    def from_path(
            path: Path, clear_cgg_properties: bool = True) -> ItemProperties | None:
        '''
        Loads the item properties from the item file. The properties are
        later reused by various functions to generate the content guide. If
        file fails to load or is missing some important data, it returns None.

        :param path: The path to the item file.
        :param clear_cgg_properties: If True, the function will clear the
            custom properties used by the content guide generator after reading
            them.
        '''
        # Load file
        try:
            data = load_jsonc(path)
        except JSONDecodeError:
            print_error(
                f"Unable to load item file as JSON\n"
                f"\tPath: {path.as_posix()}")
            return None

        file_modified  = False  # tracks if it has custom json to delete

        # List of errors to print at the end of the function
        errors: list[str] = []

        root_walker = data / 'minecraft:item' / 'description'
        # Identifier
        identifier = (root_walker / 'identifier').data
        if not isinstance(identifier, str):
            errors.append("Missing item identifier")
            return None

        # Description
        description_walker = root_walker / 'description'
        description: str = ""
        if not description_walker.exists:
            errors.append("Missing item description")
        else:
            description_data: list[str] = []
            for d in description_walker // SKIP_LIST:
                if not isinstance(d.data, str):
                    errors.append(
                        "Invalid item description (should be string or "
                        "list of strings)")
                    break
                description_data.append(d.data)
            description = '\n'.join(description_data)
            if clear_cgg_properties:
                file_modified = True
                del description_walker.parent.data['description']
        # Player facing
        player_facing_walker = root_walker / 'player_facing'
        player_facing: bool = True
        if not player_facing_walker.exists:
            errors.append(
                "Missing player_facing property "
                "(assigned True by default)")
        else:
            if not isinstance(player_facing_walker.data, bool):
                errors.append(
                    "Invalid player_facing property "
                    "(assigned True by default)")
            else:
                player_facing = player_facing_walker.data
            if clear_cgg_properties:
                file_modified = True
                del root_walker.data['player_facing']
        # Save file with removed custom properties
        if file_modified:
            with open(path, 'w') as f:
                json.dump(data.data, f, indent='\t')
        # Print errors
        if len(errors) > 0:
            print_error(
                f"File {path.as_posix()} is missing properties "
                "to generate summary of the ITEM:\n\t- " +
                "\n\t- ".join(errors)
            )
        return ItemProperties(identifier, description, player_facing)

    def item_summary(self):
        '''
        Returns the summary of the item.
        '''
        result: list[str] = [f"### {self.identifier}"]
        if self.description != "":
            result.append(f"{self.description}")
        return '\n'.join(result) + "\n"

    def item_table_summary(self):
        '''
        Returns the summary of the item in a table format (excluding the
        header).
        '''
        description = self.description.replace("\n", "<br>")
        return f"| {self.identifier} | {description} |"

def summarize_items(
        search_patterns: str | list[str],
        exclude_patterns: str | list[str] | None = None,
        player_facing: PlayerFacingSelector = 'all',
) -> str:
    '''
    Returns the summaries of all items from paths that match the search
    pattern.

    :param search_pattern: glob pattern used to find the item files. The
        pattern must be relative to behavior pack items folder.
    :param exclude_patterns: the pattern that excludes the files even if they
        matched the search pattern.
    '''
    item_paths = BP_PATH / 'items'
    filtered_paths = filter_paths(
        item_paths, search_patterns, exclude_patterns)

    result: list[str] = []
    for item_path in filtered_paths:
        item = ItemProperties.from_path(item_path)
        if item is None:
            continue
        if player_facing == 'player_facing' and not item.player_facing:
            continue
        elif player_facing == 'non_player_facing' and item.player_facing:
            continue
        result.append(item.item_summary())
    return '\n'.join(result)

def summarize_items_in_tables(
        search_patterns: str | list[str],
        exclude_patterns: str | list[str] | None = None,
        player_facing: PlayerFacingSelector = 'all',
) -> str:
    '''
    Returns the summaries of all items from paths that match the search
    pattern.

    :param search_pattern: glob pattern used to find the item files. The
        pattern must be relative to behavior pack items folder.
    :param exclude_patterns: the pattern that excludes the files even if they
        matched the search pattern.
    '''
    item_paths = BP_PATH / 'items'
    filtered_paths = filter_paths(
        item_paths, search_patterns, exclude_patterns)
    result: list[str] = [
        "| Item | Description |",
        "|------|-------------|"
    ]
    for item_path in filtered_paths:
        if not item_path.is_file():
            continue
        item = ItemProperties.from_path(item_path)
        if item is None:
            continue
        if player_facing == 'player_facing' and not item.player_facing:
            continue
        elif player_facing == 'non_player_facing' and item.player_facing:
            continue
        result.append(item.item_table_summary())
    return '\n'.join(result)

def list_items(
        search_patterns: str | list[str],
        exclude_patterns: str | list[str] | None = None,
        player_facing: PlayerFacingSelector = 'all',
) -> str:
    '''
    Simplified version of list_item_summaries that returns only the list of
    item identifiers.

    :param search_pattern: glob pattern used to find the item files. The
        pattern must be relative to behavior pack items folder.
    :param categories: optional parameter that specifies the categories of the
        items that should be included in the result. If not specified, all
        items are included.
    '''
    items_path = BP_PATH / 'items'
    filtered_paths = filter_paths(
        items_path, search_patterns, exclude_patterns)


    items_path = BP_PATH / 'items'
    result: list[str] = []
    for item_path in filtered_paths:
        if not item_path.is_file():
            continue
        if player_facing == 'player_facing' and not item.player_facing:
            continue
        elif player_facing == 'non_player_facing' and item.player_facing:
            continue
        item = ItemProperties.from_path(item_path)
        result.append(f'- {item.identifier}')
    return '\n'.join(result)
