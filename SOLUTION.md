# Solution notes

**Spoilers**: path, K and the final answer for [the puzzle](https://www.janestreet.com/puzzles/pent-up-frustration-3-knight-moves-7-index/).

Answer: **33609** (matches the [official solution](https://www.janestreet.com/puzzles/pent-up-frustration-3-knight-moves-7-solution/)).

## Key observations

- Heights are only ground or tower, so there are two move types:
  - flat L-move `(1,2)/(2,1)` between squares of equal height (`+N`)
  - straight 2-square move `(2,0)/(0,2)` onto or off a tower (`×N` / `÷N`)
- Towers can be placed lazily: the knight must visit every tower, so a tower is always on a path
  square. Landing on a square in a region with no tower yet branches on "tower here or not".
- Numbered squares may only be landed on at record moves, and the score must match exactly.
  This forces the first 18 moves almost completely (105 variants, all ending at `(3,2)` with 88).
- 11 written scores = 6 through move 18 + 5 after, so `18 + 5K <= 62` gives `K` in `4..8`.

## Files

| file | what |
|---|---|
| `knight.py` | board data, move generator, lazy tower placement, `solve_K` DFS |
| `run_K.py` | runs the search for K = 4..8 (only K = 7 has a solution, ~5s) |
| `viz.html` | interactive explorer: open in a browser, step with ← / →, place towers, load the solution |
| `viz.py` | static matplotlib renderer |
| `states_18.json` | all 105 valid states after move 18 |
| `solutions_K7.json` | the unique solution |
| `log.md` | working notes, in order |

## Run

```
python3 run_K.py
```

| K | solutions | nodes | time |
|---|---|---|---|
| 4 | 0 | 9k | 0.1s |
| 5 | 0 | 24k | 0.2s |
| 6 | 0 | 58k | 0.5s |
| 7 | 1 | 696k | 4.7s |
| 8 | 0 | 311k | 2.7s |
