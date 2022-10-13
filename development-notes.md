# Description
This page includes the notes about planned features for the tool.

# DESIGN
# Design
## Completion guide
**Regolith filter:**
Generate text based on functions from
`guide/test/{step number}_{step_name}`

# Navigation
## General
FILLED MANUALLY

In Regolith filter data put the desctiption in a `*.md` file.

## Key locations
**Regolith filter:**
Generate text based on the function from
`**/warp/{name}`

The structure of the file
```
# KEY LOCATION        ## Type is used to 
# <description>
<tp command>          ## Strip description from that 
```


Adding a comment to warp functions could be enforced by a Regolith filter.

## Landmarks
__Same solution as for hte key locations.__

**Regolith filter:**
Generate text based on the function from
`**/warp/{name}`

The structure of the file
```
# LANDMARK            ## Type is used to 
# <description>
<tp command>          ## Strip description from that 
```


## Containers
FILLED MANUALLY

In Regolith filter data put the desctiption in a `*.md` file.


## Hidden content
FILLED MANUALLY

In Regolith filter data put the desctiption in a `*.md` file.

# Character and villagers
Add minecraft:entity -> description -> guide:
  - locations: list[Vector3D]
  - description: list[string]
  - category: Literal["character", "trader", "utility", "projectile", "creature"]

Regolith should warn about missing properties. User has to ingnore them explicitly
if that's needed.

## Characters
_Explained in previous section_
## Villagers
_Explained in previous section_

# Gameplay Elements
## Mechanics
FILLED MANUALLY or...

**FUTURE IMPLEMENTATION:**
> We could automate that if we had a different system for organizing the
> projects. I'm talking about the system that puts files into certain locations
> based on their file extensions.
> 
> This specifically: <https://github.com/Nusiq/regolith-filters/tree/master/custom_project>
> 
> I wouldn't take that implementation but its extremely simple to implement
> (at most 30 min in Python for me).


## User Interface (UI)
FILLED MANUALLY

## Added Key Bindings
In `entity -> description -> guide` add new property `bindings: List[str]`

If entity doesn't require any description then put a `false` value to the
description field.

# TECHNICAL ELEMENTS
# Changes to Original Minecraft Funcionallity
## Minecraft Changes
FILLED MANUALL or...

Look at the "DESIGN->Mechanics" category. This field looks like a duplicate
to me.

# Custom Inventory Items
## Player Facing Items
Easy to list automatically. Every items which is obtainable by one of the
following:

- trade
- crafting recipe
- loot table
- give commands in functions that don't match `**/debug/**` pattern (???)
- Description in the item

Item report example
```
# Really nice blue stone
<description field from the item>

Identifier:** shapescape:really_nice_blue_stne
**Dropped by:**

- minecraft:zombie
- shapescape:gnome

## Crafted with
- `minecraft:stone` as `1`
- `minecraft:lapis` as `2`

**Pattern:**
1 2 #
# # #
# # #

**The item can be obtained with commands.**

**Other ways of obtaining:**
<obtainted_through filed from the item>
```

## Non-Player Facing Items
Easy to list automatically. Every item which isn't on the previous list.

# Custom Creaters, Entities, and Decorations
## Player Facing Entities
_Use the fields described in prvious points_



## Non-Player Facing Entities
_Use the fields described in prvious points_

# Custom Sounds
## Custom sounds
Easy to list from sound_definitions.json + checking if linked OGG files exist.
We should check for that anyways to look for invalid sound definitions.


Basically copy sounds_definitions.json. List all of the ids and in them list
all of the sounds. Like this

```
## Id of the sound (id.of.the.sound):
- funky/sound/1.ogg
- some/other/sound/2.ogg
## Id of the sound 2 (id.of.the.sound.2):
- this/is/a/sound/3.ogg
## Id of the sound 3 (id.of.the.sound.3):
- sound/sound/sound/sound.ogg
```

# Changelog
## Most Recent Changes
Manually keep list of the fields named after version releases in md files.
