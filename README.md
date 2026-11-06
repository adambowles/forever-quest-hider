# Forever Quest Hider

A small WoW Forever addon that makes Blizzard's objective tracker invisible during normal play, including with the gamepad UI. No configuration window, libraries, timer loop, or other UI changes.

## Commands

Enabled by default, saved per character:

| Command | Action |
| --- | --- |
| `/fth` | Toggle hiding |
| `/fth on` | Hide the tracker |
| `/fth off` | Restore tracker opacity |
| `/fth status` | Show the saved setting |

## Gamepad behaviour

The tracker remains registered and shown internally; its opacity is set to zero. While Blizzard's **HUD navigation mode** is open, the tracker becomes visible so controller quest selection and HUD navigation can still work. It fades back to invisible when HUD navigation closes. This deliberate exception avoids removing the frame that Blizzard uses as a navigation starting point. Visibility changes requested in combat wait until combat ends.

This also hides achievements and other objectives inside the same tracker. It does not alter quest tracking, map markers, bindings, or other panels. Because this is visual hiding, the transparent frame can still receive mouse input. Turn it off with `/fth off` if needed. Disable Polestar's tracker-hiding option and other tracker visibility addons to avoid conflicting changes.

## Install / AME

Use the packaged `ForeverQuestHider-<version>-Forever.zip` from [GitHub Releases](https://github.com/adambowles/forever-quest-hider/releases), not GitHub's source archive. Extract its `ForeverQuestHider` folder to `_forever_/Interface/AddOns/` and restart WoW.

For AME: repository `adambowles/forever-quest-hider`, release tag prefix `v`, asset pattern `ForeverQuestHider-*-Forever.zip`. There is only one installable ZIP per release.

## Development and releases

The TOC's `## Version` is the single version source, starting at 0.1.0. Use SemVer. Tests run on pushes to non-main branches. Pushes to main do nothing. A `vX.Y.Z` tag on a commit contained in main validates the TOC version, builds the ZIP, and publishes a GitHub release; tag jobs do not repeat tests. Tests and release packaging have separate workflows.

```sh
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python tools/package.py
```

After merging the PR, tag the merged commit `v0.1.0` and push the tag to publish the first release. No release is published by merging alone.

## Validation

Automated Lua 5.1 tests use mocked WoW APIs. They cannot prove in-game protection/taint or controller behaviour. Before considering this release verified, test login/reload, quest updates, entering/leaving combat, keyboard/gamepad mode changes, and opening/closing HUD navigation (including quest selection). Use `/fth off` to restore visibility if necessary.

Implementation is original. Research: [Polestar's deliberate gamepad exclusion](https://github.com/fitzforge/polestar/blob/main/addon/Polestar/QoL/Toggles.lua) and [Blizzard HUD navigation source](https://github.com/Gethe/wow-ui-source/blob/forever/Interface/AddOns/Blizzard_Gamepad/UI/HUDMode/GamepadHudMode.lua).
