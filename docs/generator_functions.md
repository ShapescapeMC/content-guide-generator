<!-- doctree start -->
- [About the documentation](/docs/README.md)
- [Arguments Types](/docs/arguments_types.md)
- [Custom properties](/docs/custom_properties.md)
- [Generator functions](/docs/generator_functions.md)
- [Tutorial](/docs/tutorial.md)
<!-- doctree end -->
# Generator functions

Generator functions are the functions that you can use to insert text into the
documentation. To do that, use the `:generate:` tag. The syntax is as follows:
```
:generate: <function_name>([arguments])

- <function_name> - the name of the function
- [arguments] - list of the arguments. The arguments are separated and must be
  written in the same order as in the function's documentation. Some functions
  let you skip some arguments at the end of the list. If argument is optional,
  it has "[OPTIONAL]" tag added to its description.
```

The tag and the functions are replaced with the text that the function returns.

> **WARNING**
>
> This page refers to arguments of the functions using their data types or short
> descriptive words that tell what arguments are (like glob pattern). If you
> don't know what that means, you should read the
> [Arguments Types](/docs/arguments_types.md)

> **WARNING**
>
> Some of the functions use "custom entity properties" or "custom item properties".
> You can read about them in the [Custom Properties](/docs/custom_properties.md)

# `completion_guide()`
Generates the completion guide for the map based on the completion guide
functions. The function names must follow the pattern `<step>_<title>`. Where
`<step>` is an integer to determine the order of the steps and `<title>` is the
title of the step. The `<title>` should be written in snake_case. The function
will change that to Title Case in the output.
## Syntax
```
:generate: completion_guide(search_patterns, exclude_patterns)
```

**Properties:**
- `search_patterns` - glob pattern or list of glob patterns to match files to
  be included in the completion guide.
- `exclude_patterns [OPTIONAL]` -  glob pattern or list of glob patterns to match the files
  to be excluded from the completion guide (even if they match the
  `search_patterns`). The value of this property is `null` by default.
  You don't have to specify it if you don't want to exclude any files.

**Example**

Input
> :generate: completion_guide("completion_guide/*.mcfunction")

Output

> ### 1 - Start level 1
> Start level 1 using the menu in lobby.
> 
> You can complete this step using: `function completion_guide/1_start_level_1`
> 
> ### 2 - Complete level 1
> Win the level 1 by killing the fruits. You can use the
> `debug/win_wave` function to win a wave. You can use the `debug/win_level`
> function to automatically win the level.
> 
> You can complete this step using: `function completion_guide/2_complete_level_1`
> ...


# `warp()`
Generates descriptions of places that can be accessed using warp functions.
The content of the matching files should follow the pattern:
```
# <description using comments (can have multiple lines)>
<tp command>
```
The `warp()` function extarts the coordinates from the `tp` command and adds
the description.
## Syntax
```
:generate: warp(search_patterns, exclude_patterns)
```


**Properties:**
- `search_patterns` - glob pattern or list of glob patterns to match files to
  be included.
- `exclude_patterns [OPTIONAL]` - glob pattern or list of glob patterns to
  match the files to be excluded (even if they match the `search_patterns`).
  The value of this property is `null` by default. You don't have to specify
  it if you don't want to exclude any files.

**Example:**

Input

> :generate: warp("game_loop/level/*/warp.mcfunction")

Output

> - Spawn location of level 9 (113 -60 -597)
> - The lobby. This is the location where you can choose the level you want to
>   play and view the credits screen. (1278 -60 -876)
> ...



# `insert()`
Inserts an external MD file into the `TEMPLATE.md` file.
## Syntax
```
:generate: insert(path)
```
**Properties**
- `path` - path to the MD file relative to the `TEMPLATE.md` file.

**Example:**

Input

> :generate: insert("templates/mechanics.md")

Output

> The content of the mechanics.md file

# `list_entities()`, `summarize_entities()` and `summarize_entities_in_tables()`
The functions that list entities using their identifiers. Some of them provide
some additional information based on custom entity properties.

- `list_entities()` is the simplest function. It only lists the identifiers
- `summarize_entities()` writes summary in a formatted text form
- `summarize_entities_in_tables()` writes summary in a table form

## Syntax
```
:generate: list_entities(search_patterns, exclude_patterns, categories)
```
```
:generate: summarize_entities(search_patterns, exclude_patterns, categories)
```
```
:generate: summarize_entities_in_tables(search_patterns, exclude_patterns, categories)
```
**Properties:**
- `search_patterns` - glob pattern or list of glob patterns to match files to
  be included.
- `exclude_patterns [OPTIONAL]` - glob pattern or list of glob patterns to
  match the files to be excluded (even if they match the `search_patterns`).
  The value of this property is `null` by default. You don't have to specify
  it if you don't want to exclude any files.
 - `categories [OPTIONAL]` - the categories of the entities to be included.
   The category is a cusom property of the entity added to the "description"
   filed in the entity behavior. Category is a string. You can pick one of the
   following categories: `"character"`, `"trader"`,
   `"non_player_facing_utility"`, `"player_facing_utility"`, `"projectile"`,
   `"creature"`, `"decoration"`, `"interactive_entity"`. You can read more
   about the categories in the [Custom Properties](/docs/custom_properties.md)
   page. By default, all categories are included.

**Example list_entities()**

Input

> :generate: summarize_entities_in_tables("**/*.json", null, ["projectile"])

Output

> - shapescape:apple_projectile
> - shapescape:potato_bullet
> - shapescape:potato_bullet_turret
> ...

**Example summarize_entities()**

Input

> :generate: summarize_entities("**/*.json", null, ["projectile"])

Output

> ### shapescape:apple_projectile
> A projectile shoot by the apple enemy.
> 
> ### shapescape:potato_bullet
> A projectile used by the potato launching weapons (Potato Yammer, Potato Masher, and Potato Shooter).
> 
> ### shapescape:potato_bullet_turret
> A projectile used by the Potato Turret.
> ...

**Example summarize_entities_in_tables()**

Input

> :generate: summarize_entities_in_tables("**/*.json", null, ["projectile"])

Output

> | Entity | Description | Locations |
> |-------|----------|------|
> | shapescape:apple_projectile | A projectile shoot by the apple enemy. | N/A |
> | shapescape:potato_bullet | A projectile used by the potato launching weapons (Potato Yammer, Potato Masher, and Potato Shooter). | N/A |
> | shapescape:potato_bullet_turret | A projectile used by the Potato Turret. | N/A |
> ...

# `list_items()`, `summarize_items()` and `summarize_items_in_tables()`
The functions that list entities using their identifiers. Some of them provide
some additional information based on custom item properties.

- `list_items()` is the simplest function. It only lists the identifiers
- `summarize_items_in_tables()` writes summary in a table form
- `summarize_items()` writes summary in a formatted text form. This format is
   the most detailed one. It contains the list of entities that drop the item,
   a list of entities that trade using this item and a list of recipes that
   create this item.

## Syntax
```
:generate: list_items(search_patterns, exclude_patterns ,player_facing)
```
```
:generate: summarize_items(search_patterns, exclude_patterns ,player_facing)
```
```
:generate: summarize_items_in_tables(search_patterns, exclude_patterns ,player_facing)
```
**Properties:**
- `search_patterns` - glob pattern or list of glob patterns to match files to
  be included.
- `exclude_patterns [OPTIONAL]` - glob pattern or list of glob patterns to
  match the files to be excluded (even if they match the `search_patterns`).
  The value of this property is `null` by default. You don't have to specify
  it if you don't want to exclude any files.
 - `player_facing [OPTIONAL]` - a string that decides if player-facing,
   non-player-facing or both types of items should be included. You can pick
   one of the following values: `"player_facing"`, `"non_player_facing"`,
   `"all"`. By default `"all"` is used which means that both types of items
    are included.

**Example list_items()**

Input

> :generate: list_items("**/*.json", null, "player_facing")

Output

> - shapescape:coin
> - shapescape:fire_extinguisher
> - shapescape:flame_thrower
> ...

**Example summarize_items()**

Input

> :generate: summarize_items("**/*.json", null, "player_facing")

Output

> ### shapescape:coin
> Drops from fruits. When collected, it is removed from the player's inventory and added to the coin counter.
> 
> ### shapescape:fire_extinguisher
> Fire extinquisher weapon. Freezes enemies. It can be purchased from the weapon shop.
> 
> ### shapescape:dragon_pants
> No, they're not made out of dragon skin, but they have a very cool dragon pattern on them.
> #### **Crafting recipe:**
> **Ingredients:**
> - minecraft:bone as N
> - minecraft:dragon_breath as D
> 
> **Pattern:**
> ```
> NNN
> NDN
> N N
> ```
> 
> #### **Dropped by:**
> - shapescape:skeleton_dummy
> #### **Traded by:**
> - shapescape:armor_trader1

**Example summarize_items_in_tables()**

Input

> :generate: summarize_items_in_tables("**/*.json", null, "player_facing")

Output

> | Item | Description |
> |------|-------------|
> | shapescape:coin | Drops from fruits. When collected, it is removed from the player's inventory and added to the coin counter. |
> | shapescape:fire_extinguisher | Fire extinguisher weapon. Freezes enemies. It can be purchased from the weapon shop. |
> | shapescape:flame_thrower | The Flameinator weapon. Sets enemies on fire. It can be purchased from the weapon shop. |
> ...



# `sound_definitions()`
Generates a list of sound definitions from the sound_definitions.json file.
The list includes "friendly names" and the actual identifiers. The friendly
names are based on the identifiers. This function takes no properties.

## Syntax
```
:generate: sound_definitions()
```
**Properties:** NONE

**Example**

Input

> :generate: sound_definitions()

Output

> - Custom - Shop Error (custom.shop.error)
> - Button - Click (button.click)
> - Shop - Buy (shop.buy)
> - Game state - Level lost (game_state.level_lost)
> - Game state - Level won (game_state.level_won)
> - Event - Wave complete (event.wave_complete)
> ...

