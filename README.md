# Juggling Lane Simulator

An animated simulator for rolling-ball juggling patterns. Balls roll across side-by-side lanes, and two hands carry them round the ends from one lane to the next.

## Using it

Open `index.html` in a browser. Pick a pattern from the list or type your own, then choose 1 to 9 balls.

- A pattern is a row of lane numbers. It is the order the hands roll in: the first hand rolls the 1st, 3rd, 5th numbers and the other hand rolls the 2nd, 4th, 6th.
- Lane 1 is at the bottom.
- With an odd number of balls the hands take turns. With an even number both hands roll at the same moment.
- The hand order stays the same whatever the number of balls. Each hand always rolls the ball that reached it first, so the paths the balls take change with the ball count.
- A typed pattern is refused if a lane would have to run in both directions.

### Zips

The "Zips" button switches to patterns with zips. A zip, written `z`, is a handoff: the hand passes its ball straight to the other hand, which rolls it on the next beat. Zips need an odd number of balls. Because a zipped ball jumps the queue, the rolls stop taking equal time; the simulator picks the most even timing that works. In zip mode, tapping a number under the lanes turns it into a zip and back.

### Lanes that change direction

The "Reverses" button switches to patterns in which a lane is rolled from both ends, such as `123` with 3 balls, where each ball rocks back and forth in its own lane. A lane can only be rolled the other way once it is empty, so each of these patterns has a top number of balls. They can have an odd number of rolls.

### Two people

The "1 person / 2 people" button puts a person at each end, with two hands each. Every ordinary pattern can be played this way, each person swapping hands from roll to roll. There are also patterns where each person rolls two balls at once, written with brackets: `[14][23]` means the right person rolls lanes 1 and 4 together, then the left person rolls lanes 2 and 3 together. The first number in each bracket is one ball's path and the second number is the other's. These use 2, 4, 6 or 8 balls.

With two people on, the "Mixed" button switches to patterns that mix single rolls and pairs, such as `12[13][24]`. The people take strict turns and both roll the same number of balls each loop. Like zips, these need uneven timing, so the beat counts are shown under the numbers; most need 5 or more balls.

A link can open on a chosen pattern, for example `index.html?p=121434&b=3&start=left`.

## Files

- `index.html`: the whole simulator.
- `fonts/`: the Fredoka typeface, used under the SIL Open Font License (see `fonts/OFL.txt`).
- `tests/test.html`: checks the rules for every listed pattern with 1 to 9 balls.
- `tests/icons.html`: shows every pattern picture at once.
- `tests/filmstrip.html`: freezes a pattern at a row of moments, for checking the motion by eye.
- `tools/find_zip_patterns.py`: searches for every zip pattern and its timing; `zip-patterns.txt` is its output.
- `tools/find_pair_patterns.py`: searches for the two-at-once patterns for two people.
- `tools/find_reverse_patterns.py`: searches for patterns with lanes that change direction.
- `tools/find_mixed_patterns.py`: searches for the mixed single-and-pair patterns for two people.
- `tools/find_patterns.py`: searches for every valid pattern up to a beat limit.

To run the checks, start `python3 -m http.server` in this folder and open `http://localhost:8000/tests/test.html`.
