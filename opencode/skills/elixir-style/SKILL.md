---
name: elixir-style
description: Elixir idioms the user favours - multi-clause tail-recursive helpers with accumulator + reverse, aggressive pattern matching in function heads (binary prefix, list shape, pinned vars), {:ok, _} contract returns, strict def vs defp discipline, ETS for memoisation, no cond, typespecs on public APIs, tuple-keyed maps for grids, atoms as tags. Load this before writing or reviewing any Elixir code.
metadata:
  scope: language
  language: elixir
---

# Elixir style

Read **naming-conventions**, **control-flow-style**, **comments-style**, and
**testing-style** first. These are Elixir-specific additions.

## Multi-clause tail-recursive helpers

The dominant computation style. A public function seeds the accumulator and
a private multi-clause recursive helper consumes the list, dispatching by
shape in function heads:

```elixir
def count_balance(input) do
    char_list = input |> String.trim() |> String.to_charlist()
    count_balance(char_list, 0)
end

defp count_balance([], acc), do: {:ok, acc}
defp count_balance([?( | tail], acc), do: count_balance(tail, acc + 1)
defp count_balance([?) | tail], acc), do: count_balance(tail, acc - 1)
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

Use `Enum.reduce` when collecting into a non-list (map, MapSet,
PriorityQueue). For list accumulation, reach for multi-clause recursion.

## `def` vs `defp`

Strict:

- `def` only for the module's public contract - entry points, struct ctors
  like `parse_line/1`, `new/2`, protocol implementations.
- `defp` for every internal helper.

Treat `defp` as the default. Flip to `def` only when an external caller
legitimately needs the function.

## Pattern matching in function heads

The user's signature move. Destructure aggressively and dispatch by shape
instead of branching inside the body.

Binary prefixes:

```elixir
def parse_line("rect " <> params), do: parse_rect(params)
def parse_line("rotate column x=" <> params), do: parse_rotate_column(params)
def parse_line("rotate row y=" <> params), do: parse_rotate_row(params)
```

```elixir
defp parse_instruction("cpy " <> rest), do: build_copy(rest)
defp parse_instruction("inc " <> rest), do: build_increment(rest)
```

List shapes with mixed constraints:

```elixir
# [a, b, b, a] where a != b
def contains_abba?([a | [b, b, a | _]]) when b != a, do: true
def contains_abba?([_ | tail]), do: contains_abba?(tail)
def contains_abba?([]), do: false
```

Alias-while-matching (`=`) to keep both the whole and the parts:

```elixir
defp move_from_point({pos_x, pos_y} = point, direction, acc), do: ...
```

```elixir
def apply_operations([{input1, operation_type, input2, _result} = head | tail], state, pending), do: ...
```

Pinned variables for equality matching (e.g. ETS lookups):

```elixir
case :ets.lookup(@cache, cache_key) do
  [{^cache_key, value}] -> value
  [] -> compute_and_insert(cache_key)
end
```

## Guards

Kept simple and mechanical. Reach for: `length/1`, `==`, `!=`, `<`, `>`,
`rem/2`, `Integer.is_odd/1` (needs `require Integer`), binary `<>` prefix.

```elixir
require Integer

def multiply_digits(digits) when Integer.is_odd(length(digits)), do: ...
```

```elixir
def is_valid_square?(x, y) when x < 0 or y < 0, do: false
```

Dispatch by list length:

```elixir
def dispatch(operations) when length(operations) == 5, do: ...
def dispatch(operations) when length(operations) == 2, do: ...
```

## No `cond`, rare `with`

- **Do not use `cond`.** If you feel the urge, split into multi-clause
  functions with guards, or use `case`.
- `with` is used sparingly, only for happy-path chains over `{:ok, _}` /
  `{:error, _}` (typically `Map.fetch`, `File.mkdir`, parser compositions):

```elixir
with {:ok, raw} <- File.read(path),
     {:ok, decoded} <- Jason.decode(raw),
     {:ok, value} <- Map.fetch(decoded, "value") do
  {:ok, value}
end
```

Prefer multiple `case` blocks otherwise.

## Pipelines

Start a pipeline with the input, then split, filter, map.

```elixir
input
|> String.split("\n", trim: true)
|> Enum.map(fn line -> parse_line(line) end)
```

Function captures when the callback is just a call:

```elixir
|> Enum.map(&String.to_integer/1)
|> Enum.map(&parse_line/1)
```

Single-step pipes are tolerated when they read better than a nested call:
`raw |> String.to_charlist()`.

## `{:ok, result}` / `{:error, reason}` as the default contract

Even helpers that cannot fail return `{:ok, result}` by convention, so that
callers can propagate `{:ok, _}` uniformly and slot a new failure mode in
later without breaking the call site:

```elixir
def run(input) do
    {:ok, parsed} = parse(input)
    {:ok, answer} = solve(parsed)
    {:ok, answer}
end
```

or

```elixir
def run(input) do
    {:ok, parsed} = parse(input)
    {:ok, _answer} = solve(parsed)
end
```

Return multi-element `{:ok, a, b, c}` when the shape is well known at the
call site rather than wrapping in a map.

Pure predicates (`contains_abba?`, `is_valid?`) return plain booleans.

Keep error reasons as atoms: `{:error, :not_found}`, `{:error, :invalid}`.
Only introduce a struct or tuple-with-payload when the caller genuinely
needs the extra data.

## Data structures

- **Structs** for domain objects. Always give the struct a
  `@type t :: %__MODULE__{...}`:

```elixir
defmodule Instruction do
  @enforce_keys [:type]
  defstruct [:type, :param1, :param2]

  @type t :: %__MODULE__{
    type: atom(),
    param1: any(),
    param2: any(),
  }
end
```

- **MapSet** for set semantics (membership, union, difference).
- **PriorityQueue** (external dep) for Dijkstra / A*.
- **Tuples** as lightweight tagged values: `{:value, v}` vs `{:register, name}`,
  instruction ASTs like `{:cpy, {:value, 5}, "a"}`. Match on the tag.
- **Keyword lists**: only for option bags (`opts \\ []`) and library APIs
  that require them. Not for data modelling.

## ETS for memoisation

Named ETS tables are the default memoisation primitive. Hold the name in a
module attribute, create the table once at the entry point, then lookup /
insert inside the recursion:

```elixir
defmodule Hasher do
  @cache :hash_cache

  def run(inputs) do
    :ets.new(@cache, [:named_table, :set, :public])
    Enum.map(inputs, &cached_hash/1)
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

Use `:public` access for write-from-tasks, `:protected` otherwise.

## Atoms as tags and reasons

Use short `:snake_case` atoms: `:ok`, `:error`, `:not_implemented`,
`:missing`, `:invalid`, `:duplicated`, `:created`. They are the
Elixir-native way to express "which case" and should be matched on, not
compared as strings.

## Default arguments

Write the default header first, then the real clauses. Do not put defaults
on every clause:

```elixir
def handle(command, arg1 \\ nil, arg2 \\ nil)

def handle("init", arg1, arg2), do: ...
def handle("run", arg1, arg2), do: ...
```

## Module attributes as constants

```elixir
@max_iterations 1_000_000
@default_timeout 5_000
@up Point2D.new(0, -1)
@down Point2D.new(0, 1)
@neighbours [{1, 1}, {1, -1}, {-1, 1}, {-1, -1}]
@cache :hash_cache
```

Use module attributes for magic numbers, fixed direction sets, table names,
file paths, and anything else you'd write `UPPER_SNAKE_CASE` for in another
language.

## Charlists and character literals

`String.to_charlist`, `?a`, `?-`, `?\s`, and the `~c"text"` sigil are fair
game. Reach for charlists when the problem is naturally per-character and
you'll be matching on `?(`, `?)`, `?\s` in function heads.

## Parsing multi-section input

When a blob contains blank-line separated sections, recurse with a `mode`
accumulator that flips on `""`:

```elixir
defp parse_lines([], _mode, acc), do: {:ok, Enum.reverse(acc)}
defp parse_lines(["" | tail], _mode, acc), do: parse_lines(tail, :next, acc)
defp parse_lines([line | tail], :first, acc), do:
  parse_lines(tail, :first, [parse_first(line) | acc])
defp parse_lines([line | tail], :next, acc), do:
  parse_lines(tail, :next, [parse_next(line) | acc])
```

## Documentation discipline

Scale the doc weight with the module's audience.

### Published / library modules (others call this)

- `@moduledoc` at least a sentence describing what and why.
- Every struct: `@type t :: %__MODULE__{...}`. Add `@derive Jason.Encoder`
  if the struct is persisted / serialised.
- Every function in the public API: `@spec`.
- `@typep` for private helper types used across several functions.
- `@doc` on every public function, even a single sentence.

### Internal / application modules

- `@moduledoc false` is fine when the module is an internal detail.
- Typespecs optional - skip them when they obscure more than they explain.
- Comments carry the algorithmic explanation (see **comments-style** for the
  prose format).

If you're unsure whether a module is "published", err on the side of
writing a `@spec` and `@type t`.

## Debug output

`inspect() |> IO.puts()` is the debug channel:

```elixir
{:misplaced_input, something} |> inspect() |> IO.puts()
```

Remove before declaring done, unless the print is an intentional CLI status
line.

## Shelling out

When a problem is best solved by an external tool, shell out with
`System.cmd/2`, write any required files to a temp location, parse the
stdout, and clean up. Do not port the external tool to Elixir just to avoid
the shell dependency.

## Testing

See **testing-style**. For Elixir specifically:

- `describe "Module.fun/arity"` blocks only - always named with the
  function reference.
- `setup` returns a map, destructured in each test's second arg.
- `assert {:ok, value} = fun(...)` - match, don't `==`.
- No doctests, no Mox, no property-based tests by default.
- No `async: true` unless you have a reason.

## Summary checklist

- [ ] Multi-clause tail-recursive private helpers; reverse accumulator on
  base case.
- [ ] `defp` for everything internal; `def` only for the public contract.
- [ ] Pattern-match in function heads: binary prefixes, list shapes,
  alias-while-matching, pinned vars.
- [ ] No `cond`. `with` only for `{:ok, _}` chains.
- [ ] Return `{:ok, result}` / `{:error, atom}` from anything that could
  plausibly fail in the future.
- [ ] Tuple-keyed maps for grids; structs with `@type t` for domain rows;
  MapSet for sets; atoms for tags.
- [ ] ETS named tables for memoisation.
- [ ] Module attributes for constants and table names.
- [ ] British English in names / comments; atoms in `:snake_case`.
- [ ] Typespecs and `@moduledoc` on published modules, relaxed for
  internal-only modules.
