<!-- doctree start -->
- [About the documentation](/docs/README.md)
- [Arguments Types](/docs/arguments_types.md)
- [Custom properties](/docs/custom_properties.md)
- [Generator functions](/docs/generator_functions.md)
- [Tutorial](/docs/tutorial.md)
<!-- doctree end -->
# Custom properties
This page lists and explains all custom properties that can be added to JSON
files of the project to control the generation process.

## Behavior Pack Entity Files
### `description`

- Path: `BP/entities/environment/*.json`
- JSON Path: `["minecraft:entity"].description.description`

Description is a string or a list of strings that describes the entity in
`summarize_entities()` and `summarize_entities_in_tables()` functions. If
description is written as a list, it is assumed that each string is a separate
line of the description


**Examples**
```
"This is the main entity used for running commands."
```
```
[
    "This entity serves as player's companion. It has multiple purposes:",
    "- It can heal the player",
    "- It helps with telling the story"
]
```


### `locations`
- Path: `BP/entities/environment/*.json`
- JSON Path: `["minecraft:entity"].description.locations`

Locations is a list of locations that the entity can be found in. Locations
should be written as a list of strings. The strings should follow the format:
`<x> <y> <z>` ,where `<x>`, `<y>` and `<z>` are numbers.

If providing, locations to the information about the entity doesn't make sense,
(e.g. the entity is a mob and spawns dynamically in the world), the property
should be an empty list (`[]`).

**Examples**
```
[]
```
```
["1 2 3", "1.1 -2.3 10"]
```


### `category`
- Path: `BP/entities/environment/*.json`
- JSON Path: `["minecraft:entity"].description.category`

Category is a string that puts the entity into one of the following groups:
- `"character"` - this category was added to match Microsoft's suggestion of
    that describes how to write content guide. The entities used for telling
    the story should be put into this category. Entities from this group should
    be added to the "Characters and Villagers" section of the content guide.
- `"trader"` - this category was added to match Microsoft's suggestion of
    that describes how to write content guide. The living entities used for
    trading should be put into this category. The entities from this group
    should be added to the "Characters and Villagers" section of the content.
- `"non_player_facing_utility"` - every invisible entity like (path markers,
    main entity, invisible spawners, etc.) should be added to this category.
    Entities from this category should go to the "Non-Player Facing Entities"
    section of the content guide.
- `"player_facing_utility"` - this category can be treated as "other" category.
    It describes visible utility entities that don't interact with the player
    directly in any way. Here are some examples:
    - a portal (with particle effect) that spawns mobs. It would be
        non_player_facing but it's visible.
    - an entity that represents a cloud of poison gas.
    - an entity used only to spawn certain particles and despawns immediately
        after spawning.
    - an automatic turret or other traps
- `"projectile"` - every entity that uses "minecraft:projectile" component
- `"creature"` - every living entity that doesn't fit into character or
    trader category (mobs and monsters).
- `"decoration"` - every entity used purely for visual purposes (e.g.
    furniture)
- `"interactive_entity"` - inanimate entities that you spawn on the world to be
    interacted with (e.g. entity based menus, stationary shop entities, etc.)

## Behavior Pack Item Files
### `description`

- Path: `packs/BP/items/*.json`
- JSON Path: `["minecraft:item"].description.description`

Description is a string or a list of strings that describes the item in
`summarize_items()` and `summarize_items_in_tables()` functions. If
description is written as a list, it is assumed that each string is a separate
line of the description

**Examples**
```
"This is the main entity used for running commands."
```
```
[
    "This entity serves as player's companion. It has multiple purposes:",
    "- It can heal the player",
    "- It helps with telling the story"
]
```

### `player_facing`

- Path: `packs/BP/items/*.json`
- JSON Path: `["minecraft:item"].description.player_facing`

Player facing is a boolean value that determines whether the item is a
"player-facing" item or not. Most of the items are player-facing, but the
Micosoft's recommendation is to separate them into two groups, while
documenting.
