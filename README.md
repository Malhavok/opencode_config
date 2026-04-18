# OpenCode configuration generator

This repository is to be used as a source of agents and skills for OpenCode. Currently, it's generated assuming all models come from OpenCode Zen, but it's simple enough to override the provider.

## Whom I stole from

- https://senior.software/how-i-actually-use-llms-to-build-software/ – great read, initial approach taken from here
- https://github.com/martinffx/atelier – agents were further refined using this repository
- https://github.com/JuliusBrussee/caveman – token reduction for medium and cheap agents use this repository as a base

## The What

This repo provides you with "architect" models that you chat with over the feature you want to implement and once you "approve", it spins developer and reviewers to deliver to you the best it can. It worked pretty well for me, but since it's LLMs YMMV.

You have (at the time of writing) four architects available:

- Pro architect – spare no expense, everything is top of the line (Opus, Sonnet, etc).
- Free architect – uses only free Zen models.
- Medium architect – uses top model for architect (so the plan is sound), cheap and medium developers, top reviewers, all in caveman mode.
- Cheap architect – uses medium model for architect, free and cheap developers, top reviewers, all in caveman to save tokens.

I can't really see reason to go beyond these four for now, and I need to do much more testing before I can surely say I'm pleased/displeased with any of them. Even free architect seems to have its uses (especially once you run out of tokens at the very end of implementation :p)

## Assumptions

When you `./link.sh`, you literally link `opencode` to your `~/.config/opencode` directory, so back your configurations before running.

If you want to use it as-is, you should connect to Zen first.

## The Why

I like the configuration, but I wanted a bit more flexibility. When I burned by first $20, I wanted to check if I could get better results with lower-cost models. Using this, I can juggle architects, developers and reviewers from "top of the line" to "absolutely free" with a few tab clicks.
