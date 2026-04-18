---
name: love2d-style
description: Lua / Love2D style from PuzzleBruiser - hump.class OOP, ICan<Verb> mixins, PascalCase modules with snake_case fields, camelCase methods, callback-last nullable callbacks, cancel-then-start tween idiom, dot-separated requires, WorldScaler for resolution-independent rendering, hump.gamestate scenes. Load this before writing or reviewing any Lua code for the PuzzleBruiser project.
metadata:
  scope: language
  language: lua
  framework: love2d
---

# Love2D / Lua style (PuzzleBruiser)

Target: Love2D 11.x, using **hump** (class, timer, gamestate, vector) from
`libs/hump/`. Project lives at
`/Users/malhavok/Coding/Love2D/PuzzleBruiser/`.

Read **naming-conventions**, **control-flow-style**, and **comments-style**
first. These are Lua / Love2D additions.

## Project layout

```
PuzzleBruiser/
├── main.lua                # love.load, love.keypressed, love.update only
├── env.lua                 # `love = require("api.love")` for LSP; not required by main
├── tests.lua               # scratchpad demo; NOT wired into the game
├── run.sh                  # /Applications/love.app/.../love . --console
├── api/                    # LÖVE API type stubs for LSP (don't require from src/)
├── libs/                   # submodules: hump (used), suit and knife (unused)
├── resources/              # fonts/, images/, sounds/
└── src/
    ├── core/               # texture_atlas.lua, world_scaler.lua
    ├── scenes/             # game.lua
    ├── tiles/              # tile.lua, board.lua, matcher.lua, hit.lua, rules/
    └── tweens/             # i_can_bounce.lua, i_can_shake.lua, i_can_wiggle.lua
```

- Directory names are **purpose-based** (`core`, `scenes`, `tiles`, `tweens`),
  not type-based.
- Rules are their own subfolder (`src/tiles/rules/`) implying pluggable match
  rules.
- Files are always `snake_case.lua` even when the module inside is PascalCase.

## Requires

Dot-separated paths. Always prefix with `libs.` or `src.`. Never `./` or `/`.
Group external / internal with a blank line:

```lua
local Class = require('libs.hump.class')
local WorldScaler = require('src.core.world_scaler')

local ICanBounce = require('src.tweens.i_can_bounce')
local ICanShake = require('src.tweens.i_can_shake')
local ICanWiggle = require('src.tweens.i_can_wiggle')
```

One require per line. `local` is mandatory.

## Module shape: hump.class

The dominant style. Every file under `src/tiles/` and `src/tweens/`, plus
`src/core/texture_atlas.lua`, looks like:

```lua
local Class = require('libs.hump.class')

local Hit = Class {}

function Hit:init(tile_names, is_valid)
    self.tile_names = tile_names
    self.is_valid = is_valid
end

function Hit:getLength()
    return #self.tile_names
end

return Hit
```

- `local ClassName = Class {}` - PascalCase module variable.
- `:init(...)` for construction (hump's convention).
- Methods defined with `function Class:method(args)`.
- Last line is always `return ClassName`.

## Mixins: `__includes`

The user uses hump's `__includes` for trait-like mixins. Each trait file
follows the `ICan<Verb>` naming:

```lua
local Tile = Class { __includes = { ICanBounce, ICanShake, ICanWiggle } }

function Tile:init(name, image, quad)
    ICanBounce.init(self)
    ICanShake.init(self)
    ICanWiggle.init(self)
    ...
end
```

**Explicitly call each parent `.init(self)`** - do not rely on a super chain.

Each `ICan<Verb>` module owns *one aspect* of visual state:

- `ICanBounce` owns `tweened_scale` and the `scale_tween` handle.
- `ICanShake` owns rotation perturbation and `rotation_tween`.
- `ICanWiggle` owns position offset and `wiggle_tween`.

The consumer (`Tile`) reads them directly: `self.tweened_scale`,
`self.tweened_rotation`, `self.tweened_position`.

## Singleton table modules

For scope-less services (no instances needed) use a plain table:

```lua
local WorldScaler = {
    num_y_tiles = 11,
    pixels_per_tile = nil,
    num_x_tiles = nil,
}

function WorldScaler:update()
    local screen_width, screen_height = love.window.getMode()
    self.pixels_per_tile = screen_height / self.num_y_tiles
    self.num_x_tiles = math.floor(screen_width / self.pixels_per_tile)
end

function WorldScaler:getQuadScale(quad)
    local _, _, width, _ = quad:getViewport()
    return self.pixels_per_tile / width
end

return WorldScaler
```

Scenes (hump.gamestate) use the same shape - `scene = {}` with `:enter`,
`:update(dt)`, `:draw`.

## Method visibility

- **Public methods**: `camelCase` - `addMatchChangedCallback`, `bounceUp`,
  `canAddTile`, `isValidChain`, `splitIntoHits`.
- **Private methods**: leading `_` + camelCase - `_spawnTiles`,
  `_tileToPosition`, `_positionToTile`, `_buildAllowedTiles`,
  `_callMatchChangedCallback`, `_makeHit`.

Fields are `snake_case`: `self.tile_positions`, `self.is_active`,
`self.selected_tiles`, `self.tweened_scale`.

## `self.field` vs globals in scenes

The scene (`src/scenes/game.lua`) intentionally assigns key objects
**without `local`** in `:enter`, making them scene-level globals:

```lua
function scene:enter()
    board = Board(generator, 6, 6)
    matcher = Matcher(board, rule_same_colour)
    ...
end
```

Other modules then read the global `board` directly. If you're editing
something inside the scene, **keep this pattern**: don't sprinkle `local`
unless the whole scene is being refactored. If you're editing outside the
scene, **use `self.<field>` where possible**, but this is fine to access the
scene globals as an ambient context.

## Control flow: guards first

See **control-flow-style**. Lua-specific examples:

```lua
function Tile:highlight(callback)
    if not self.is_active then
        return
    end

    self.is_highlighted = true
    self:bounceUp(callback)
end
```

Multi-line booleans with standalone connectors:

```lua
if
    self.rules:canAddTile(self.selected_tiles_names, neighbour_tile.name)
    and
    not self.selected_tiles_set[neighbour_tile]
then
    ...
end
```

## Callbacks: optional, last, nullable

Every tween method / state transition accepts an optional `callback` last:

```lua
function ICanBounce:show(callback)
    if self.scale_tween ~= nil then
        Timer.cancel(self.scale_tween)
    end

    self.tweened_scale = 0.0
    self.scale_tween = Timer.tween(0.3, self, { tweened_scale = 1.0 }, 'out-elastic', callback)
end
```

Consumers guard it: `if callback ~= nil then callback() end`.

## Cancel-then-start tween idiom

Every tween method starts with the same 3 lines. The user **copies this
pattern** rather than extracting a helper. When editing, match the style:

```lua
if self.scale_tween ~= nil then
    Timer.cancel(self.scale_tween)
end

self.tweened_scale = 0.0
self.scale_tween = Timer.tween(0.3, self, { tweened_scale = 1.0 }, 'out-elastic', callback)
```

## Named local closures inside methods

When a callback closes over locals, define it as a `local function` inside
the method - don't inline it if it spans more than a couple of lines:

```lua
function Board:removeTile(tile)
    local tile_position = self.tile_positions[tile]
    if tile_position == nil then
        return
    end

    local tile_key = tostring(tile_position)

    local function replace()
        self.tile_positions[tile] = nil

        local new_tile = self.generator:getTile()
        new_tile:appear()

        self.tile_positions[new_tile] = tile_position
        self.tiles[tile_key] = new_tile
    end

    tile:disappear(replace)
end
```

Anonymous inline functions are only used for trivial Timer callbacks:

```lua
self.rotation_tween = Timer.every(
    0.05,
    function()
        self.tweened_rotation = love.math.random() * math.pi / 3 - math.pi / 6
    end
)
```

## Data structures

- **Arrays**: 1-indexed, built via `table.insert(t, v)`.
- **Sets**: `t[key] = true`, membership via `if t[key]`, clear with `self.foo
  = {}`.
- **Parallel containers** for different access patterns: `selected_tiles`
  (array, order), `selected_tiles_names` (parallel array of names),
  `selected_tiles_set` (O(1) membership).
- **Bidirectional maps** when needed: `tiles` (key → tile) and
  `tile_positions` (tile → vector).
- **`tostring(vector)` as key** for string-keyed tables holding vector
  positions:

```lua
local tile_position = Vector(x_idx, y_idx)
local tile_key = tostring(tile_position)
...
self.tiles[tile_key] = new_tile
```

- **`rawget(self.tiles, tile_key)`** when `__index` might lie (hump.class
  instances).

## Constants at module top

A `local` table at the top of the file. No SCREAMING_CASE:

```lua
local neighbours = {
    Vector(0, -1),
    Vector(0,  1),
    Vector(-1, 0),
    Vector( 1, 0),
}
```

## hump.vector

Vectors are added with `+` (operator overloaded). Common calls:
`Vector(x, y)`, `Vector.zero`, `Vector.randomDirection()`,
`Vector.fromPolar(angle, radius)`. Don't roll your own Point/Vector.

## Love2D callbacks

- `main.lua` owns `love.load`, `love.keypressed`, `love.update`.
- `love.draw` is **not** implemented at top level - hump.gamestate does it
  via `GameState.registerEvents()`.
- `Timer.update(dt)` is ticked centrally in `love.update`.
- Escape-to-quit is a dev convenience, wired in `main.lua`.

## Scene shape

```lua
local scene = {}

function scene:enter()
    -- Load resources here, not at require time.
    local image = love.graphics.newImage('resources/images/gems.png')
    local atlas = TextureAtlas(image, 6, 1)
    ...
end

function scene:update(dt)
    -- Poll input, update state.
end

function scene:draw()
    love.graphics.draw(...)
end

return scene
```

- **Load resources in `:enter`**, not at module-load time. `tests.lua` breaks
  this rule but it's cruft.
- **Poll input inside `:update`** with `love.mouse.isDown`,
  `love.mouse.getPosition`. Manual edge detection with a `clicked_state`
  shadow variable is the user's pattern, not `love.mousepressed`.

## Resolution-independent rendering

Final scale for any sprite is
`world_scale * tweened_scale`, where `world_scale` is derived from
`WorldScaler.pixels_per_tile`. Keep this multiplication in any `:draw`
routine:

```lua
love.graphics.draw(
    self.image,
    self.quad,
    x + self.tweened_position.x,
    y + self.tweened_position.y,
    self.tweened_rotation,
    self.world_scale * self.tweened_scale,
    self.world_scale * self.tweened_scale,
    self.center_offset_x,
    self.center_offset_y
)
```

Call `love.graphics.draw` with the **full 9-arg signature** - don't rely on
defaults.

Pixel-art set-up in `love.load`:

```lua
love.graphics.setDefaultFilter('nearest', 'nearest', 1)
love.window.setMode(1280, 800)
```

## Texture atlas

A single image + an array of `love.graphics.newQuad` slices:

```lua
function TextureAtlas:init(image, x_count, y_count)
    self.image = image
    self.layers = {}
    local image_width, image_height = self.image:getDimensions()
    local cell_width = image_width / x_count
    local cell_height = image_height / y_count

    for y_idx = 1, y_count do
        for x_idx = 1, x_count do
            table.insert(self.layers, love.graphics.newQuad(
                (x_idx - 1) * cell_width,
                (y_idx - 1) * cell_height,
                cell_width,
                cell_height,
                image_width,
                image_height
            ))
        end
    end
end

function TextureAtlas:get_layer(index)
    return self.layers[index]
end
```

## No error handling

The user does not use `pcall` / `error(...)` / `assert(...)` in this project.
Code is optimistic. If you need to validate, add a single `assert(...)` -
don't introduce a new error-handling scheme without asking.

## No tests

PuzzleBruiser has **no tests, no test runner, no CI**. `tests.lua` at the
root is a hump.gamestate scratchpad demo - it has stale requires (missing
`libs.` prefix) and isn't hooked up.

Do not invent a Lua test framework. If a change is risky, use `print(...)`
to the console (`run.sh` starts love with `--console`).

## Debugging

- `print(...)` to the console. The only channel.
- Escape quits. Good for iteration.
- No logging library.

## Comments

See **comments-style**. Lua-specific:

- `--` line comments only. **No block comments** `--[[ ]]`.
- **No EmmyLua `---@param` annotations** in user code. `api/` has LSP stubs;
  keep them out of `src/`.
- British spelling: `colour`, `neighbour`.
- En-dash `–` in prose where it appears already.

## Summary checklist

- [ ] `local Class = require('libs.hump.class')` at the top; dot-separated
  requires; blank line between external and internal groups.
- [ ] Module file: `snake_case.lua`. Module local: `PascalCase`.
- [ ] hump.class `Class {}` or `Class { __includes = { ... } }`; explicit
  parent `.init(self)` in `:init`.
- [ ] Methods: `camelCase` public, `_camelCase` private.
- [ ] Fields: `snake_case` with `is_` / `has_` / `did_` for booleans.
- [ ] Guard clauses at the top of every method; multi-line booleans with
  standalone `and` / `not`.
- [ ] Callback is the last argument and always nullable-guarded.
- [ ] Every tween method starts with the cancel-then-start 3-line idiom.
- [ ] Resources loaded in scene `:enter`, not at module-load time.
- [ ] Draw with full 9-arg `love.graphics.draw` and the `world_scale *
  tweened_scale` multiplier.
- [ ] No error handling, no tests, no EmmyLua annotations.
- [ ] British spelling (`colour`, `neighbour`).
