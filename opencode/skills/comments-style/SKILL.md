---
name: comments-style
description: Universal comment and docstring style for the user's code - prose sentences in British English, em-dashes, ASCII diagrams, "why not what", section headers in long functions, minimal docstrings. Load this when writing new comments, reviewing documentation, or editing near commented code.
metadata:
  scope: universal
  languages: python,elixir,lua
---

# Comments and documentation

The user writes comments as **full English prose**, in a voice that often says
"we" and favours explaining *why* rather than restating *what*. Comments are
dense where the logic is non-obvious and absent where code speaks for itself.

## Baseline rules

- Comments are **full sentences, starting with a capital letter, ending with a
  period**. Even one-liners.
- Voice is British English. Spell `colour`, `neighbour`, `behaviour`, `analyse`,
  `initialise`.
- First-person plural ("we") is fine and common: "we're already committing
  everything to the main store", "we don't really need to keep distances here".
- No trailing "TODO" without context; if you must leave one, write a sentence
  explaining what and why.

## Punctuation tic: en-dash `–` (U+2013)

The user genuinely uses an en-dash as a mid-sentence connector, not a hyphen
`-` and not `--`. Match this when editing adjacent comments. Examples:

```python
# Preamble – convert all variables from in-state to variables.
# Assumption – the numbers have less variance from the back.
# Rotations shouldn't be taken into account here – just number of tiles.
```

```lua
-- mapping tile_key –> tile
-- Check for allowed neighbours. If a tile was already selected – it's allowed in another place.
-- Note – these might be invalid hits.
```

If your editor makes this awkward, paste it from an existing file. Do not
silently replace existing `–` with `-`.

## Why > what

Good comments explain reasoning:

```python
# All operations only increase values, so if it's too big now, it's not useful any more.
# It is said to be only one path, so no need to do anything fancier.
# Duplicated code to reduce function calls.
# Since we're already committing everything to the main store to make it faster, we just drop the stack.
```

```elixir
# Since we always go from the "smallest" value, we don't really need to keep distances here.
# Picking some big number so we never can go below zero.
# If there are unpaired microchips, the floor isn't safe.
```

```lua
-- When we cut to the tile, we cut including that tile.
-- Nothing else here remains in power if we moved outside of the board.
```

Bad (restates code):

```python
# Increment i by 1.
i += 1
```

## Section headers in long functions

When a function has clear phases, mark them with a short capitalised comment
with a period. No ASCII rulers, no `===` banners.

```python
# Connections.
for line in lines:
    ...

# Reductions.
for connection in connections:
    ...
```

```python
# Cleanup.
# Handle.
# First flap, supporting bottom.
```

```lua
-- Initialize system.
-- Load and setup font.
-- Ensure that everything is properly scaling.
-- State init.
```

## ASCII diagrams when geometry matters

For 2D / 3D layouts, puzzle shapes, state machines, or derivations, include an
inline ASCII picture. This is one of the clearest signature moves of the user.

Example:

```
# Drawing outline of the whole box.
#     0         1         2
#     0123456789012345678901234
#  0         /---------\
#  1         |Title    |
#  2         +---------+
#  3         |  Back   |
#  4         |         |
#  5         +---------+
#  6       /\| Bottom  |/\
#  7     /+--+---------+--+\
#  8    | |  |  Front  |  | |
#  9     \+--|         |--+/
# 10         +---------+
```

Or a mathematical derivation as a docstring:

```python
def when_intersects(p_1: int, v_1: int, p_2: int, v_2: int) -> int | None:
    """
    Looking for a 1d integer intersections.

    So, for t such as:
    p_1 + t * v_1 = p_2 + t * v_2
    t * (v_1 - v_2) = (p_2 - p_1)
    t = (p_2 - p_1) / (v_1 - v_2)
    """
```

Do not half-heartedly strip these out when tidying.

## Echoing the input / problem statement

When solving a problem with a textual spec, quote one or two example lines of
the input near the parser:

```elixir
# value 61 goes to bot 209
# bot 189 gives low to bot 62 and high to bot 168
```

## Docstrings: short and purposeful

- The user **rarely writes docstrings** in day-to-day code (AoC solutions have
  near zero).
- When a utility / framework function gets one, it is short, prose-style, not
  PEP 257. Often lists assumptions as bullet dashes:

```python
class Labyrinth(Generic[FieldType]):
    """
    Assuming:
    - given grid IS a labyrinth (doesn't check it)
    - using cardinal directions only
    """
```

- For library code (Python `utils/`, Elixir `lib/`) a one-liner describing
  behaviour is enough:

```python
def load_empty_lines_split(filename: pathlib.Path) -> list[list[str]]:
    """
    Loads given filename and provides groups of lines that are separated in original files by empty line.
    """
```

## Type hints carry the weight of the contract

Since docstrings are sparse, Python type hints and Elixir `@spec`/`@type` are
how the user documents signatures. Do not skip them; see the language-specific
skills.

## Elixir typespecs

- Every struct has `@type t :: %__MODULE__{...}`, every function has
  a `@spec`, and persistent structs (that are to be serialised) get `@derive Jason.Encoder`.

## Lua documentation

- `--` line comments only. **No block comments `--[[ ]]`**.
- **No EmmyLua / `---@param` annotations** in user code.
- Moderate density: a comment per non-obvious method or block, none above
  trivial lines.

## Debug prints

The user uses `print(f'{var=}')` (Python), `inspect() |> IO.puts()` (Elixir),
`print(...)` (Lua) as lightweight debug channels. These are allowed during
development but must be removed before declaring a change complete, unless the
print is **intentional operator output** (e.g. CLI status, runner summaries).

```python
print(f'{coin=} – {buffer=}')
```

```elixir
{:misplaced_input, something} |> inspect() |> IO.puts()
```

## `# noqa` with human reason

If a linter rule has to be suppressed, add a short parenthetical explaining
why. No bare `# noqa` lines.

```python
except BaseException as ex:  # noqa: (wide catch)
    GLOBAL_EXIT_STACK.close()
    raise
```

## Commented-out code

Preserving one or two commented-out lines as notes is fine when they document
an alternative (e.g. "Run params" vs "Test params"), especially in AoC day
files. Do not leave hundreds of lines of disabled code - collapse to a comment
describing what was tried and why it was dropped.

## Personality is OK

The user has a soft spot for small personal touches: `# <3` in
`2025/6/main.ex`, conversational asides, and opinionated judgements. Don't
sterilise these when touching nearby code.

## Checklist

- [ ] Full sentences, capitalised, ending with a period.
- [ ] British spelling.
- [ ] Prefer "why" over "what".
- [ ] Use `–` (en-dash) where the user uses it nearby.
- [ ] Section headers for long functions, short and capitalised.
- [ ] ASCII diagrams for geometry or derivations when they help.
- [ ] No gratuitous docstrings. Let types carry the contract.
- [ ] No EmmyLua annotations in Lua user code.
- [ ] Debug `print` and `IO.puts` removed before done.
