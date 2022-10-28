# DESIGN

# Design
## Completion guide
:generate: completion_guide("completion_guide/*.mcfunction")

# Navigation
## General
:generate: insert("templates/general.md")

## Key locations
:generate: warp("warp/level/key_locations/*.mcfunction")

## Landmarks
:generate: warp("warp/level/landmarks/*.mcfunction")

## Containers
:generate: insert("templates/containers.md")

## Hidden content
:generate: insert("templates/hidden_content.md")

# Character and Villagers
## Characters

*This section provides a list of character entities on the map. All entities
including the characters are described below in the "Player Facing Entities"
section. To avoid writing the same information twice, this list only contains
the names of the entities.*

:generate: summarize_entities_in_tables("**/*.json", null, ["character"])

## Villagers

*This section provides a list of villager entities on the map. All entities
including the villagers are described below in the "Player Facing Entities"
section. To avoid writing the same information twice, this list only contains
the names of the entities.*

:generate: summarize_entities_in_tables("**/*.json", null, ["trader"])

# Gameplay Elements
## Mechanics
:generate: insert("templates/mechanics.md")

## User Interface (UI)
:generate: insert("templates/ui.md")
## Added Key Bindings



# TECHNICAL ELEMENTS
# Changes to Original Minecraft Funcionallity
:generate: insert("templates/mc_functionallity_changes.md")
## Minecraft Changes

# Custom Inventory Items
## Player Facing Items
:generate: summarize_items_in_tables("**/*.json", null, "player_facing")
## Non-Player Facing Items
There is no non-player facing items in the game.

# Custom Creaters, Entities, and Decorations
## Player Facing Entities

**Living creatures**

Every living entity that performs some actions on its own:

:generate: summarize_entities_in_tables("**/*.json", null, ["character", "trader", "creature"])


**Menus and other interactive entities**

Shops and menus. Non-living entities that player can interact with:

:generate: summarize_entities_in_tables("**/*.json", null, ["interactive_entity"])

**Projectiles**

Every projectile in the game:

:generate: summarize_entities_in_tables("**/*.json", null, ["projectile"])

**Decorations:**

Purely decorative entities:

:generate: summarize_entities_in_tables("**/*.json", null, ["decoration"])

**Utilities:**

Entities that are visible but don't interact with the player directly

:generate: summarize_entities_in_tables("**/*.json", null, ["player_facing_utility"])

## Non-Player Facing Entities

Invisible entities that affect the game in some way:

:generate: summarize_entities_in_tables("**/*.json", null, ["non_player_facing_utility"])

# Custom Sounds
## Custom sounds
:generate: sound_definitions()

# Changelog
## Most Recent Changes
:generate: insert("templates/most_recent_changes.md")
