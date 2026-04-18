---
name: lua-style
description: Lua / Love2D style - hump.class OOP with mixins, PascalCase modules with snake_case fields, camelCase methods, callback-last nullable callbacks, cancel-then-start tween idiom, dot-separated requires, resolution-independent rendering via scalers, gamestate scenes, single-file modules returning the class. Load this before writing or reviewing any Lua code.
metadata:
  scope: language
  language: lua
  framework: love2d
---

# Lua / Love2D style

Target: Love2D 11.x with **hump** (class, timer, gamestate, vector).

Read **naming-conventions**, **control-flow-style**, and **comments-style**
first. These are Lua-specific additions.

## Requires

Dot-separated paths with clear grouping. External / third-party libs first,
then internal modules, with a blank line between:

```lua
local Class = require('libs.hump.class')
local Timer = require('libs.hump.timer')
local Vector = require('libs.hump.vector')

local TextureAtlas = require('src.core.texture_atlas')
local WorldScaler = require('src.core.world_scaler')
local Tile = require('src.tiles.tile')
```

One require per line. `local` is mandatory.

## Single-file module shape: hump.class

The standard module pattern. Each file is a class or service:

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
- `:init(...)` for construction.
- Methods defined with `function Class:method(args)`.
- Last line is always `return ClassName`.

## Mixins via `__includes`

Hump's `__includes` for trait-like composition. Each mixin owns *one aspect*
of visual or behavioural state:

```lua
local Tile = Class { __includes = { ICanBounce, ICanShake, ICanWiggle } }

function Tile:init(name, image, quad)
    ICanBounce.init(self)
    ICanShake.init(self)
    ICanWiggle.init(self)
    self.name = name
    self.image = image
    self.quad = quad
end
```

**Explicitly call each parent `.init(self)`** - do not rely on a super chain.

Each mixin exposes verb-like methods and manages its own tweened state:

- `ICanBounce` owns `self.tweened_scale` and `self.scale_tween` handle.
- `ICanShake` owns `self.tweened_rotation` and `self.rotation_tween`.
- `ICanWiggle` owns `self.tweened_position` and `self.wiggle_tween`.

## Singleton table modules

For scope-less services (no instances needed) use a plain table with methods:

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

function WorldScaler:getScale()
    return self.pixels_per_tile
end

return WorldScaler
```

Use this for services that need to be globally accessible (screen scalers,
asset caches, configuration).

## Method visibility

- **Public methods**: `camelCase` - `addMatchChangedCallback`, `bounceUp`,
  `canAddTile`, `isValidChain`.
- **Private methods**: leading `_` + camelCase - `_spawnTiles`,
  `_tileToPosition`, `_buildAllowedTiles`.

Fields are `snake_case`: `self.tile_positions`, `self.is_active`,
`self.selected_tiles`.

## Scene globals pattern

When using hump.gamestate, it's common to assign scene-level objects
**without `local`** in `:enter`, making them ambient globals:

```lua
function scene:enter()
    board = Board(generator, 6, 6)
    matcher = Matcher(board, rule)
end
```

Other modules then read these globals directly. When editing inside the
scene, keep this pattern. When editing outside, prefer explicit dependency
injection, but accessing scene globals is acceptable.

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

Every method that triggers an async effect accepts an optional `callback` as
the last argument:

```lua
function ICanBounce:show(callback)
    if self.scale_tween ~= nil then
        Timer.cancel(self.scale_tween)
    end

    self.tweened_scale = 0.0
    self.scale_tween = Timer.tween(0.3, self, { tweened_scale = 1.0 }, 'out-elastic', callback)
end
```

Consumers guard before calling: `if callback ~= nil then callback() end`.

## Cancel-then-start tween idiom

Any effect that can be retriggered must cancel the previous one first. The
pattern is copied literally, not abstracted:

```lua
if self.scale_tween ~= nil then
    Timer.cancel(self.scale_tween)
end

self.scale_tween = Timer.tween(...)
```

## Named local closures inside methods

When a callback closes over locals, define it as a `local function` inside
the method rather than inlining it:

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

Anonymous inline functions are reserved for trivial timer callbacks.

## Data structures

- **Arrays**: 1-indexed, built via `table.insert(t, v)`.
- **Sets**: `t[key] = true`, membership via `if t[key]`, cleared with `self.foo
  = {}`.
- **Parallel containers** for different access patterns: `selected_tiles`
  (array, ordered), `selected_tiles_names` (parallel array of names),
  `selected_tiles_set` (O(1) membership).
- **`tostring(object)` as key** for string-keyed tables holding complex objects
  (vectors, custom objects):

```lua
local tile_key = tostring(position)
self.tiles[tile_key] = tile
```

- **`rawget(self, key)`** when `__index` might lie (hump.class instances).

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

Use hump's vector for 2D math. Overloaded operators: `+`, `-`, `*`.

```lua
local new_position = position + direction
local scaled = position * 2.0
```

Common constructors: `Vector(x, y)`, `Vector.zero`, `Vector.randomDirection()`,
`Vector.fromPolar(angle, radius)`.

## Love2D entry points

- `main.lua` owns `love.load`, `love.keypressed`, `love.update`.
- `love.draw` delegated to gamestate via `GameState.registerEvents()`.
- `Timer.update(dt)` ticked centrally in `love.update`.

## Scene lifecycle

```lua
local scene = {}

function scene:enter()
    -- Load resources here, not at module-load time.
    local image = love.graphics.newImage('resources/images/sprites.png')
    self.atlas = TextureAtlas(image, 6, 1)
end

function scene:update(dt)
    -- Poll input, update state.
    local is_clicked = love.mouse.isDown(1)
end

function scene:draw()
    -- Render with world_scale * tweened_scale.
end

return scene
```

- **Load resources in `:enter`**, not at require time.
- **Poll input in `:update`** via `love.mouse.isDown`, `love.mouse.getPosition`.
- Edge detection (clicked vs released) done manually with a shadow variable,
  not via `love.mousepressed`/`love.mousereleased`.

## Resolution-independent rendering

Calculate a base `world_scale` (e.g. `pixels_per_tile`) and multiply by any
tweened scale in `:draw`:

```lua
love.graphics.draw(
    self.image,
    self.quad,
    x + self.tweened_position.x,
    y + self.tweened_position.y,
    self.tweened_rotation,
    self.world_scale * self.tweened_scale,
    self.world_scale * self.tweened_scale,
    center_x,
    center_y
)
```

Call `love.graphics.draw` with the **full 9-argument signature** - don't rely
on defaults.

Pixel-art filtering in `love.load`:

```lua
love.graphics.setDefaultFilter('nearest', 'nearest', 1)
love.window.setMode(1280, 800)
```

## Texture atlas

A single image sprite sheet split into quads:

```lua
function TextureAtlas:init(image, x_count, y_count)
    self.image = image
    self.layers = {}
    local w, h = image:getDimensions()
    local cell_w, cell_h = w / x_count, h / y_count

    for y = 1, y_count do
        for x = 1, x_count do
            table.insert(self.layers, love.graphics.newQuad(
                (x - 1) * cell_w,
                (y - 1) * cell_h,
                cell_w, cell_h, w, h
            ))
        end
    end
end

function TextureAtlas:get(index)
    return self.layers[index]
end
```

## No error handling

The codebase does not use `pcall` / `error(...)` / `assert(...)` heavily.
Code is optimistic. Add a single `assert` for critical invariants if needed,
but don't introduce a full error-handling scheme.

## No test framework

The codebase has no automated tests. Use `print(...)` to the console for
debugging (run Love2D with `--console` flag to see output).

## Debugging

- `print(...)` is the only debugging channel.
- Escape quits for rapid iteration.
- No logging library.

## Comments

See **comments-style**. Lua-specific:

- `--` line comments only. No block comments `--[[ ]]`.
- No EmmyLua `---@param` annotations in source code (they belong in `api/`
  LSP stubs if needed).
- British spelling: `colour`, `neighbour`.
- Use en-dash `–` where it reads naturally in prose.

## Summary checklist

- [ ] `local Class = require('libs.hump.class')` at top; dot-separated requires;
  blank line between external and internal groups.
- [ ] File: `snake_case.lua`. Module local: `PascalCase`.
- [ ] `Class {}` or `Class { __includes = { ... } }`; explicit parent `.init(self)`
  in `:init`.
- [ ] Methods: `camelCase` public, `_camelCase` private.
- [ ] Fields: `snake_case`, `is_`/`has_`/`did_` for booleans.
- [ ] Guard clauses at top of every method; multi-line booleans with standalone
  `and` / `not`.
- [ ] Callback is last argument and always nullable-guarded.
- [ ] Every tween method starts with cancel-then-start.
- [ ] Resources loaded in scene `:enter`, not at require time.
- [ ] Draw with full 9-arg `love.graphics.draw` and `world_scale * tweened_scale`.
- [ ] No error handling, no tests.
- [ ] British spelling (`colour`, `neighbour`).