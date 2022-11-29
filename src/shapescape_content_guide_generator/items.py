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
from sqlite_bedrock_packs.wrappers import Entity

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
player-facing only items, non-player-facing only items or all items.
'''

class ItemProperties(NamedTuple):
    identifier: str
    description: str
    player_facing: bool
    recipe_patterns: list[str]
    dropping_entities: list[str]  # Entities that drop this item
    trading_entities: list[str]  # Entities that drop this item

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

        # Optional list with the patterns of the recipes
        recipe_patterns: list[str] = []

        root_walker = data / 'minecraft:item' / 'description'
        # Identifier
        identifier = (root_walker / 'identifier').data
        if not isinstance(identifier, str):
            errors.append("Missing item identifier")
            return None
        # Dropping and trading entities
        dropping_entities = list_dropping_entities(identifier)
        trading_entities = list_trading_entities(identifier)

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
        player_facing: bool = False
        if not player_facing_walker.exists:
            craftable_items = _list_craftable_items()
            if identifier in craftable_items:
                recipe_patterns.append("\n\n".join(craftable_items[identifier]))
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
                    "(assigned False by default)")
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
        return ItemProperties(
            identifier, description, player_facing, recipe_patterns,
            dropping_entities=dropping_entities,
            trading_entities=trading_entities)

    @cache
    @staticmethod
    def from_entity_path(path: Path, clear_cgg_properties: bool = True) -> ItemProperties | None:
        '''
        Loads the item (spawn egg) properties from an entity file. The properties are
        later reused by various functions to generate the content guide. If
        file fails to load or is missing some important data, it returns None.

        :param path: The path to the entity file.
        :param clear_cgg_properties: If True, the function will clear the
            custom properties used by the content guide generator after reading
            them.
        '''
        # Load file
        try:
            data = load_jsonc(path)
        except JSONDecodeError:
            print_error(
                f"Unable to load entity file as JSON\n"
                f"\tPath: {path.as_posix()}")
            return None

        file_modified  = False  # tracks if it has custom json to delete
        has_spawn_egg = False  # whether the entity has a spawn egg

        # List of errors to print at the end of the function
        errors: list[str] = []

        # Optional list with the patterns of the recipes
        recipe_patterns: list[str] = []

        root_walker = data / 'minecraft:entity' / 'description'
        # Check if the spawn egg even exists
        spawn_egg_walker = root_walker / 'is_spawnable'
        
        if isinstance(spawn_egg_walker.data, bool):
            has_spawn_egg = spawn_egg_walker.data
        elif spawn_egg_walker.exists:
            # By default it's false, if it exists and is not bool, it's invalid
            errors.append("Invalid spawnable property (should be a bool)")
        # If not spawnable, return None
        if not has_spawn_egg:
            # Clear custom properties if there are any
            if clear_cgg_properties:
                if (root_walker / "spawn_egg_description").exists:
                    del root_walker.data["spawn_egg_description"]
                    file_modified = True
                if (root_walker / "spawn_egg_player_facing").exists:
                    del root_walker.data["spawn_egg_player_facing"]
                    file_modified = True
            # Save file with removed custom properties
            if file_modified:
                with open(path, 'w') as f:
                    json.dump(data.data, f, indent='\t')
            # Print errors
            if len(errors) > 0:
                print_error(
                    f"File {path.as_posix()} is missing properties "
                    "to generate summary of the SPAWN EGG:\n\t- " +
                    "\n\t- ".join(errors)
                )
            return None
        # Identifier
        identifier = (root_walker / 'identifier').data
        if not isinstance(identifier, str):
            errors.append("Missing entity identifier")
            return None
        identifier = f"{identifier}_spawn_egg"
        if identifier.startswith("minecraft:"):
            return None  # Silently ignore vanilla spawn eggs

        # Dropping and trading entities
        dropping_entities = list_dropping_entities(identifier)
        trading_entities = list_trading_entities(identifier)

        # Description
        description_walker = root_walker / 'spawn_egg_description'
        description: str = ""
        if not description_walker.exists:
            errors.append("Missing spawn egg description.")
        else:
            description_data: list[str] = []
            for d in description_walker // SKIP_LIST:
                if not isinstance(d.data, str):
                    errors.append(
                        "Invalid spawn egg description (should be string or "
                        "list of strings)")
                    break
                description_data.append(d.data)
            description = '\n'.join(description_data)
            if clear_cgg_properties:
                file_modified = True
                del description_walker.parent.data['spawn_egg_description']
        # Player facing
        player_facing_walker = root_walker / 'spawn_egg_player_facing'
        player_facing: bool = False
        if not player_facing_walker.exists:
            craftable_items = _list_craftable_items()
            if identifier in craftable_items:
                recipe_patterns.append(
                    "\n\n".join(craftable_items[identifier]))
                player_facing = True
            elif len(dropping_entities) > 0 or len(trading_entities) > 0:
                player_facing = True
            else:
                errors.append(
                    "Unable to determine player_facing property of the spawn "
                    "egg (assigned False by default)")
        else:
            if not isinstance(player_facing_walker.data, bool):
                errors.append(
                    "Invalid player_facing property of the spawn egg "
                    "(assigned False by default)")
            else:
                player_facing = player_facing_walker.data
            if clear_cgg_properties:
                file_modified = True
                del root_walker.data['spawn_egg_player_facing']
        # Save file with removed custom properties
        if file_modified:
            with open(path, 'w') as f:
                json.dump(data.data, f, indent='\t')
        # Print errors
        if len(errors) > 0:
            print_error(
                f"File {path.as_posix()} is missing properties "
                "to generate summary of the SPAWN EGG:\n\t- " +
                "\n\t- ".join(errors)
            )
        return ItemProperties(
            identifier, description, player_facing, recipe_patterns,
            dropping_entities=dropping_entities,
            trading_entities=trading_entities)

    @cache
    @staticmethod
    def from_block_path(path: Path, clear_cgg_properties: bool = True) -> ItemProperties | None:
        '''
        Loads the item properties from the block file. The properties are
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

        file_modified = False  # tracks if it has custom json to delete

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
            errors.append("Missing item description")
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
            craftable_items = _list_craftable_items()
            if identifier in craftable_items:
                recipe_patterns.append(
                    "\n\n".join(craftable_items[identifier]))
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
                    "(assigned False by default)")
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
        return ItemProperties(
            identifier, description, player_facing, recipe_patterns,
            dropping_entities=dropping_entities,
            trading_entities=trading_entities)

    def item_summary(self):
        '''
        Returns the summary of the item.
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
    item_paths = AppConfig.get().bp_path / 'items'
    filtered_paths = filter_paths(
        item_paths, search_patterns, exclude_patterns)

    result: list[str] = []
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
    item_paths = AppConfig.get().bp_path / 'items'
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
    '''
    items_path = AppConfig.get().bp_path / 'items'
    filtered_paths = filter_paths(
        items_path, search_patterns, exclude_patterns)


    result: list[str] = []
    for item_path in filtered_paths:
        if not item_path.is_file():
            continue
        item = ItemProperties.from_path(item_path)
        if player_facing == 'player_facing' and not item.player_facing:
            continue
        elif player_facing == 'non_player_facing' and item.player_facing:
            continue
        result.append(f'- {item.identifier}')
    return '\n'.join(result)

def summarize_blocks(
        search_patterns: str | list[str],
        exclude_patterns: str | list[str] | None = None,
        player_facing: PlayerFacingSelector = 'all',
) -> str:
    '''
    Returns the summaries of all blocks from paths that match the search
    pattern.

    :param search_pattern: glob pattern used to find the block files. The
        pattern must be relative to behavior pack blocks folder.
    :param exclude_patterns: the pattern that excludes the files even if they
        matched the search pattern.
    '''
    block_paths = AppConfig.get().bp_path / 'blocks'
    filtered_paths = filter_paths(
        block_paths, search_patterns, exclude_patterns)

    result: list[str] = []
    for block_path in filtered_paths:
        if not block_path.is_file():
            continue
        block = ItemProperties.from_block_path(block_path)
        if block is None:
            continue
        if player_facing == 'player_facing' and not block.player_facing:
            continue
        elif player_facing == 'non_player_facing' and block.player_facing:
            continue
        result.append(block.item_summary())
    return '\n'.join(result)

def summarize_blocks_in_tables(
        search_patterns: str | list[str],
        exclude_patterns: str | list[str] | None = None,
        player_facing: PlayerFacingSelector = 'all',
) -> str:
    '''
    Returns the summaries of all blocks from paths that match the search
    pattern.

    :param search_pattern: glob pattern used to find the block files. The
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
        block = ItemProperties.from_block_path(block_path)
        if block is None:
            continue
        if player_facing == 'player_facing' and not block.player_facing:
            continue
        elif player_facing == 'non_player_facing' and block.player_facing:
            continue
        result.append(block.item_table_summary())
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
    '''
    blocks_path = AppConfig.get().bp_path / 'blocks'
    filtered_paths = filter_paths(
        blocks_path, search_patterns, exclude_patterns)

    result: list[str] = []
    for block_path in filtered_paths:
        if not block_path.is_file():
            continue
        block = ItemProperties.from_block_path(block_path)
        if player_facing == 'player_facing' and not block.player_facing:
            continue
        elif player_facing == 'non_player_facing' and block.player_facing:
            continue
        result.append(f'- {block.identifier}')
    return '\n'.join(result)

def summarize_spawn_eggs(
        search_patterns: str | list[str],
        exclude_patterns: str | list[str] | None = None,
        player_facing: PlayerFacingSelector = 'all',
) -> str:
    '''
    Returns the summaries of all spawn_eggs from paths that match the search
    pattern.

    :param search_pattern: glob pattern used to find the entity files. The
        pattern must be relative to behavior pack entities folder.
    :param exclude_patterns: the pattern that excludes the files even if they
        matched the search pattern.
    '''
    item_paths = AppConfig.get().bp_path / 'entities'
    filtered_paths = filter_paths(
        item_paths, search_patterns, exclude_patterns)

    result: list[str] = []
    for item_path in filtered_paths:
        if not item_path.is_file():
            continue
        item = ItemProperties.from_entity_path(item_path)
        if item is None:
            continue
        if player_facing == 'player_facing' and not item.player_facing:
            continue
        elif player_facing == 'non_player_facing' and item.player_facing:
            continue
        result.append(item.item_summary())
    return '\n'.join(result)

def summarize_spawn_eggs_in_tables(
        search_patterns: str | list[str],
        exclude_patterns: str | list[str] | None = None,
        player_facing: PlayerFacingSelector = 'all',
) -> str:
    '''
    Returns the summaries of all spawn_eggs from paths that match the search
    pattern.

    :param search_pattern: glob pattern used to find the entity files. The
        pattern must be relative to behavior pack entities folder.
    :param exclude_patterns: the pattern that excludes the files even if they
        matched the search pattern.
    '''
    item_paths = AppConfig.get().bp_path / 'items'
    filtered_paths = filter_paths(
        item_paths, search_patterns, exclude_patterns)
    result: list[str] = [
        "| Item | Description |",
        "|------|-------------|"
    ]
    for item_path in filtered_paths:
        if not item_path.is_file():
            continue
        item = ItemProperties.from_entity_path(item_path)
        if item is None:
            continue
        if player_facing == 'player_facing' and not item.player_facing:
            continue
        elif player_facing == 'non_player_facing' and item.player_facing:
            continue
        result.append(item.item_table_summary())
    return '\n'.join(result)

def list_spawn_eggs(
        search_patterns: str | list[str],
        exclude_patterns: str | list[str] | None = None,
        player_facing: PlayerFacingSelector = 'all',
) -> str:
    '''
    Simplified version of summarize_spawn_eggs that returns only the list of
    item identifiers.

    :param search_pattern: glob pattern used to find the entity files. The
        pattern must be relative to behavior pack entities folder.
    :param exclude_patterns: the pattern that excludes the files even if they
        matched the search pattern.
    '''
    items_path = AppConfig.get().bp_path / 'entities'
    filtered_paths = filter_paths(
        items_path, search_patterns, exclude_patterns)

    result: list[str] = []
    for item_path in filtered_paths:
        if not item_path.is_file():
            continue
        item = ItemProperties.from_entity_path(item_path)
        if player_facing == 'player_facing' and not item.player_facing:
            continue
        elif player_facing == 'non_player_facing' and item.player_facing:
            continue
        result.append(f'- {item.identifier}')
    return '\n'.join(result)

@cache
def _list_craftable_items() -> dict[str, list[str]]:
    '''
    Lists all of the items that can be crafted and their recipes in as string
    form using the "recipes.py" script which is a part of the
    Recipe Image Generator
    '''
    recipes_path = AppConfig.get().bp_path / 'recipes'
    result: dict[str, list[str]] = defaultdict(list)
    for recipe_path in recipes_path.rglob("*.json"):
        the_chosen_one = False
        if recipe_path.as_posix() == 'behavior_packs/0/recipes/cb/quartz_bricks_bannister_stair_north.recipe.json':
            the_chosen_one = True
        try:
            recipe = load_recipe(recipe_path)
        except InvalidRecipeException as e:
            print_error(
                f"Failed to load recipe form: "
                f"{recipe_path.as_posix()}")
            if the_chosen_one:
                raise Exception(
                    f"Failed to load recipe form: "
                    f"{recipe_path.as_posix()}"
                    f"{e}"
                )
            continue
        if isinstance(recipe, RecipeCrafting):
            recipe_text = (
                f"#### **Crafting recipe:**\n"
                "**Ingredients:**\n")
            for k, v in recipe.keys.items():
                recipe_text += f"- {v.item} as {k}\n"
            recipe_text += "\n**Pattern:**\n```\n"
            recipe_text += "\n".join(recipe.pattern) + "\n```\n"
            result[recipe.result.get_true_item_name()].append(recipe_text)
        if isinstance(recipe, RecipeFurnace):
            recipe_text = (
                "#### **Furnace recipe:**\n"
                f"- Input: {recipe.input.item}\n"
                f"- Output: {recipe.output.item}\n"
            )
            result[recipe.output.get_true_item_name()].append(recipe_text)
        if isinstance(recipe, RecipeBrewing):
            recipe_text = (
                "#### **Brewing recipe:**\n"
                f"- Input: {recipe.input.item}\n"
                f"- Reagent: {recipe.reagent.item}\n"
                f"- Output: {recipe.output.item}\n"
            )
            result[recipe.output.get_true_item_name()].append(recipe_text)
    return dict(result)

def list_dropping_entities(item_name: str) -> list[str]:
    '''
    Lists the identifiers of the entities that drop the specified item.
    '''
    db = get_db()
    result: list[str] = []
    if item_name.endswith("_spawn_egg"):
        q = EasyQuery.build(
            db, "LootTable", "LootTableItemSpawnEggReferenceField",
            "Entity",
            where=(
                "LootTableItemSpawnEggReferenceField.spawnEggIdentifier = "
                f"'{item_name}'")
        )
        for _, _, entity in q.yield_wrappers():
            entity = cast(Entity, entity)
            if entity.identifier is None:
                continue
            result.append(entity.identifier)
    else:
        q = EasyQuery.build(
            db, 'BpItem', 'LootTable', 'Entity', 
            where=[f"BpItem.identifier = '{item_name}'"])
        for _, _, entity in q.yield_wrappers():
            entity = cast(Entity, entity)
            if entity.identifier is None:
                continue
            result.append(entity.identifier)
    return result

def list_trading_entities(item_name: str) -> list[str]:
    '''
    Lists the identifiers of the entities that trade the specified item.
    '''
    db = get_db()
    result: list[str] = []
    if item_name.endswith("_spawn_egg"):
        q = EasyQuery.build(
            db, "TradeTable", "TradeTableItemSpawnEggReferenceField",
            "Entity",
            where=(
                "TradeTableItemSpawnEggReferenceField.spawnEggIdentifier = "
                f"'{item_name}'")
        )
        for _, _, entity in q.yield_wrappers():
            entity = cast(Entity, entity)
            if entity.identifier is None:
                continue
            result.append(entity.identifier)
    else:
        q = EasyQuery.build(
            db, 'BpItem', 'TradeTable', 'Entity',
            where=[f"BpItem.identifier = '{item_name}'"])
        for _, _, entity in q.yield_wrappers():
            entity = cast(Entity, entity)
            if entity.identifier is None:
                continue
            result.append(entity.identifier)
    return result