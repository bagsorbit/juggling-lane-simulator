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

Reverses also work with 2 people on: the same patterns and ball counts, with each person using their hands in turn. There are also 6-lane pair patterns with an odd number of brackets, like `(12)(34)(56)`: each person rolls two at once, and the next time round the other person takes each bracket, so every lane changes direction. They work with 2, 4 or 6 balls. With an even number of brackets, lanes change direction where the same lane turns up at both ends: `(12)(34)(34)(12)` is two pairs going back and forth on four lanes, each pair on its own two lanes, with 2 or 4 balls.

Zips also work with 2 people on. A `z` always means a zip to your own other hand, just as for one person; the other hand rolls it on that person's next turn. A `p` is a pass: the two people meet in the middle of the board and hand the ball across, and it is rolled on the next beat. The list has every one-person zip pattern (played with its zips as passes), patterns where both people zip to themselves, and patterns where each person does both. Tapping a number cycles roll, pass, zip. Passes can also go two at once, written `(pp)` inside a bracket pattern: `(12)(pp)` means one person rolls lanes 1 and 2 together and the other hands both balls straight back across the middle. Each named zip pattern has a two-at-once version in the list, called "... Sync" (`(12)(pp)` is Parade Sync).

Moves made at the same moment are written in round brackets, like `(14)(23)`, as siteswap writes sync throws (square brackets mean multiplexes there). The page, the engine and the search tools all use this spelling, and `z` for a zip to your own other hand and `p` for a pass, throughout. Old share links (from before 2026-11-18, without `v=2`) wrote square brackets and, for two people, `z` for a pass and `s` for a zip to yourself; those links and saved favourites are converted when they are opened. The search tools sort their lists in the order they had when brackets were square, so the lists keep their order.

### Slope

The "Ping Pong" button is a one-person mode with three balls. Just after a ball rolls past, the hand places its own ball a little way up the lane (about the second chevron), then jumps back and grabs the one that went past before it reaches the end, and carries it to its next lane. So a lane can be used both ways, even one lane on its own (`1` is a three-ball cascade on a single lane). The grab has to be quick, so each roll is in the same lane as the roll before it or the lane next to it. The All patterns wall has all 26 three-ball patterns of up to 8 rolls that use some lane both ways and in which no hand move happens twice, and the pattern list has a few picked from both kinds, grouped by lanes (plus `111222`, which repeats a hand move and was added by hand). With four balls the hands place at the same moment, written in brackets with the right hand first: `(12)(21)` is the right hand in lane 1 and the left in lane 2, then the other way round. The two lanes of a bracket must differ (otherwise the balls meet head-on), and each hand grabs the ball the other placed a beat before, in the same or the next lane. With 2 people on, there is a person at each end, each switching hands from one placing to the next: the balls move the same, and a ball is grabbed by the hand that will place it next, so after placing a hand goes back to wait for its next ball. Each pattern has one ball count, so the ball buttons are greyed out; there are 72 four-ball patterns of up to 5 beats. Search: `tools/find_ping_patterns.py` (`--embed` writes them into `index.html`).

The "Slope" button turns the lanes to run up the screen, sloping down towards one person at the bottom. A hand carries a ball up a lane and lets go, and the ball rolls back. These are toss-juggling patterns: each is written as the lanes in the order the hands use them, then the siteswap in brackets, such as `12 (siteswap 3)` for the cascade. Every ball rolls at the same speed, so a bigger siteswap number starts higher up the lane. A `z` is a zip (a siteswap 1). The patterns come from a fixed list.

### Lanes that change direction

The "Reverses" button switches to patterns in which a lane is rolled from both ends, such as `123` with 3 balls, where each ball rocks back and forth in its own lane. A lane can only be rolled the other way once it is empty, so each of these patterns has a top number of balls. They can have an odd number of rolls.

### Two people

The "1 person / 2 people" button puts a person at each end, with two hands each. Every ordinary pattern can be played this way, each person swapping hands from roll to roll. There are also patterns where each person rolls two balls at once, written with brackets: `(14)(23)` means the right person rolls lanes 1 and 4 together, then the left person rolls lanes 2 and 3 together. The first number in each bracket is one ball's path and the second number is the other's. These use 2, 4, 6 or 8 balls.

With two people on, the "Mixed" button switches to patterns where each person keeps their own rhythm, mixing single rolls and pairs. They are written as a row for each person with a `|` between them: `(13)-|22` means one person rolls lanes 1 and 3 together and then rests a beat, while the other rolls lane 2 on every beat. Every ball rolls at the same speed; a ball that arrives early waits in a hand, and a person can hold at most two. Most of these work with 3, 5, 7 or 9 balls. A few have lanes rolled from both ends, so those lanes change direction once they are empty, such as `1234|3412`. The Snakes, such as `12345----|----12345` (one person rolls every lane in turn, the other starts as the first ball arrives and sends them all back), and the Funnel `(15)(24)3---|---(15)(24)3` are written the same way but are listed under 2 people + Reverses.

A link can open on a chosen pattern, for example `index.html?p=121434&b=3&start=left`.

## Files

- `index.html`: the whole simulator.
- `fonts/`: the Fredoka typeface, used under the SIL Open Font License (see `fonts/OFL.txt`).
- `tests/test.html`: checks the rules for every listed pattern with 1 to 9 balls.
- `tests/icons.html`: shows every pattern picture at once.
- `tests/filmstrip.html`: freezes a pattern at a row of moments, for checking the motion by eye.
- `tools/find_zip_patterns.py`: searches for every zip pattern and its timing; `zip-patterns.txt` is its output.
- `tools/find_pair_reverse_patterns.py`: searches for reversing pair patterns; `--embed` writes them into `index.html`.
- `tools/find_two_zip_patterns.py`: searches for two-person patterns with self zips; `--embed` writes the picked list into `index.html`.
- `tools/find_pair_zip_patterns.py`: searches for passes two at once (`(pp)` on the page, `(zz)` in the code) and works out the Sync version of each named zip pattern; `--embed` writes them into `index.html`.
- `tools/find_pair_patterns.py`: searches for the two-at-once patterns for two people.
- `tools/find_reverse_patterns.py`: searches for patterns with lanes that change direction.
- `tools/find_rhythm_patterns.py`: searches for the two-person patterns where each person keeps their own rhythm.
- `tools/find_patterns.py`: searches for every valid pattern up to a beat limit.

To run the checks, start `python3 -m http.server` in this folder and open `http://localhost:8000/tests/test.html`.
