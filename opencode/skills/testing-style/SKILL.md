---
name: testing-style
description: Universal testing style for the user - pytest parametrize, bare asserts with f-string messages inside unittest, ExUnit describe blocks matching "Module.fun/arity", fixture shapes, what NOT to test. Load this when writing or editing tests, or before adding a new test file.
metadata:
  scope: universal
  languages: python,elixir
---

# Testing style

The user tests pragmatically - thoroughly where it pays off, almost not at all
for throwaway solvers and tweens. Match the project's existing testing stance
before adding anything.

## Decide first: should there be a test here?

Write tests for:

- Reusable library code (`utils/` in Python, `lib/` in Elixir).
- Business rules, parsing, validation, scoring.
- Non-trivial algorithms (graph walks, memoisation, DP transitions).
- Edge cases and known-regression bugs.

Do **not** write tests for:

- One-off scripts / AoC day solutions (Elixir verifies them with
  `./aoc test` running against `test.txt`, not ExUnit).
- Framework internals, third-party libraries, trivial getters/setters.
- Love2D scene / tween code (no tests in the corpus - do not invent a
  framework without asking).

## Python: hybrid unittest + bare assert

Competitive / HackerRank scripts use `unittest.TestCase` as the runner but
**bare `assert` with an f-string message**, not `self.assertEqual`. This is the
user's signature style.

```python
# /Users/malhavok/Coding/Python/LegoBlocks/tests.py
class Tests(unittest.TestCase):
    def test_1(self) -> None:
        result = lego_blocks(2, 2)
        assert result == 3, f'{result=}'

    def test_2(self) -> None:
        result = lego_blocks(2, 3)
        assert result == 7, f'{result=}'

    @timeout_decorator.timeout(3)
    def test_5(self) -> None:
        result = lego_blocks(4, 5)
        assert result == 35714, f'{result=}'
```

Use `f'{result=}'` (walrus-like self-documenting format) as the failure
message. For multiple comparisons use an explicit format with named variables:

```python
assert result == expected, f'{params[:2]=}, {len(params[2])=}, {result=}, {expected=}'
```

For loops that should each assert, use `subTest`:

```python
def test_1(self) -> None:
    for entry in [(1, 1), (1, 4), (4, 1), (4, 4)]:
        with self.subTest(f'{entry=}'):
            result = queens_attack(4, entry, [])
            assert result == 9, f'{result=}'
```

## Python: pytest for framework tests

Framework / library tests (e.g. `AdventOfCode/tests/test_*.py`) use **pytest**
with parametrize and fixtures. Always type-annotate parameters and return
`-> None`.

Parametrize layout:

```python
@pytest.mark.parametrize(
    ['input_data', 'expected_outputs'],
    [
        (
            [['A', 'B'], ['C', 'D'], ['E', 'F']],
            {'ACE', 'ACF', 'ADE', 'ADF', 'BCE', 'BCF', 'BDE', 'BDF'},
        ),
        (
            [['A'], ['B'], ['C']],
            {'ABC'},
        ),
    ],
)
def test_iterations(input_data: list[list[str]], expected_outputs: set[str]) -> None:
    all_results = set()
    for result in iterate_all_options(input_data):
        str_result = ''.join(result)
        all_results.add(str_result)
    assert all_results == expected_outputs
```

- Column names as a list: `['input_data', 'expected_outputs']`.
- Each row is a tuple. Trailing comma inside the list.
- Long-form tuple rows get multi-line bodies, aligned.

Fixtures are small, direct, and typed:

```python
@pytest.fixture
def labyrinth() -> Labyrinth:
    grid = Grid2D.from_lines(TEST_INPUT.splitlines())
    labyrinth = Labyrinth(grid, wall='#', empty='.')
    return labyrinth
```

`pytest.raises` for expected exceptions:

```python
with pytest.raises(ValueError):
    labyrinth.go_until_crossroads_or_end(Tile2D(-1, -1), DIRECTION_UP)
```

## Python: filename-encoded expected result

For cases with many test fixtures on disk, encode the expected answer in the
filename (`testN__<expected>.txt`) and parse it in `_load_case`:

```python
@classmethod
def _load_case(cls, filename: str) -> tuple[list[int], int, int]:
    expected_result = int(filename.split('__')[1].split('.')[0])
    ...
```

This is a distinctive user pattern - keep using it for data-driven cases.

## Elixir: ExUnit describe blocks

Day solutions are **not** ExUnit-tested. Only `lib/` modules get tests under
`test/`. Structure:

```elixir
defmodule GridTest do
  use ExUnit.Case

  describe "Grid.init/1" do
    test "returns an empty map for empty input" do
      assert {:ok, map} = Grid.init("")
      assert map == %{}
    end

    test "parses a 2x2 grid" do
      content = "AB\nCD"
      assert {:ok, map} = Grid.init(content)
      assert map == %{{0, 0} => ?A, {1, 0} => ?B, {0, 1} => ?C, {1, 1} => ?D}
    end
  end

  describe "Grid.get_neighbours/3" do
    setup do
      {:ok, map} = Grid.init("ABC\nDEF\nGHI")
      %{map: map}
    end

    test "returns 4 cardinal neighbours by default", %{map: map} do
      neighbours = Grid.get_neighbours(map, {1, 1})
      assert {{0, 1}, ?D} in neighbours
    end
  end
end
```

Rules:

- `describe` blocks are always named `"Module.fun/arity"`, never a free-form
  description.
- `setup` blocks return `%{key: value}` and the test destructures the second
  argument: `test "...", %{map: map} do`.
- No `async: true` in this codebase. Leave it off unless you have a reason.
- **No doctests** (`doctest Module`) are used. Don't add them.
- Assert on the `{:ok, value}` shape first, then on the content:
  `assert {:ok, value} = fun(...)` (using `=` match, not `==`).
- No Mox, no ExUnitProperties, no fixtures on disk - tests use small literal
  inputs built inline.

## What makes a good assertion

- Assert the contract first (`{:ok, _}` vs `{:error, _}` in Elixir, return
  type / exception in Python).
- Then assert the value.
- Include enough context in failure messages that a failing test tells you
  *what* went wrong without `pdb`:

```python
assert path == expected_tiles, f'Got {path=} vs {expected_tiles=}'
```

## Timeouts for pathological inputs

If a HackerRank-style test should fail loudly on a regression causing
exponential blowup, use `@timeout_decorator.timeout(<seconds>)`:

```python
@timeout_decorator.timeout(3)
def test_5(self) -> None:
    result = lego_blocks(4, 5)
    assert result == 35714, f'{result=}'
```

## Test-first discipline

When implementing new library code under direction, follow test-first:

1. Write the failing test with a specific expected value.
2. Run it and confirm it fails for the right reason.
3. Write the minimum code to pass.
4. Refactor while keeping it green.

After fixing a bug add a regression test so the same failure cannot come back
silently.

## Run commands cheatsheet

- Python pytest: `pytest tests/` or `pytest tests/test_grid2d.py`.
- Python unittest: `python -m unittest` from the project root, or run
  `python tests.py` directly (the user's scripts typically have
  `if __name__ == '__main__': unittest.main()`).
- Elixir: `mix test` from `/Users/malhavok/Coding/Elixir/eaoc/`.

Verify before declaring done.
