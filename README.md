# Multiplication Flash Cards

A one page practice site for the times tables, 1 through 12.

- Pick which tables to drill, or all of them
- Flip the card yourself, or pick the answer from four choices
- Shuffle or go in order
- Optional timer per card, which flips the card when it runs out
- Sounds for right and wrong, with a mute button

Live at https://achyboy.github.io/seth-math/

Everything is in `index.html`. There is no build step and nothing to install.
The sounds are synthesised with the Web Audio API, so there are no audio files.

The working source lives at `JobHub/_local/seth-flashcards.html`. Copy it over
`index.html` here and push to deploy. Bump `x-cards-version` in the meta tag
when you do, so a phone holding a stale copy is easy to spot.
