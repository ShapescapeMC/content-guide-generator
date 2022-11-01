# Description
This is a repository for the Content Guide generator. It is a Python module which can be used independently, however
it is recommended to use it as a Regolith filter. See: https://github.com/ShapescapeMC/regolith-filters

You can read more about this tool in the [documentation](docs/README.md)


# Changelog
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