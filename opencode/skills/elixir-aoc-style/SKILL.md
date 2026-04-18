---
name: elixir-aoc-style
description: Elixir idioms the user favours in the eaoc project - Main module per day, multi-clause tail-recursive helpers, binary-prefix pattern matching, {:ok, _} everywhere, ETS memoisation, no cond, tuple-keyed grids, @spec only in lib/. Load this before writing or reviewing any Elixir code in the eaoc project.
metadata:
  scope: language
  language: elixir
---

# Elixir style (eaoc)

Target: Elixir `~> 1.19`, compiled as an escript `aoc` binary. The `eaoc`
project lives at `/Users/malhavok/Coding/Elixir/eaoc/`.

Read **naming-conventions**, **control-flow-style**, **comments-style**, and
**testing-style** first. These are Elixir-specific additions.

## Project layout

```
eaoc/
├── .formatter.exs          # includes "**/*.ex" so per-day files are formatted
├── aoc                     # pre-built escript binary
├── lib/                    # framework only (runner, config, grid, point2d, ...)
├── test/                   # ExUnit tests for lib/ only
├── YEAR/DAY/
│   ├── main.ex             # defmodule Main do ... end - part1/1, part2/1
│   ├── input.txt
│   ├── test.txt
│   └── .config.json        # status + event log for this day
```

Days live **outside** `lib/` so the runner can `Code.compile_file` them
individually, call `Main.part1/1` or `Main.part2/1`, and then `:code.purge` /
`:code.delete` the module. All days define the module exactly as `Main`.

## Day file contract

```elixir
defmodule Main do
  def part1(input_data) do
    {:error, :notimplemented}
  end

  def part2(input_data) do
    {:error, :notimplemented}
  end
end
```

- Module is literally `Main`. Any auxiliary modules nest under it:
  `Main.Input`, `Main.Board`, `Main.Instruction`, `Main.Polyomino`.
- `part1/1` and `part2/1` take the raw binary input file contents.
- Both return `{:ok, answer}` or `{:error, reason}`. The runner handles
  printing and logging.

Scaffolding is done via `./aoc init [day] [year]`.

## Runner workflow

- `./aoc init [day] [year]` - scaffolds `YEAR/DAY/{main.ex,input.txt,test.txt,.config.json}`.
- `./aoc test` / `./aoc run` - compile and invoke `Main.partN/1` with
  `test.txt` or `input.txt` depending on `.config.json` status.
- `./aoc done` - mark status `:part1` → `:part2` → `:done`.
- `./aoc log` - dump the per-day event log.

Day files are not ExUnit-tested. The runner *is* the test loop.

## Multi-clause tail-recursive helpers

This is the dominant computation style. The public function seeds the
accumulator and the private multi-clause recursive helper consumes the list:

```elixir
def part1(input_data) do
    char_list = input_data |> String.trim() |> String.to_charlist()
    part1_counter(char_list, 0)
end

defp part1_counter([], acc), do: {:ok, acc}
defp part1_counter([?( | tail], acc), do: part1_counter(tail, acc + 1)
defp part1_counter([?) | tail], acc), do: part1_counter(tail, acc - 1)
```

Accumulate head-first (`[new | acc]`) and **reverse at the terminal clause**:

```elixir
defp merge_ranges([], acc), do: {:ok, Enum.reverse(acc)}
defp merge_ranges([range | tail], []), do: merge_ranges(tail, [range])
defp merge_ranges([{a1, b1} | tail], [{a2, b2} | acc_tail]) when a1 <= b2 + 1 do
    merge_ranges(tail, [{a2, max(b1, b2)} | acc_tail])
end
defp merge_ranges([range | tail], acc), do: merge_ranges(tail, [range | acc])
```

Use `Enum.reduce` only when you're collecting into a non-list (map, MapSet,
PriorityQueue). For list accumulation, pick the multi-clause recursion.

## `def` vs `defp`

Strict:

- `def` only for the module's public contract - `part1/1`, `part2/1`, struct
  ctors like `parse_line/1`, `new/2`.
- `defp` for every other helper inside a module.

If you see `def foo` on an internal helper in an older day file, match the
file - but new code should be strict about `defp`.

## Pattern matching in function heads

This is the user's signature move. Destructure aggressively and dispatch by
shape. Some patterns to imitate:

Binary prefixes:

```elixir
def parse_line("rect " <> params), do: ...
def parse_line("rotate column x=" <> params), do: ...
def parse_line("rotate row y=" <> params), do: ...
```

```elixir
defp parse_instruction("cpy " <> rest), do: ...
defp parse_instruction("inc " <> rest), do: ...
```

List shapes with mixed constraints:

```elixir
# [a, b, b, a] where a != b
def contains_abba?([a | [b, b, a | _]]) when b != a, do: true
def contains_abba?([_ | tail]), do: contains_abba?(tail)
def contains_abba?([]), do: false
```

Alias-while-matching:

```elixir
defp move_from_point({pos_x, pos_y} = point, direction, acc), do: ...
```

```elixir
def apply_operations([{input1, operation_type, input2, _result} = head | tail], state, pending), do: ...
```

Pinned for ETS lookups:

```elixir
case :ets.lookup(@cache, cache_key) do
  [{^cache_key, value}] -> value
  [] -> compute_and_insert(cache_key)
end
```

## Guards

Kept simple and mechanical. Stock guards: `length/1`, `==`, `!=`, `<`, `>`,
`rem/2`, `Integer.is_odd/1` (needs `require Integer`), binary length via `<>`
prefix.

```elixir
require Integer

def multiply_digits(digits) when Integer.is_odd(length(digits)), do: ...
```

```elixir
def is_valid_square?(x, y) when x < 0 or y < 0, do: false
```

```elixir
def dispatch(operations) when length(operations) == 5, do: ...
def dispatch(operations) when length(operations) == 2, do: ...
```

## No `cond`, rare `with`

- **`cond` is never used** in the whole repo. If you feel the urge, split into
  multi-clause functions with guards, or use `case`.
- `with` is used sparingly (3 times total), only for `Map.fetch` / `File.mkdir`
  happy-path chains:

```elixir
with {:ok, _} <- year(year),
     {:ok, :created} <- create_day(year, day) do
  {:ok, :created}
end
```

Prefer multiple `case` blocks otherwise.

## Pipelines

Start a pipeline with the input data, split, filter, map. **Do not use
`String.split("\n", trim: true)`** - the user writes `filter` + `String.length
> 0` explicitly:

```elixir
input_data
|> String.split("\n")
|> Enum.filter(fn line -> String.length(line) > 0 end)
|> Enum.map(fn line -> parse_line(line) end)
```

Function captures are idiomatic when the callback is just a call:

```elixir
|> Enum.map(&String.to_integer/1)
|> Enum.map(&parse_line/1)
```

## `{:ok, result}` everywhere

By convention, even helpers that cannot fail return `{:ok, result}`. Downstream
code matches it out immediately. This is so that `part1`/`part2` can always
propagate `{:ok, _}` / `{:error, _}`.

```elixir
def part1(input_data) do
    {:ok, parsed} = parse_input(input_data)
    {:ok, answer} = solve(parsed)
    {:ok, answer}
end
```

Return multi-element `{:ok, a, b, c}` rather than wrapping in a map when the
shape is well-known at the call site.

Pure predicates (`contains_abba?`, `is_valid?`) return plain booleans.

## Data structures

- **Grids are `%{{x, y} => char}` - tuple-keyed maps**, not structs. Use
  `Grid.init/1` from `lib/grid.ex`.
- **`Point2D` struct** is only for BFS / PriorityQueue arithmetic
  (`Point2D.add/2`, `Point2D.carinal/0` - yes, typo preserved: the function is
  literally `carinal` across the codebase).
- **Structs** for parsed rows and domain objects, nested under `Main` in day
  files:

```elixir
defmodule Main.Instruction do
  defstruct [:type, :param1, :param2]
end
```

- **MapSet** for point sets in grid problems.
- **PriorityQueue** (external dep) for BFS/Dijkstra.
- **Keyword lists**: essentially unused in application code.

## ETS caches

Named tables are the memoisation primitive. Module attribute holds the name,
`:ets.new` inside `part1`/`part2` (the module is purged between runs):

```elixir
defmodule Main do
  @cache :hash_cache

  def part1(input_data) do
    :ets.new(@cache, [:named_table, :set, :public])
    ...
  end

  defp cached_hash(key) do
    case :ets.lookup(@cache, key) do
      [{^key, value}] -> value
      [] ->
        value = compute_hash(key)
        :ets.insert(@cache, {key, value})
        value
    end
  end
end
```

## Atoms as tags and reasons

Use short `:snake_case` atoms: `:ok`, `:error`, `:notimplemented`, `:missing`,
`:duplicated_operation`, `:carry_chain_malformed`, `:valid`, `:invalid`,
`:alreadyexists`, `:exception`, `:created`.

## Default arguments

Write the default header first, then the real clauses:

```elixir
def handle(command, day_str \\ nil, year_str \\ nil)

def handle("init", day_str, year_str), do: ...
def handle("run", day_str, year_str), do: ...
```

## Parsing multi-section input

The canonical pattern for input with blank-line separators:

```elixir
defp parse_lines([], _mode, acc), do: {:ok, Enum.reverse(acc)}
defp parse_lines(["" | tail], _mode, acc), do: parse_lines(tail, :next, acc)
defp parse_lines([line | tail], :first, acc), do:
  parse_lines(tail, :first, [parse_first(line) | acc])
defp parse_lines([line | tail], :next, acc), do:
  parse_lines(tail, :next, [parse_next(line) | acc])
```

For single-value input, take the first line:

```elixir
input_data |> String.split("\n") |> Enum.at(0)
```

## Module attributes as constants

```elixir
@start_position 50
@total_numbers 100
@up Point2D.new(0, -1)
@down Point2D.new(0, 1)
@neighbours [{1, 1}, {1, -1}, {-1, 1}, {-1, -1}]
@cache :hash_cache
```

## Charlists and character literals

`String.to_charlist`, `?a`, `?-`, `?\s`, and the `~c"northpole object
storage"` sigil are all fair game. Use charlists when the problem is naturally
per-character.

## `lib/` vs day-file discipline

### In `lib/` (framework code)

- `@moduledoc` at least a sentence.
- Every struct: `@derive Jason.Encoder` (if persisted), `@type t :: %__MODULE__{...}`.
- Every function: `@spec`.
- `@typep` for private helper types.
- `defp` strictly. `def` only for the public API.
- ExUnit tests under `test/` with `describe "Module.fun/arity"`.

### In day files (`YEAR/DAY/main.ex`)

- **No `@moduledoc`, no `@doc`, no `@spec`** (unless the day genuinely
  warrants it - exceptions exist in 2025/12 and 2016/17).
- Comments carry the algorithmic explanation; big day-opening prose blocks
  are welcome (see 2016/15's CRT preface, 2025/12's SCIP solver preface).
- No ExUnit tests - the runner + `test.txt` is the check.

## Copy-paste between parts is OK

Part 2 being a copy of Part 1 with tweaks is intentional in this codebase.
The user rarely refactors to share. **Do not aggressively extract shared code
between `part1`/`part2` unless asked** - it often obscures the differences.

## Debug output

`inspect() |> IO.puts()` is the debug channel:

```elixir
{:misplaced_input, something} |> inspect() |> IO.puts()
```

Remove before declaring done.

## External solvers

For hard constraint problems (LP, SAT) the user shells out to SCIP / GLPSOL
via `System.cmd/2`, writing an `.lp` file, invoking the solver, parsing
stdout, deleting the files. If you see that pattern, match it - do not try to
re-implement the solver in Elixir.

## Testing

See **testing-style**. For Elixir specifically:

- `describe "Module.fun/arity"` blocks only.
- `setup` returns a map, destructured in each test's second arg.
- `assert {:ok, value} = fun(...)` - match, don't `==`.
- No doctests, no Mox, no property-based tests.
- No `async: true`.

## Summary checklist

- [ ] `defmodule Main` for day files, auxiliary modules nested under it.
- [ ] `part1/1` and `part2/1` return `{:ok, answer}` or `{:error, reason}`.
- [ ] Multi-clause tail-recursive private helpers; reverse accumulator on base.
- [ ] No `cond`, minimal `with`.
- [ ] Binary-prefix / list-shape pattern matching in function heads.
- [ ] Grids as `%{{x, y} => char}` tuple-keyed maps.
- [ ] ETS named tables for memoisation.
- [ ] Split with `String.split("\n") |> Enum.filter(fn line -> String.length(line) > 0 end)`.
- [ ] British English in names/comments; atoms in `:snake_case`.
- [ ] `@spec`/`@type` only in `lib/`, not in day files.
- [ ] Preserve the `Point2D.carinal/0` typo when touching that file.
