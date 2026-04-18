---
name: control-flow-style
description: Universal control-flow idioms the user favours - guard clauses, early returns, dispatch tables, flat structure, accumulator recursion. Load this when writing any branching, loop, or state-machine code, or when reviewing a diff that has deep nesting or tangled if/else trees.
metadata:
  scope: universal
  languages: python,elixir,lua
---

# Control-flow style

The user strongly prefers **flat code**. Deep nesting is treated as a smell;
guard clauses, early returns, and dispatch-by-data are the tools that keep
things shallow.

## Guard clauses first

Any preconditions are checked at the top of the function as individual guards
that bail out fast. Do not collect them into a single `if` or nest them.

Python:

```python
# /Users/malhavok/Coding/Python/AdventOfCode/tasks/2024/day12/main.py:28-39
def build_island(grid: Grid2D, tile: Tile2D) -> set[Tile2D]:
    island = set()
    to_visit = [tile]
    island_character = grid.tiles[tile]

    while len(to_visit) > 0:
        current_tile = to_visit.pop(0)

        if current_tile in island:
            continue
        island.add(current_tile)

        for neighbour in CARDINAL_DIRECTIONS:
            new_tile = current_tile + neighbour
            if grid.tiles.get(new_tile) != island_character:
                continue
            to_visit.append(new_tile)

    return island
```

Lua - notice how several single-line guards run one after the other:

```lua
-- src/tiles/matcher.lua
function Matcher:setCursorPosition(x_pos, y_pos)
    local new_tile = board:getTileAtPosition(x_pos, y_pos)
    if new_tile == self.current_tile then
        return
    end

    if self.current_tile ~= nil then
        self.current_tile:diminish()
    end

    self.current_tile = new_tile

    if self.current_tile == nil then
        return
    end
    self.current_tile:highlight()

    if not self.is_selecting then
        return
    end
    -- ...
end
```

## Multi-line boolean conditions get their own layout

When a condition spans multiple expressions, put operators on their own lines:

```lua
if
    self.rules:canAddTile(self.selected_tiles_names, neighbour_tile.name)
    and
    not self.selected_tiles_set[neighbour_tile]
then
```

Python - use parentheses and hang continuations:

```python
if (
    self.rules.can_add_tile(self.selected_tiles_names, neighbour_tile.name)
    and neighbour_tile not in self.selected_tiles_set
):
    ...
```

## Dispatch by data, not by `if/elif` chain

When the branching selects among N similar operations, build a mapping from the
discriminator to a handler and index into it. Avoid ladders of `elif`.

```python
# /Users/malhavok/Coding/Python/AdventOfCode/aoc.py
command_fun = {
    'year': year_command,
    'day': day_command,
    'run': run_command,
    'logs': logs_command,
    'mark': mark_command,
    'current': current_command,
}[command]

command_fun(**command_kwargs)
```

Even better - derive the mapping metaprogrammatically when the names are
regular:

```python
# /Users/malhavok/Coding/Python/AdventOfCode/tasks/2024/day17/main.py
OPCODE_FUN: dict[Opcode, Callable[[int, Registers, list[int]], OpcodeResult]] = {
    opcode: globals()[f'apply_{opcode.name.lower()}']
    for opcode in Opcode
}
```

```python
PYTHON_OPERATION = {Operation.AND: '&', Operation.OR: '|', Operation.XOR: '^'}
```

Elixir's equivalent is **multi-clause functions on atoms / binary prefixes** -
see elixir-aoc-style skill.

## No `cond`, rarely `switch`

- Elixir: the user **never writes `cond`**. Either build multi-clause functions
  with guards, or use `case`. This is a hard rule in this codebase.
- Python: no `match` / `case` statements found in the corpus. Dispatch dict is
  preferred.
- Lua: no dispatch tables in the current Love2D code, but also no long
  `elseif` chains.

## Early returns over `else`

Prefer returning from the happy-path guards rather than wrapping the rest of
the function in `else`.

Bad:

```python
def handle(user):
    if user is not None:
        if user.active:
            return do_work(user)
        else:
            return None
    else:
        return None
```

Good:

```python
def handle(user: User | None) -> Result | None:
    if user is None:
        return None
    if not user.active:
        return None
    return do_work(user)
```

## Loops

- **Explicit queue + `while len(q) > 0`** is the default BFS/DFS scaffold in
  Python, not `deque` or generators. Use `heapq` for priority searches.
- **Tail-recursive multi-clause helpers with an accumulator** are the default
  in Elixir, and the accumulator is reversed at the terminal clause rather
  than prepended in order.
- Lua uses `for x_idx = 1, count do` / nested `for y_idx = 1, count do` for
  grids. `ipairs` for arrays, `pairs` for set-like tables.

Accumulator pattern in Elixir:

```elixir
def merge_ranges([], acc), do: {:ok, Enum.reverse(acc)}
def merge_ranges([range | tail], []), do: merge_ranges(tail, [range])
def merge_ranges([{a1, b1} | tail], [{a2, b2} | acc_tail]) when a1 <= b2 + 1 do
    merge_ranges(tail, [{a2, max(b1, b2)} | acc_tail])
end
def merge_ranges([range | tail], acc), do: merge_ranges(tail, [range | acc])
```

## `for/else` for "didn't find it" idiom (Python)

Used deliberately when the search has a natural sentinel:

```python
for idx in range(len(indices)):
    indices[idx] += 1
    if indices[idx] < len(options[idx]):
        break
    indices[idx] = 0
else:
    # We've iterated everything.
    break
```

Comment the `else` clause when the semantics aren't obvious.

## Callbacks are optional and nullable

When a function takes an optional callback:

- Put it **last** in the argument list.
- Allow `None` / `nil`.
- Guard before calling: `if callback is not None: callback()`.

Lua (every tween method in `src/tweens/`):

```lua
function ICanBounce:show(callback)
    if self.scale_tween ~= nil then
        Timer.cancel(self.scale_tween)
    end

    self.tweened_scale = 0.0
    self.scale_tween = Timer.tween(0.3, self, { tweened_scale = 1.0 }, 'out-elastic', callback)
end
```

## Cancel-then-start idiom

Any long-running effect that can be triggered twice (tween, debounced timer,
in-flight task) must cancel the previous one before starting a new one. The
user copies this pattern rather than extracting a helper - do the same unless
asked to refactor it.

## State flags on `self`

For UI / interaction flags, store them on the object (no getter methods) and
have external code read them directly: `tile.is_active`,
`tile.is_highlighted`, `is_selecting`. Only add a getter when derivation is
non-trivial.

## `while True:` is fine

For iteration with an internal sentinel. Do not contort it into a `do while`
simulation.

```python
while True:
    step = compute_next()
    if step is None:
        break
    apply(step)
```

## Infinite recursion is fine when it's truly tail

In Elixir a multi-clause tail-recursive function is idiomatic for arbitrary
input sizes. Don't translate it to `while` manually.

## Summary checklist

Before finishing a change, re-read it and verify:

- [ ] No `if` nested more than two levels deep.
- [ ] Preconditions handled as early-return guards at the top.
- [ ] No `cond` in Elixir. No long `elif` ladder in Python/Lua.
- [ ] Branching over N similar cases uses a dispatch map.
- [ ] Callbacks are optional, last, and guarded.
- [ ] Effectful "retrigger" code cancels the previous effect first.
