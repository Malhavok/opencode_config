---
name: python-style
description: Python-specific idioms the user favours - NamedTuple-first data modelling, PEP 604 unions, classmethod factories, make_* class factories, pathlib everywhere, strict absolute imports with trailing commas, dispatch dicts, explicit BFS queues, assert as validation. Load this before writing or reviewing any Python code.
metadata:
  scope: language
  language: python
---

# Python style

Target: **Python 3.10+** (PEP 604 unions, `X | Y`, `@cache`, match-free - the
user does not use `match`). No numpy / pandas / networkx / scipy unless seriously needed;
algorithms are rolled by hand on top of the standard library otherwise.

Read **naming-conventions**, **control-flow-style**, **comments-style**, and
**testing-style** before this. The rules below are Python additions, not
replacements.

## Type hints are mandatory

Every `def` - public or private, top-level or nested - is annotated. No bare
parameters. Return type annotated even for `-> None`.

```python
def does_calibration_work(calibration: Calibration, ops: list[Callable[[int, int], int]]) -> bool:
    ...
```

Use **PEP 604 syntax**: `int | None`, `str | int`. `Optional[X]` is tolerated
only in older code. Prefer the modern form in new code.

Common type imports kept at the top:

```python
from typing import (
    NamedTuple,
    Callable,
    Iterator,
    NewType,
    Literal,
    Annotated,
    Self,
)
```

## `NamedTuple` is the default data class

For lightweight immutable records - **reach for `NamedTuple` first**. The user
even explicitly chose it in some cases for performance and for free
`__eq__`/`__lt__`.

```python
class NumberPairs(NamedTuple):
    first: int
    second: int

    @classmethod
    def from_line(cls, line: str) -> 'NumberPairs':
        first_raw, second_raw = line.split('   ')
        return cls(int(first_raw), int(second_raw))
```

Overload operators on NamedTuples for vector-like types:

```python
class Tile2D(NamedTuple):
    x: int
    y: int

    def __add__(self, other: 'Tile2D') -> 'Tile2D':
        return Tile2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Tile2D') -> 'Tile2D':
        return Tile2D(self.x - other.x, self.y - other.y)

    def __neg__(self) -> 'Tile2D':
        return Tile2D(-self.x, -self.y)

    def __mul__(self, other: int) -> 'Tile2D':
        if not isinstance(other, int):
            raise ValueError('Only integer multiplication is allowed.')
        return Tile2D(self.x * other, self.y * other)

    def distance(self) -> int:
        return abs(self.x) + abs(self.y)

    @classmethod
    def from_line(cls, line: str, separator: str = ',') -> 'Tile2D':
        data = [int(elem.strip()) for elem in line.split(separator, maxsplit=1)]
        return cls(*data)
```

## When to reach for `@dataclass`

- Mutable state needs to be updated after construction.
- You need default values that aren't easily expressed inline.
- Hashing matters: use `@dataclass(frozen=True)`.

```python
@dataclasses.dataclass
class AoCConfig:
    last_year: int | None = None
    last_day: int | None = None
```

## `pydantic.BaseModel` for JSON

When the type has to round-trip through disk / network, use pydantic with
discriminated unions:

```python
class LogRunEntry(LogEntryBase):
    duration: datetime.timedelta
    input_file: str | None = None
    stop_reason: str | None = None
    result: str | int | None = None
    log_type: Literal['run'] = 'run'


class LogMarkEntry(LogEntryBase):
    is_done: bool = False
    log_type: Literal['mark'] = 'mark'


LOG_UNION = Annotated[
    Union[LogMarkEntry, LogRunEntry],
    Field(discriminator='log_type'),
]
```

## Enums

Mix in `str` or `int` so members compare naturally with raw inputs.

```python
class TaskPart(str, enum.Enum):
    PART_1 = 'part1'
    PART_2 = 'part2'


class Opcode(int, enum.Enum):
    ADV = 0  # Division of A vs 2 ^ combo, truncated to int, saved into A
    BXL = 1  # Bitwise XOR B vs literal, saved into B
    ...
```

Use comments to document semantics next to each member.

## The `make_*` class factory

Distinctive user pattern for generic/parametric containers. Function returns a
NamedTuple class parametrised by a field type:

```python
def make_grid(field_class: Type, field_ctor: Optional[Callable[[str], Type]] = None) -> Type[GridProtocol]:
    field_ctor = field_ctor or field_class

    class NewGrid(NamedTuple):
        tiles: dict[Tile2D, field_class]
        characters: defaultdict[field_class, set[Tile2D]]

        @classmethod
        def init(cls) -> 'NewGrid':
            return cls(dict(), defaultdict(set))

        @classmethod
        def from_lines(cls, lines: list[str]) -> 'NewGrid':
            grid = cls.init()
            for y_idx, line in enumerate(lines):
                for x_idx, character in enumerate(line):
                    tile = Tile2D(x_idx, y_idx)
                    grid.set_tile(tile, field_ctor(character))
            return grid
        # ...

    return cast(Type[GridProtocol], NewGrid)


Grid2D = make_grid(field_class=str)
```

Use this when you want a "template" over a type. Pair it with a `Protocol`-like
class full of `raise NotImplemented` stubs for IDE discoverability.

## Protocol-style classes

The user writes "protocol" bases as plain classes whose methods `raise
NotImplemented` (the sentinel - note: not `NotImplementedError`, that's a tic
to preserve when matching nearby style).

```python
class GridProtocol:
    tiles: dict[Tile2D, Any]

    @classmethod
    def init(cls) -> 'GridProtocol':
        raise NotImplemented

    @classmethod
    def from_lines(cls, lines: list[str]) -> 'GridProtocol':
        raise NotImplemented
```

For truly new abstract methods in new code, `raise NotImplementedError` (the
exception) is acceptable too - follow the file you're editing.

## Classmethod factories

`@classmethod` is heavily used for alternative constructors:

- `from_line`, `from_char`, `from_short`, `init`, `from_lines`
- Return type `-> 'ClassName'` with the self-string (no `Self` in older code;
  use `Self` from typing in new code).

```python
@classmethod
def from_line(cls, line: str) -> 'Calibration':
    left, right = line.split(': ')
    return cls(int(left), [int(elem) for elem in right.split(' ')])
```

## Default arguments

Prefer `None` as default and fill in inside the body:

```python
def run(year_number: int | None = None) -> None:
    year_number = year_number or config.last_year
    assert year_number is not None, f'No configuration found, thus year number needs to be provided'
```

Same pattern for containers:

```python
optional_ends = optional_ends or set()
field_ctor = field_ctor or field_class
```

Do not use mutable defaults. Never `def f(x=[]): ...`.

## Dispatch dicts

See control-flow-style. In Python:

```python
command_fun = {
    'year': year_command,
    'day': day_command,
    'run': run_command,
}[command]

command_fun(**command_kwargs)
```

Metaprogrammed:

```python
OPCODE_FUN: dict[Opcode, Callable[[int, Registers, list[int]], OpcodeResult]] = {
    opcode: globals()[f'apply_{opcode.name.lower()}']
    for opcode in Opcode
}
```

## Explicit loops over fancy comprehensions for algorithms

BFS / DFS / Dijkstra are written with an explicit `to_visit` list and
`while len(to_visit) > 0`. Use `list.pop(0)` for FIFO, `heapq` for priority.

```python
def get_shortest_path_with_distance(grid: Grid2D, start: Tile2D, end: Tile2D) -> dict[Tile2D, int]:
    to_visit = [(0, start)]
    final_path: dict[Tile2D, int] = {}

    while len(to_visit) > 0:
        distance, tile = heapq.heappop(to_visit)

        # It is said to be only one path, so no need to do anything fancier.
        final_path[tile] = distance
        if tile == end:
            break

        for direction in CARDINAL_DIRECTIONS:
            next_tile = tile + direction
            if grid.tiles.get(next_tile) != '.' or next_tile in final_path:
                continue

            heapq.heappush(to_visit, (distance + 1, next_tile))

    return final_path
```

**Do not** silently rewrite `while len(q) > 0` as `while q`. The explicit form
is the user's preferred idiom and reads as intent.

## List / dict comprehensions

Used freely, multi-line and aligned when wide:

```python
EQUIPMENT = [
    make_equip(equip_type, f'{level}', stack_depth=12)
    for level in [1, 2, 3]
    for equip_type in [
        'Coral', 'Fire', 'Thunder', 'Horn', 'Metal',
        'Crystal', 'Feather', 'Ice', 'Venom',
    ]
]
```

```python
reverse_mapping = {value: key for key, value in value_mapping.items()}
```

## Generators

Use `yield` only when streaming is the point (large iteration, early
termination).

## `next(iter(...))`

Idiomatic way to pull "any element" out of a set or dict the user already
knows is non-empty. Use it.

## `len(x) > 0` vs truthiness

The user consistently writes `len(x) > 0`, `len(x) == 0`. This is a style
tell. Prefer it over `if x:` / `if not x:` when the variable is clearly a
container.

## Walrus operator

Used occasionally for clarity in conditions:

```python
while (next_char := f.read(1)) != '\n':
    ...
```

Do not overuse it.

## Assertions as validation

`assert cond, f'...'` is the standard validation idiom - **both** in tests and
in production-like code:

```python
assert result.returncode == 0, f'Failed with:\n{result.stdout}\n{result.stderr}'
assert year_number is not None, f'No configuration found, thus year number needs to be provided'
assert self.grid.tiles.get(start + direction) == self.empty, f'Pointing at the wall.'
```

Yes, `assert` can be stripped by `-O`, but this is the user's style for
unexpected-state checks. Raise `ValueError` / `NotImplementedError` for
user-facing errors at public boundaries; use `assert` for invariants.

## Exceptions

- `raise ValueError(f'...')` for bad input at a public boundary.
- `raise NotImplementedError` for stubs (template files, unfinished branches).
- Custom base exceptions are small, empty classes named `FooError`:

```python
class MyModuleError(Exception):
    pass
```

- All module exceptions inherit the custom base exception, preferably adding
  flavour to them:

```python
class SpecificError(MyModuleError):
    def __init__(self, params):
        super.__init__(f'New message using {params}')
```

- Do not leak abstraction, prefer raising local exception to something generic.
- `try/except` is rare, exception are raised for unexpected cases.
- When it has to catch broadly, use `except Exception as ex:`
  (or `BaseException`) and **re-raise** after cleanup,
  with a `# noqa` and a reason:

```python
try:
    ...
except BaseException as ex:  # noqa: (wide catch)
    GLOBAL_EXIT_STACK.close()
    raise
```

## Input / files

**`pathlib.Path` everywhere.** Never `os.path`. Read text with
`filename.read_text().splitlines()`. Do not use `with open(...) as f:` for
simple text input.

```python
for elem in filename.read_text().splitlines():
    ...
```

Use `with open(...) as f` only when handling large files, streaming data etc.

- Ensure that you properly configure buffers if you do that.
- Still `pathlib.Path` for files, never raw strings.

## Entry point idiom

```python
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('toml_config', type=pathlib.Path)
    parser.add_argument('--wall_thickness', type=int, default=1)
    args = parser.parse_args()
    ...


if __name__ == '__main__':
    main()
```

- `argparse`, not `click`/`typer`.
- If args are files, type them with `pathlib.Path`.
- `--long_option_name` with underscores (matches the user's style; the
  argparse attr name stays `args.long_option_name`).

## Imports

Strict three groups, blank line between, absolute paths. Parenthesised
multi-name form with **trailing comma**:

```python
import enum
import heapq
import pathlib
from typing import (
    NamedTuple,
    NewType,
)

from tqdm import tqdm

from utils.grid2d import Grid2D
from utils.iterations import iterate_all_options
from utils.key_cache import (
    make_cache,
    EMPTY_CACHE,
)
from utils.tile2d import (
    Tile2D,
    Direction,
    DIRECTION_CHARACTER_MAP,
    CARDINAL_DIRECTIONS,
)
```

Alphabetical within each group. No relative imports outside `tests/` packages.

## Libraries reached for first

- stdlib: `pathlib`, `collections` (`defaultdict`, `Counter`, `deque`),
  `heapq`, `bisect`, `itertools`, `functools` (`@cache`, `reduce`),
  `contextlib`, `re` (compile at module top), `enum`, `dataclasses`,
  `typing`, `argparse`, `logging`, `importlib`.
- third-party: `pytest`, `pydantic`, `tqdm`, `timeout_decorator`, `numpy`,
  `pandas`, `scipy`, `networkx`, `requests`, `django`, `fastapi`, `tenacity`.

## Debug prints

`print(f'{var=}')` is the lightweight debug channel. Remove them before
declaring done, unless they're an intentional CLI status line.

## Summary checklist

- [ ] Every function / method typed, including `-> None`.
- [ ] PEP 604 union `X | None` in new code.
- [ ] `NamedTuple` unless there's a reason to use dataclass / pydantic.
- [ ] `@classmethod` factories (`from_line`, `init`) for parsers.
- [ ] Dispatch dicts instead of `if/elif` ladders.
- [ ] `pathlib.Path.read_text().splitlines()` for input.
- [ ] `assert cond, f'{var=}'` for invariants; `raise ValueError(...)` for
      user-facing errors.
- [ ] `len(x) > 0` / `len(x) == 0` consistently.
- [ ] Imports: three groups, parenthesised with trailing comma, alphabetical.
- [ ] British spelling in names and comments (`neighbour`, `colour`).
