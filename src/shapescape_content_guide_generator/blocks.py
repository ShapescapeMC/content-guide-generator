'''
This module contains logic used for gathering and presenting the information
about items.
'''
from __future__ import annotations
from collections import defaultdict

from typing import NamedTuple, Literal, cast
from pathlib import Path
from functools import cache
from json import JSONDecodeError
import json

from sqlite_bedrock_packs.better_json_tools import load_jsonc, SKIP_LIST
from sqlite_bedrock_packs import EasyQuery
from sqlite_bedrock_packs.wrappers import BpItem, Entity, TradeTable

# Local imports
from .utils import filter_paths
from .errors import print_error
from .globals import AppConfig, get_db
from .recipes import (
    load_recipe, InvalidRecipeException, RecipeCrafting, RecipeFurnace,
    RecipeBrewing)

PlayerFacingSelector = Literal['player_facing', 'non_player_facing', 'all']
'''
In the functions that filter items by player facing property it's used to select
player-facing only items, non-player-facing only blocks or all items.
'''

class BlocksProperties(NamedTuple):
    identifier: str
    description: str
    player_facing: bool
    recipe_patterns: list[str]
    dropping_entities: list[str]  # Entities that drop this item
    trading_entities: list[str]  # Entities that drop this item

    @cache
    @staticmethod
    def from_path(
            path: Path, clear_cgg_properties: bool = True) -> BlocksProperties | None:
        '''
        Loads the item properties from the block file. The properties are
        later reused by various functions to generate the content guide. If
        file fails to load or is missing some important data, it returns None.

        :param path: The path to the block file.
        :param clear_cgg_properties: If True, the function will clear the
            custom properties used by the content guide generator after reading
            them.
        '''
        # Load file
        try:
            data = load_jsonc(path)
        except JSONDecodeError:
            print_error(
                f"Unable to load block file as JSON\n"
                f"\tPath: {path.as_posix()}")
            return None

        file_modified  = False  # tracks if it has custom json to delete

        # List of errors to print at the end of the function
        errors: list[str] = []

        # Optional list with the patterns of the recipes
        recipe_patterns: list[str] = []

        root_walker = data / 'minecraft:block' / 'description'
        # Identifier
        identifier = (root_walker / 'identifier').data
        if not isinstance(identifier, str):
            errors.append("Missing block identifier")
            return None
        # Dropping and trading entities
        dropping_entities = list_dropping_entities(identifier)
        trading_entities = list_trading_entities(identifier)

        # Description
        description_walker = root_walker / 'description'
        description: str = ""
        if not description_walker.exists:
            errors.append("Missing block description")
        else:
            description_data: list[str] = []
            for d in description_walker // SKIP_LIST:
                if not isinstance(d.data, str):
                    errors.append(
                        "Invalid block description (should be string or "
                        "list of strings)")
                    break
                description_data.append(d.data)
            description = '\n'.join(description_data)
            if clear_cgg_properties:
                file_modified = True
                del description_walker.parent.data['description']
        # Player facing
        player_facing_walker = root_walker / 'player_facing'
        player_facing: bool = False
        if not player_facing_walker.exists:
            craftable_blocks = _list_craftable_blocks()
            if identifier in craftable_blocks:
                recipe_patterns.append("\n\n".join(craftable_blocks[identifier]))
                player_facing = True
            elif len(dropping_entities) > 0 or len(trading_entities) > 0:
                player_facing = True
            else:
                errors.append(
                    "Unable to determine player_facing property "
                    "(assigned False by default)")
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
                "to generate summary of the BLOCK:\n\t- " +
                "\n\t- ".join(errors)
            )
        return BlocksProperties(
            identifier, description, player_facing, recipe_patterns,
            dropping_entities=dropping_entities,
            trading_entities=trading_entities)

    def block_summary(self):
        '''
        Returns the summary of the block.
        '''
        result: list[str] = [f"### {self.identifier}"]
        if self.description != "":
            result.append(f"{self.description}")

        if len(self.recipe_patterns) > 0:
            result.extend(self.recipe_patterns)
        if len(self.dropping_entities) > 0:
            result.append("#### **Dropped by:**")
            result.extend([f'- {e}' for e in self.dropping_entities])
        if len(self.trading_entities) > 0:
            result.append("#### **Traded by:**")
            result.extend([f'- {e}' for e in self.trading_entities])
        return '\n'.join(result) + "\n"

    def block_table_summary(self):
        '''
        Returns the summary of the block in a table format (excluding the
        header).
        '''
        description = self.description.replace("\n", "<br>")
        return f"| {self.identifier} | {description} |"

def summarize_blocks(
        search_patterns: str | list[str],
        exclude_patterns: str | list[str] | None = None,
        player_facing: PlayerFacingSelector = 'all',
) -> str:
    '''
    Returns the summaries of all blocks from paths that match the search
    pattern.

    :param search_pattern: glob pattern used to find the block files. The
        pattern must be relative to behavior pack items folder.
    :param exclude_patterns: the pattern that excludes the files even if they
        matched the search pattern.
    '''
    item_paths = AppConfig.get().bp_path / 'blocks'
    filtered_paths = filter_paths(
        item_paths, search_patterns, exclude_patterns)

    result: list[str] = []
    for block_path in filtered_paths:
        if not block_path.is_file():
            continue
        item = BlocksProperties.from_path(block_path)
        if item is None:
            continue
        if player_facing == 'player_facing' and not item.player_facing:
            continue
        elif player_facing == 'non_player_facing' and item.player_facing:
            continue
        result.append(item.block_summary())
    return '\n'.join(result)

def summarize_blocks_in_tables(
        search_patterns: str | list[str],
        exclude_patterns: str | list[str] | None = None,
        player_facing: PlayerFacingSelector = 'all',
) -> str:
    '''
    Returns the summaries of all blocks from paths that match the search
    pattern.

    :param search_pattern: glob pattern used to find the blocks files. The
        pattern must be relative to behavior pack blocks folder.
    :param exclude_patterns: the pattern that excludes the files even if they
        matched the search pattern.
    '''
    block_paths = AppConfig.get().bp_path / 'blocks'
    filtered_paths = filter_paths(
        block_paths, search_patterns, exclude_patterns)
    result: list[str] = [
        "| Block | Description |",
        "|------|-------------|"
    ]
    for block_path in filtered_paths:
        if not block_path.is_file():
            continue
        item = BlocksProperties.from_path(block_path)
        if item is None:
            continue
        if player_facing == 'player_facing' and not item.player_facing:
            continue
        elif player_facing == 'non_player_facing' and item.player_facing:
            continue
        result.append(item.block_table_summary())
    return '\n'.join(result)

def list_blocks(
        search_patterns: str | list[str],
        exclude_patterns: str | list[str] | None = None,
        player_facing: PlayerFacingSelector = 'all',
) -> str:
    '''
    Simplified version of list_block_summaries that returns only the list of
    block identifiers.

    :param search_pattern: glob pattern used to find the block files. The
        pattern must be relative to behavior pack blocks folder.
    :param categories: optional parameter that specifies the categories of the
        blocks that should be included in the result. If not specified, all
        blocks are included.
    '''
    blocks_path = AppConfig.get().bp_path / 'blocks'
    filtered_paths = filter_paths(
        blocks_path, search_patterns, exclude_patterns)


    blocks_path = AppConfig.get().bp_path / 'blocks'
    result: list[str] = []
    for block_path in filtered_paths:
        if not block_path.is_file():
            continue
        block = BlocksProperties.from_path(block_path)
        if player_facing == 'player_facing' and not block.player_facing:
            continue
        elif player_facing == 'non_player_facing' and block.player_facing:
            continue
        result.append(f'- {block.identifier}')
    return '\n'.join(result)

@cache
def _list_craftable_blocks() -> dict[str, list[str]]:
    '''
    Lists all of the blocks that can be crafted and their recipes in as string
    form using the "recipes.py" script which is a part of the
    Recipe Image Generator
    '''
    recipes_path = AppConfig.get().bp_path / 'recipes'
    result: dict[str, list[str]] = defaultdict(list)
    for recipe_path in recipes_path.rglob("*.json"):
        try:
            recipe = load_recipe(recipe_path)
        except InvalidRecipeException:
            print_error(
                f"Failed to load recipe form: "
                f"{recipe_path.as_posix()}")
            continue
        if isinstance(recipe, RecipeCrafting):
            recipe_text = (
                f"#### **Crafting recipe:**\n"
                "**Ingredients:**\n")
            for k, v in recipe.keys.items():
                recipe_text += f"- {v.item} as {k}\n"
            recipe_text += "\n**Pattern:**\n```\n"
            recipe_text += "\n".join(recipe.pattern) + "\n```\n"
            result[recipe.result.item].append(recipe_text)
        if isinstance(recipe, RecipeFurnace):
            recipe_text = (
                "#### **Furnace recipe:**\n"
                f"- Input: {recipe.input.item}\n"
                f"- Output: {recipe.output.item}\n"
            )
            result[recipe.output.item].append(recipe_text)
        if isinstance(recipe, RecipeBrewing):
            recipe_text = (
                "#### **Brewing recipe:**\n"
                f"- Input: {recipe.input.item}\n"
                f"- Reagent: {recipe.reagent.item}\n"
                f"- Output: {recipe.output.item}\n"
            )
            result[recipe.output.item].append(recipe_text)
    return dict(result)

def list_dropping_entities(block_name: str) -> list[str]:
    '''
    Lists the identifiers of the entities that drop the specified item.
    '''
    
    db = get_db()
    result: list[str] = []
    q = EasyQuery.build(
        db, 'BpItem', 'LootTable', 'Entity', 
        where=[f"BpItem.identifier = '{block_name}'"])
    for _, _, entity in q.yield_wrappers():
        entity = cast(Entity, entity)
        if entity.identifier is None:
            continue
        result.append(entity.identifier)
    return result

def list_trading_entities(block_name: str) -> list[str]:
    '''
    Lists the identifiers of the entities that trade the specified item.
    '''
    db = get_db()
    result: list[str] = []
    q = EasyQuery.build(
        db, 'BpItem', 'TradeTable', 'Entity',
        where=[f"BpItem.identifier = '{block_name}'"])
    for _, _, entity in q.yield_wrappers():
        entity = cast(Entity, entity)
        if entity.identifier is None:
            continue
        result.append(entity.identifier)
    return result