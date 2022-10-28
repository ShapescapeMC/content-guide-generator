'''
This module contains logic used for gathering and presenting the information
about entities.
'''
from __future__ import annotations

from typing import Literal, NamedTuple
from pathlib import Path
from functools import cache
from json import JSONDecodeError
import json

from sqlite_bedrock_packs.better_json_tools import load_jsonc, SKIP_LIST

# Local imports
from .utils import filter_paths
from .errors import print_error
from .globals import BP_PATH

EntityCategory = Literal[
    "character", "trader", "non_player_facing_utility", "player_facing_utility",
    "projectile", "creature", "decoration", "interactive_entity"]

ENTITY_CATEGORIES = (
    "character", "trader", "non_player_facing_utility", "player_facing_utility",
    "projectile", "creature", "decoration", "interactive_entity")
'''
Notes on the decision of using these categories:
- character & trader are a thing required by content guide template
- "non_player_facing_utility" was originally called "utility" but during the
  generation of the content guide, it was hard to decide whether some uitilities
  should be included in the mandatory section "Player facing entities" or in
  "Non-player facing entities". The categories are used to decide what goes
  where, so It was either putting all utilities in the "Player facing entities"
  or to "Non-player facing entities". Then the "decoration" and
  "interactive_entity" categories were added but some of the entities aren't
  any of them. Examples:
  - enemy_spawn - the portal, it's visible, it's a key part of the game because
    it spawns the enemies. It's not just a decoration, it's not interactive
    and it's not non_player_facing
  - poison_aoe - a puddle of poison that damages enemies (same as above)
- "player_facing_utility" was added to cover the problem of the "utility"
  described above.
- "projectile" - it's a projectile
- "creature" - any living creature which is not a character or a trader
- "decoration" - purely decorative entiteis
- "interactive_entity" - entities that can be interacted with like shops, menus
   etc. The non-interactive parts of the shops should also be added to this
   category (as a part of a bigger thing).
'''


class EntityProperties(NamedTuple):
    identifier: str
    description: str
    locations: list[str]
    category: EntityCategory
    locations: list[tuple[float, float, float]]


    @cache
    @staticmethod
    def from_path(
            path: Path, clear_cgg_properties: bool = True) -> EntityProperties | None:
        '''
        Loads the entity properties from the entity file. The properties are
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

        # List of errors to print at the end of the function
        errors: list[str] = []

        root_walker = data / 'minecraft:entity' / 'description'
        # Identifier
        identifier = (root_walker / 'identifier').data
        if not isinstance(identifier, str):
            errors.append("Missing entity identifier")
            return None
        if identifier.startswith("minecraft:"):
            return None  # Silently skip vanilla entities

        # Description
        description_walker = root_walker / 'description'
        description: str = ""
        if not description_walker.exists:
            errors.append("Missing entity description")
        else:
            description_data: list[str] = []
            for d in description_walker // SKIP_LIST:
                if not isinstance(d.data, str):
                    errors.append(
                        "Invalid entity description (should be string or "
                        "list of strings)")
                    break
                description_data.append(d.data)
            description = '\n'.join(description_data)
            if clear_cgg_properties:
                file_modified = True
                del description_walker.parent.data['description']
        # Category
        category_walker = root_walker / 'category'
        category: EntityCategory = "non_player_facing_utility"  # Set default category to utility
        if not category_walker.exists:
            errors.append(
                "Missing category property "
                "(assigned 'utility' category by default)")
        else:
            category = category_walker.data
            if category not in ENTITY_CATEGORIES:
                errors.append(
                    f"Invalid entity category: {category}.\n"
                    f"Expected one of: " + ", ".join(ENTITY_CATEGORIES) + "\n"
                    f"(assigned 'utility' category by default)")
                category = "non_player_facing_utility"
            if clear_cgg_properties:
                file_modified = True
                del category_walker.parent.data['category']
        # Locations
        locations: list[tuple[float, float, float]] | None = []
        locations_walker = root_walker / 'locations'
        if locations_walker.exists:
            for location in locations_walker // SKIP_LIST:
                location_format_error = (
                    "Invalid entity location format")
                if not isinstance(location.data, str):
                    errors.append(location_format_error)
                    break
                crds_str = location.data.split(' ')
                if len(crds_str) != 3:
                    errors.append(location_format_error)
                    break
                try:
                    crds = tuple(map(float, crds_str))
                except ValueError:
                    errors.append(location_format_error)
                    break
                locations.append(crds)
            if clear_cgg_properties:
                file_modified = True
                del locations_walker.parent.data['locations']
        else:
            errors.append("Missing locations property")
        if file_modified:
            with open(path, 'w') as f:
                json.dump(data.data, f, indent='\t')
        if len(errors) > 0:
            print_error(
                f"File {path.as_posix()} is missing properties "
                "to generate summary of the ENTITY:\n\t- " +
                "\n\t- ".join(
                    # Multiline errors need indentation
                    [error.replace("\n", "\n\t  ") for error in errors]
                )
            )
        return EntityProperties(identifier, description, locations, category)

    def entity_summary(self):
        '''
        Returns the summary of the entity.
        '''
        result: list[str] = [f"### {self.identifier}"]
        if self.description != "":
            result.append(f"{self.description}")
        if self.locations is not None and len(self.locations) > 0:
            result.append(
                "\n**Locations:** " +
                ", ".join(
                    [
                        f"({location[0]} {location[1]} {location[2]})"
                        for location in self.locations
                    ]
                )
            )
        return '\n'.join(result) + "\n"

    def entity_table_summary(self):
        '''
        Returns the summary of the entity in a table format (excluding the
        header).
        '''
        description = self.description.replace("\n", "<br>")
        if self.locations is not None and len(self.locations) > 0:
            locations = ", ".join(
                [
                    f"({location[0]} {location[1]} {location[2]})"
                    for location in self.locations
                ]
            )
        else:
            locations = "N/A"
        return f"| {self.identifier} | {description} | {locations} |"

def summarize_entities(
        search_patterns: str | list[str],
        exclude_patterns: str | list[str] | None = None,
        categories: EntityCategory | list[EntityCategory] | None = None
) -> str:
    '''
    Returns the summaries of all entities from paths that match the search
    pattern.

    :param search_pattern: glob pattern used to find the entity files. The
        pattern must be relative to behavior pack entities folder.
    :param category: optional parameter that specifies the categories of the
        entities that should be included in the result. If not specified, all
        entities are included.
    '''
    if categories is None:
        categories = ENTITY_CATEGORIES
    elif isinstance(categories, str):
        categories = [categories]
    entities_path = BP_PATH / 'entities'
    filtered_paths = filter_paths(
        entities_path, search_patterns, exclude_patterns)


    result: list[str] = []
    for entity_path in filtered_paths:
        entity = EntityProperties.from_path(entity_path)
        if entity is None:
            continue
        if entity.category not in categories:
            continue
        result.append(entity.entity_summary())
    return '\n'.join(result)

def summarize_entities_in_tables(
        search_patterns: str | list[str],
        exclude_patterns: str | list[str] | None = None,
        categories: EntityCategory | list[EntityCategory] | None = None
) -> str:
    '''
    Returns the summaries of all entities from paths that match the search
    pattern.

    :param search_pattern: glob pattern used to find the entity files. The
        pattern must be relative to behavior pack entities folder.
    :param categories: optional parameter that specifies the categories of the
        entities that should be included in the result. If not specified, all
        entities are included.
    '''
    if categories is None:
        categories = ENTITY_CATEGORIES
    elif isinstance(categories, str):
        categories = [categories]
    entities_path = BP_PATH / 'entities'
    filtered_paths = filter_paths(
        entities_path, search_patterns, exclude_patterns)


    result: list[str] = [
        "| Entity | Description | Locations |",
        "|-------|----------|------|"
    ]
    for entity_path in filtered_paths:
        if not entity_path.is_file():
            continue
        entity = EntityProperties.from_path(entity_path)
        if entity is None:
            continue
        if entity.category not in categories:
            continue
        result.append(entity.entity_table_summary())
    return '\n'.join(result)

def list_entities(
        search_patterns: str | list[str],
        exclude_patterns: str | list[str] | None = None,
        categories: EntityCategory | list[EntityCategory] | None = None
) -> str:
    '''
    Simplified version of list_entity_summaries that returns only the list of
    entity identifiers.

    :param search_pattern: glob pattern used to find the entity files. The
        pattern must be relative to behavior pack entities folder.
    :param categories: optional parameter that specifies the categories of the
        entities that should be included in the result. If not specified, all
        entities are included.
    '''
    if categories is None:
        categories = ENTITY_CATEGORIES
    elif isinstance(categories, str):
        categories = [categories]
    entities_path = BP_PATH / 'entities'
    filtered_paths = filter_paths(
        entities_path, search_patterns, exclude_patterns)


    entities_path = BP_PATH / 'entities'
    result: list[str] = []
    for entity_path in filtered_paths:
        if not entity_path.is_file():
            continue
        entity = EntityProperties.from_path(entity_path)
        if entity is None:
            continue
        if entity.category not in categories:
            continue
        result.append(f'- {entity.identifier}')
    return '\n'.join(result)
