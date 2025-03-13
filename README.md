# Description
This repository contains a Python module used by the [Content Guide Generator Regolith filters](https://github.com/Shapescape-Software/content_guide_generator). The module can be used independently, however it is recommended to use it as a Regolith filter.

You can read more about this tool in the [documentation](docs/README.md)


# Changelog

## 1.7.5
Fixed formatting not correctly applying.

## 1.7.4
Updated formatting for "empty category" messages and updated formatting for items summaries.

## 1.7.3
Added support for item tags in recipes.

## 1.7.2
Fixed the crashes of the feature_tree function.

## 1.7.1
The feature/feature_rule summaries will return a message that says that the project doesn't have features/feature rules if there is no fr or f on the project.

## 1.7.0
Added 6 new functions for summarizing features and feature rules: `list_features()`, `summarize_features()`, `summarize_features_in_tables()`, `list_feature_rules()`, `summarize_feature_rules()`, `summarize_feature_rules_in_tables()` and `feature_tree()`.

## 1.6.0
Added new function `summarize_trades()` which generates a human-readable summary of all of the trades in the game and an information about the entities that use them.

## 1.5.1
The recipe image generator can accept shapeless recipes which define ingredients as a dictionary.

## 1.5.0
The `summerize_...` functions generate different messages when there is no data to summarize. They say that there is missing data.

## 1.4.4
Added a function for outputing data to multiple files. This is used with the combination of the "output_paths" property of the Regolith filter which uses this library.

## 1.4.3
Added `"block_entity"` entity category.

## 1.4.2
Filter supports older verison of Python (3.9) previously only supported 3.10+

## 1.4.1
The recipes generated in the content guide include the data values of the
items.

## 1.4.0
Added support for custom blocks documentation using 
`list_blocks()`, `summarize_blocks()` and `summarize_blocks_in_tables()`

## 1.3.1
Fixed listing spawn eggs in trade tables and loot tables.

## 1.3.0
Spawn egg summary can detect items that use the `query.get_actor_info_id`
function to assign the spawn egg to an entity.

## 1.2.0
Added new functions for summarizing spawn eggs. They are analogous to the
functions for summarizing items.

## 1.1.2
Added `"vehicle"` entity category.

## 1.1.1
Fixed a typo "encodint" -> "encoding". Fixes the filters ability to update the
entity files.

## 1.1.0
Item report generator improvements:
- The default item player-facing value was changed to False (items are assumed to be non-player facing)
- The summarize_items() function now adds new info to the report:
  - list of recipes that craft the item
  - list of entities that trade using the item
  - list of entities that drop the item
- Items that are craftable, tradable or drop as a loot and don't have the player_facing property are
  assumed to be player facing.

## 1.0.1
Fixed problems with encoding. Some of the functions read
## 1.0.0
initial implementation.