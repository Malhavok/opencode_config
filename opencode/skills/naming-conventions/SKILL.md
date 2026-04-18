---
name: naming-conventions
description: Universal naming conventions extracted from the user's code across Python, Elixir, and Lua. Load this whenever writing or reviewing new code, deciding what to call a function/variable/module, or reconciling the style of an edit with the surrounding codebase.
metadata:
  scope: universal
  languages: python,elixir,lua
---

# Naming conventions

The user's style is extremely consistent across languages. Follow these rules
unless the surrounding file is already breaking them - in which case match the
file.

## Case, per language

| Language | Variables / functions / modules files | Classes / modules / structs | Constants          |
|----------|---------------------------------------|------------------------------|--------------------|
| Python   | `snake_case`                          | `PascalCase`                 | `UPPER_SNAKE_CASE` |
| Elixir   | `snake_case`                          | `PascalCase` (dots for nesting: `Event.Run`) | `@snake_case` module attributes |
| Lua      | `snake_case` for locals/fields, `camelCase` for methods, `_camelCase` for private methods | `PascalCase` for modules/classes | no screaming case - just a `snake_case` field on the module table |

Files are always `snake_case` - even in Lua where the module inside is PascalCase
(e.g. file `texture_atlas.lua` defines `local TextureAtlas = Class {}`).

## Be descriptive, not terse

Names are **long and explicit**. Full words beat abbreviations.

Good:

```python
get_shortest_path_with_distance
build_initial_check_list
count_ways_in_which_change_can_be_provided
iterate_rows_and_columns_after_first
```

```elixir
def is_input_valid?(lines)
def does_belong_to_range?(range, value)
def search_for_valid_name(list, offset)
```

```lua
function Matcher:addMatchChangedCallback(callback)
function Board:_buildAllowedTiles(tile)
```

Avoid `dat`, `tmp`, `res`, `lst`, single letters (except loop counters and
destructured vector components).

## Accepted short names

These are the few allowed abbreviations:

- `elem` - generic loop element, favoured over `item`
- `idx`, `x_idx`, `y_idx` - indexes
- `ex` - exception binding: `except BaseException as ex:`
- `pos`, `x_pos`, `y_pos` - positions
- `_foo` - unused parameter / destructured value you want to name for the reader

## Prefix verbs for action functions

Function prefixes the user reaches for repeatedly:

- `get_*` - read / compute and return
- `build_*` - assemble from parts
- `make_*` - factory, often returning a class (see python-style's `make_grid`)
- `load_*` - read from disk, parse input
- `calculate_*` - derive a value
- `iterate_*` - generator / yields / Enum
- `find_*` - search, may return `None`/`nil`
- `apply_*` - perform an op / mutate
- `handle_*` - dispatch handler
- `draw_*` - render
- `parse_*` - parse a line, a section, a binary

Classmethod / factory constructors are named `from_line`, `from_char`,
`from_short`, `init` (Python) and `parse_line`, `new` (Elixir).

## Predicates

- Python: `is_solid`, `has_remaining_true`, `does_calibration_work`.
- Elixir: end with `?`. The older Erlang-era `is_` prefix is combined with it:
  `is_input_valid?`, `contains_abba?`, `does_cross_any_edge?`. This is
  technically against the community guide but this user always does it.
- Lua: `is_active`, `is_selecting`, `did_clicked_state_change`, `has_*`.

## Booleans

Prefix with `is_`, `has_`, `did_`, `does_`, `should_`. No bare `active`,
`clicked`, or similar - always qualified: `is_active`, `was_clicked`.

## Unused parameters

Always prefix with `_`. The user does this even when the semantic meaning still
matters to the reader:

```python
def apply_bxc(_operand: int, registers: Registers, _output: list[int]) -> OpcodeResult:
```

```elixir
def parse_input(["value " <> params | tail], bots, _map)
```

## Positions and sizes

The consistent convention is `<axis>_<role>`: `x_pos`, `y_pos`, `x_idx`,
`y_idx`, `x_size`, `y_size`, `x_count`, `y_count`. Never `xPos` / `row`/`col`
(except for legacy code).

## Private vs public

- Python: single leading underscore for module-level or class-level private:
  `_fill_info`, `_raw_set`, `_load_case`. No double-underscore name mangling.
- Elixir: `defp` for everything internal. Only the module's public contract
  (`part1/1`, `part2/1`, `parse_line/1`, struct builders) uses `def`.
- Lua: `_camelCase` methods on classes are private by convention:
  `_spawnTiles`, `_tileToPosition`, `_buildAllowedTiles`.

## British English

This is non-negotiable. Use British spelling for names and comments:

- `colour` not `color` (e.g. `RuleSameColour`, `same_colour.lua`)
- `neighbour` not `neighbor` (e.g. `CARDINAL_DIRECTIONS`, `get_neighbours`)
- `behaviour`, `analyse`, `initialise`, `optimise`

If you find `color`/`neighbor` in code you're editing, do not rename it in the
same PR - but any new symbol must use the British form.

## Constants: module-level or atom-like

Python:

```python
DEFAULT_AOC_CONFIG_PATH = pathlib.Path('./.config.json')
CARDINAL_DIRECTIONS = [DIRECTION_UP, DIRECTION_DOWN, DIRECTION_LEFT, DIRECTION_RIGHT]
PERPENDICULAR_DIRECTIONS = {
    DIRECTION_UP:    [DIRECTION_LEFT, DIRECTION_RIGHT],
    DIRECTION_DOWN:  [DIRECTION_LEFT, DIRECTION_RIGHT],
    DIRECTION_LEFT:  [DIRECTION_UP,   DIRECTION_DOWN],
    DIRECTION_RIGHT: [DIRECTION_UP,   DIRECTION_DOWN],
}
```

Elixir:

```elixir
@start_position 50
@total_numbers 100
@up Point2D.new(0, -1)
@neighbours [{1, 1}, {1, -1}, {-1, 1}, {-1, -1}]
@cache :hash_cache
```

Lua (no SCREAMING_CASE - module table field):

```lua
local WorldScaler = {
    num_y_tiles = 11,
    pixels_per_tile = nil,
    num_x_tiles = nil,
}
```

## Atoms and tags (Elixir-flavoured but universal principle)

When a value represents a tagged state, use short `:snake_case` atoms or string
literals, not integers: `:ok`, `:error`, `:missing`, `:notimplemented`,
`:duplicated_operation`. Callers should match on them.

## Test names

- Python: `test_1`, `test_2` as the default, descriptive when it pays off
  (`test_basic`, `test_tricky_logic`, `test_large_input`).
- Elixir: `describe "Module.fun/arity"` blocks, tests named with the behaviour
  under test.

## File names

- Python modules: `tile2d.py`, `grid2d.py`, `key_cache.py`, `status_printer.py`.
- Elixir: `main.ex` per day, `aoc_config.ex`, `day_config.ex` under `lib/`.
- Lua: `texture_atlas.lua`, `world_scaler.lua`, `i_can_bounce.lua`.

Always `snake_case`, no dashes, no camelCase in filenames.

## Rename tolerance

If you touch a legacy file that violates these rules, do not rename things in
the same change. Match the file's existing vocabulary and add a separate todo
if a broader rename is warranted.

## Units

If unit is not obvious from type, ensure to add it in variable name.

Good:
```python
TIMEOUT_SECONDS = 1.0
```

```elixir
@angle_radians 3.14159265 / 2
@timeout_ms 1000
```

Bad:

```python
TIMEOUT = 1.0
```

```elixir
@angle 3.14159265 / 2
@timeout 1000
```

This is non-negotiable. If you touch a legacy file that violates these rules,
consider at least adding a comment that would explain the unit.
