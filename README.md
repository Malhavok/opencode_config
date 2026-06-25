# OpenCode configuration generator

This repository is to be used as a source of agents and skills for OpenCode. Currently, it's generated assuming all models come from OpenCode Zen, but it's simple enough to override the provider.

## Whom I stole from

- https://senior.software/how-i-actually-use-llms-to-build-software/ – great read, initial approach taken from here
- https://github.com/martinffx/atelier – agents were further refined using this repository
- https://github.com/mksglu/context-mode – caveman + mcp for further saving tokens
- https://github.com/DietrichGebert/ponytail – said to be a better caveman
- https://github.com/aeroxy/ast-bro – look at codebases from the perspective of code, not text

## The What

This repo provides you with "architect" models that you chat with over the feature you want to implement and once you "approve", it spins developer and reviewers to deliver to you the best it can. It worked pretty well for me, but since it's LLMs YMMV.

You have (at the time of writing) four architects available:

- Pro architect – spare no expense, everything is top of the line (Opus, Sonnet, etc).
- Cheap architect – uses coder model for architect, free and cheap developers, top reviewers + architecture reviewer.
- Free architect – uses free model for architect, free developers, free reviewers.

I can't really see reason to go beyond these three for now, and I need to do much more testing before I can surely say I'm pleased/displeased with any of them. Cheap architect is my way to go – with architecture review it proved itself a fre times now without breaking my wallet. Free architect is decent for playing around or e.g. making simple games in Usagi or Love2D. I don't know why I'm keeping the Pro tho – it's too expensive to be used just-like-that.

## Assumptions

When you `./link.sh`, you literally link `opencode` to your `~/.config/opencode` directory, so back your configurations before running.

If you want to use it as-is, you should connect to Zen first.

You need to install the following:
```bash
npm install -g context-mode
git submodule update --init --recursive
brew install aeroxy/tap/ast-bro
```

## The Why

I like the configuration, but I wanted a bit more flexibility. When I burned by first $20, I wanted to check if I could get better results with lower-cost models. Using this, I can juggle architects, developers and reviewers from "top of the line" to "absolutely free" with a few tab clicks.
