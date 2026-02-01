# AI Judge MVP

## Overview

Prompt-driven AI Judge.

## Design Principles

- **Prompt Authority**: Game logic and bot moves in `system.txt`.
- **Minimal State**: Tracks rounds and bomb usage.
- **Deterministic Output**: Strict JSON schema.

## Architecture

- `system.txt`: Logic specification and precedence.
- `instruction.txt`: Data injection template.
- `judge.py`: Glue for API execution and state propagation.

## State Model

- `round`: Turn index.
- `user_bomb_used`: User constraint flag.
- `bot_bomb_used`: Bot constraint flag.

## Edge Cases

- Bomb reuse (INVALID)
- Conflicting moves (UNCLEAR)
- No move intent (INVALID)
- Emoji mapping (VALID)
- Turn wasting on non-valid moves
