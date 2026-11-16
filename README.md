# Juggling Lane Simulator

An animated simulator for rolling-ball juggling patterns. Balls roll across side-by-side lanes, and two hands carry them round the ends from one lane to the next.

## Using it

Open `index.html` in a browser. Pick a pattern from the list or type your own, then choose 1 to 9 balls.

- A pattern is a row of lane numbers. It is the order the hands roll in: the first hand rolls the 1st, 3rd, 5th numbers and the other hand rolls the 2nd, 4th, 6th.
- Lane 1 is at the bottom.
- With an odd number of balls the hands take turns. With an even number both hands roll at the same moment.
- The hand order stays the same whatever the number of balls. Each hand always rolls the ball that reached it first, so the paths the balls take change with the ball count.
- A typed pattern is refused if a lane would have to run in both directions.

A link can open on a chosen pattern, for example `index.html?p=121434&b=3&start=left`.

## Files

- `index.html`: the whole simulator.
- `fonts/`: the Fredoka typeface, used under the SIL Open Font License (see `fonts/OFL.txt`).
- `tests/test.html`: checks the rules for every listed pattern with 1 to 9 balls.
- `tests/filmstrip.html`: freezes a pattern at a row of moments, for checking the motion by eye.
- `tools/find_patterns.py`: searches for every valid pattern up to a beat limit.

To run the checks, start `python3 -m http.server` in this folder and open `http://localhost:8000/tests/test.html`.
