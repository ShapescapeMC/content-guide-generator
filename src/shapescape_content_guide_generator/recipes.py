'''
This code is copied from the Recipe Image Generator project. It is not the best
solution, but it's implemented already so I'm using it for now.

This code strips important information from the recipe files. It's used for
splitting itmes into player-facing and non-player-facing. An item that is a
result of a recipe is considered player-facing.
'''
from __future__ import annotations
from typing import NamedTuple, Any, Dict, List, Union
from pathlib import Path
import re

from sqlite_bedrock_packs.better_json_tools import load_jsonc, JSONWalker

# Gets the name of an entity for certain molang query
ACTOR_ID_WILDCARD_REGEX = re.compile(
    r"(?:(?:query)|(?:q))\.get_actor_info_id\('([a-zA-Z0-9_]+:[a-zA-Z0-9_]+)'\)")

# A new format of naming spawn eggs without using weird Molang queries
NEW_SPAWN_EGG_REGEX = re.compile(
    r"((?:[a-zA-Z0-9_]+:)?[a-zA-Z0-9_]+)_spawn_egg")

# An item in format that provides both it's name and the data value (e.g
# "stone:1" or "minecraft:stone:1")
ITEM_WITH_DATA_REGEX = re.compile(
    r"((?:[a-zA-Z0-9_]+:)?[a-zA-Z0-9_]+):([1-9][0-9]*)"
)

class InvalidRecipeException(Exception):
    '''Exception for invalid recipe files'''

class ActorIdWildcard(NamedTuple):
    actor_name: str

class RecipeKey:
    def __init__(self, json_data: Any):
        if isinstance(json_data, str):
            if match := ITEM_WITH_DATA_REGEX.fullmatch(json_data):
                item = match[1]
                data = int(match[2])
                json_data = {"item": item, "data": data}
            else:
                json_data = {"item": json_data}
        if not isinstance(json_data, dict):
            raise InvalidRecipeException(
                "Recipe 'key' instance is not a dict or str")
        if not "item" in json_data:
            raise InvalidRecipeException(
                "Recipe 'key' instance property is missing 'item'")
        if not isinstance(json_data["item"], str):
            raise InvalidRecipeException(
                "Recipe 'key' property 'item' is not a string")
        recipe_key_item = json_data["item"]
        if match := NEW_SPAWN_EGG_REGEX.fullmatch(recipe_key_item):
            self.item = "minecraft:spawn_egg"
            item_data = match[1]
            if ":" not in item_data:
                item_data = f"minecraft:{item_data}"
            self.data: Union[int, ActorIdWildcard] = ActorIdWildcard(item_data)
        elif match := ITEM_WITH_DATA_REGEX.fullmatch(recipe_key_item):
            self.item = match[1]
            self.data = int(match[2])
            if "data" in json_data:
                raise InvalidRecipeException(
                    "Recipe key is ambiguous, providing the data value both "
                    "in the item name and the data property.")
        else:
            if ":" not in recipe_key_item:
                recipe_key_item = f"minecraft:{recipe_key_item}"
            self.item = recipe_key_item
            self.data = self._load_data(json_data)

    def _load_data(self, json_data: Any) -> Union[int, ActorIdWildcard]:
        recipe_key_data = None
        if isinstance(json_data.get("data", 0), int):
            recipe_key_data = json_data.get("data", 0)
        elif "data" in json_data and isinstance(json_data["data"], str):
            if match := ACTOR_ID_WILDCARD_REGEX.fullmatch(json_data["data"]):
                recipe_key_data = ActorIdWildcard(match[1])
                if self.item != "minecraft:spawn_egg":
                    raise InvalidRecipeException(
                        "The ActorIdWildcard is only supported for "
                        f"'minecraft:spawn_egg' not {self.item}")
            else:
                try:
                    recipe_key_data = int(json_data["data"])
                except ValueError:
                    pass
        if recipe_key_data is None:
            raise InvalidRecipeException(
                "Recipe 'key' property 'data' is not an int or "
                "a ActorIdWildcard")
        return recipe_key_data

    def get_true_item_name(self) -> str:
        '''
        Returns the true name of the item. In most cases it's the same as
        self.item, but for spawn eggs it's
        '<namespace>:<entity_name>_spawn_egg'
        '''
        if not isinstance(self.data, ActorIdWildcard):
            return self.item
        else:
            return self.data.actor_name + "_spawn_egg"

    def get_full_item_name(self)-> str:
        '''
        Gets the full name of the item including the data value for recipes in
        the content guide. Format: '<namespace>:<item>:<data>'
        '''
        if isinstance(self.data, int):
            pattern = re.compile(r"(.+)(:[0-9]+)")
            if match := pattern.fullmatch(self.item):
                return self.item
            return f"{self.item}:{self.data}"
        return f"{self.item}"

def load_recipe_name(recipe_path: Path) -> str:
    '''
    Simple function for loading just the name of the recipe from the file.
    Gets the name form the file. If it fails it raises InvalidRecipeException.
    '''
    try:
        json_data = load_jsonc(recipe_path).data
        if 'minecraft:recipe_shaped' in json_data:
            recipe = json_data["minecraft:recipe_shaped"]
        elif "minecraft:recipe_shapeless" in json_data:
            recipe = json_data["minecraft:recipe_shapeless"]
        name = recipe["description"]["identifier"]
        if not isinstance(name, str):
            raise InvalidRecipeException(
                f"Failed to load recipe name from {recipe_path}: "
                "identifier is not a string")
        return name
    except (LookupError, FileNotFoundError) as e:
        raise InvalidRecipeException(
            f"Failed to load recipe name from {recipe_path}: {e}")

class RecipeCrafting:
    def __init__(self, json_data: Any):
        if 'minecraft:recipe_shaped' in json_data:
            recipe = json_data["minecraft:recipe_shaped"]
            self.name = self._load_name(recipe)
            self.pattern = self._load_pattern(recipe)
            self.result = self._load_result(recipe)
            self.keys = self._load_keys(recipe)
        elif "minecraft:recipe_shapeless" in json_data:
            recipe = json_data["minecraft:recipe_shapeless"]
            self.name = self._load_name(recipe)
            self.pattern = self._fake_pattern_from_ingredients(recipe)
            self.result = self._load_result(recipe)
            self.keys = self._fake_keys_from_ingredients(recipe)
        else:
            raise InvalidRecipeException(
                "Unknown recipe type (only minecraft:recipe_shaped and "
                "minecraft:recipe_shapeless are supported)")

    def _fake_pattern_from_ingredients(self, recipe: Any) -> List[str]:
        ingredients = recipe["ingredients"]
        if isinstance(ingredients, dict):
            ingredients = [ingredients]
        if not isinstance(ingredients, list):
            raise InvalidRecipeException("Recipe 'ingredients' property is not a list")
        pattern = [
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
        ]
        keys = []
        for ingredient_key, ingredient in enumerate(ingredients):
             # Convert short form (str) to full form {item: str}
            if isinstance(ingredient, str):
                ingredient = {"item": ingredient}
            elif not isinstance(ingredient, dict):
                raise InvalidRecipeException(
                    "Recipe 'ingredients' property is not a list of strings "
                    "or dicts.")
            for i in range(ingredient.get("count", 1)):
                keys.append(str(ingredient_key))
        if len(keys) > 9:
            raise InvalidRecipeException(
                "Shapeless recipes can have at most 9 ingredients."
                "Ingredients that use the 'count' property greater than 1 "
                "are couted as multiple ingredients.")
        for i in range(3):
            for j in range(3):
                index = i * 3 + j
                if index < len(keys):
                    pattern[i][j] = keys[index]
                else:
                    break
        str_pattern: List[str] = []
        for i in range(3):
            str_pattern.append("".join(pattern[i]))
        return str_pattern

    def _fake_keys_from_ingredients(self, recipe: Any) -> Dict[str, RecipeKey]:
        # KEYS: self.keys
        ingredients = recipe["ingredients"]
        if isinstance(ingredients, dict):
            ingredients = [ingredients]
        if not isinstance(ingredients, list):
            raise InvalidRecipeException("Recipe 'ingredients' property is not a list")
        if len(ingredients) > 9:
            raise InvalidRecipeException("Shapeless recipes can have at most 9 ingredients")
        recipe_keys: Dict[str, RecipeKey] = {}
        for i, v in enumerate(ingredients):
            recipe_keys[str(i)] = RecipeKey(v)
        return recipe_keys

    def _load_name(self, recipe: Any) -> str:
        # NAME: self.name
        name = recipe["description"]["identifier"]
        if not isinstance(name, str):
            raise InvalidRecipeException("Recipe name is not a string")
        return name

    def _load_pattern(self, recipe: Any) -> List[str]:
        # PATTERN: self.pattern
        pattern = recipe["pattern"]
        if not isinstance(pattern, list):
            raise InvalidRecipeException("Pattern is not a list")
        if len(pattern) > 3:
            raise InvalidRecipeException("Pattern is not 3x3")
        elif len(pattern) < 3:
            for _ in range(len(pattern), 3):
                pattern.append("   ")
        for i in range(len(pattern)):
            if not isinstance(pattern[i], str):
                raise InvalidRecipeException("Pattern raw is not a string")
            if len(pattern[i]) > 3:
                raise InvalidRecipeException("Pattern is not 3x3")
            elif len(pattern[i]) < 3:
                pattern[i] = pattern[i].ljust(3)  # Add spaces
        return pattern

    def _load_result(self, recipe: Any) -> RecipeKey:
        result = recipe["result"]
        if isinstance(result, list):
            if len(result) == 0:
                raise InvalidRecipeException(
                    "Crafting recipe doesn't define the result item.")
            result = result[0]
        return RecipeKey(result)

    def _load_keys(self, recipe: Any) -> Dict[str, RecipeKey]:
        # KEYS: self.keys
        keys = recipe["key"]
        if not isinstance(keys, dict):
            raise InvalidRecipeException("Recipe 'key' property is not a dict")
        recipe_keys: Dict[str, RecipeKey] = {}
        for k, v in keys.items():
            recipe_keys[k] = RecipeKey(v)
        # Check if patterns use only defined keys
        for p in self.pattern:
            for c in p:
                if c not in recipe_keys and c != " ":
                    raise InvalidRecipeException(
                        f"Pattern '{p}' uses an undefined key '{c}'")
        return recipe_keys

class RecipeFurnace:
    def __init__(self, json_data: Any):
        recipe = json_data["minecraft:recipe_furnace"]
        self.name = self._load_name(recipe)
        self.input = self._load_input(recipe)
        self.output = self._load_output(recipe)

    def _load_name(self, recipe: Any) -> str:
        # NAME: self.name
        name = recipe["description"]["identifier"]
        if not isinstance(name, str):
            raise InvalidRecipeException("Recipe name is not a string")
        return name

    def _load_input(self, recipe: Any) -> RecipeKey:
        result = recipe["input"]
        return RecipeKey(result)

    def _load_output(self, recipe: Any) -> RecipeKey:
        output = recipe["output"]
        return RecipeKey(output)

# This class uses different (newer) implementation of recipe loading that
# utilizes the JSONWalker class.
# TODO - update other recipe classes to use this one.
class RecipeBrewing:
    def __init__(self, json_data: JSONWalker):
        recipe = json_data / "minecraft:recipe_brewing_mix"
        self.name: str
        self.input: RecipeKey
        self.reagent: RecipeKey
        self.output: RecipeKey

        name = recipe / "description" / "identifier"
        if not name.exists or not isinstance(name.data, str):
            raise InvalidRecipeException("Recipe name is not a string")
        self.name = name.data

        input_ = recipe / "input"
        if not input_.exists:
            raise InvalidRecipeException("Recipe 'input' property is missing")
        self.input = RecipeKey(input_.data)

        reagent = recipe / "reagent"
        if not reagent.exists:
            raise InvalidRecipeException("Recipe 'reagent' property is missing")
        self.reagent = RecipeKey(reagent.data)

        output = recipe / "output"
        if not output.exists:
            raise InvalidRecipeException("Recipe 'output' property is missing")
        self.output = RecipeKey(output.data)


Recipe = Union[RecipeCrafting, RecipeFurnace, RecipeBrewing]

def load_recipe(recipe_path: Path) -> Recipe:
    walker = load_jsonc(recipe_path)
    if "minecraft:recipe_shaped" in walker.data:
        return RecipeCrafting(walker.data)
    elif "minecraft:recipe_shapeless" in walker.data:
        return RecipeCrafting(walker.data)
    elif "minecraft:recipe_furnace" in walker.data:
        return RecipeFurnace(walker.data)
    elif "minecraft:recipe_brewing_mix" in walker.data:
        return RecipeBrewing(walker)
    else:
        raise InvalidRecipeException(
            "Unknown recipe type (only minecraft:recipe_shaped, "
            "minecraft:recipe_shapeless, minecraft:recipe_furnace and "
            "minecraft:recipe_brewing_mix are supported)")
