# Pent-Up Frustration 3 / Knight Moves 7 — log

## Problem (paraphrased)
- 8x8 board tiled by 12 pentominoes + one 2x2 tetromino = 13 regions.
- Add one **tower** (extra 1x1x1 cube, altitude 2 instead of 1) to exactly one square of each region.
- Knight starts bottom-left. Makes 3D knight moves (0 in one dim, 1 in another, 2 in third) until all 13 towers visited. Never revisits a square. May pass over towers.
- Score starts 0. On move N:
  - same altitude: score += N
  - up: score *= N
  - down: score /= N (only allowed if score % N == 0)
- Score written on landing square at moves 3, 6, ..., 18; then every K moves (K > 3).
- Answer: fill in scores on all visited squares; for each unvisited square sum orthogonal neighbors on path; total of those sums.

## Coordinates
(0,0) bottom-left, (7,7) top-right. (x, y) = (col, row).

## Board data
Numbers (written scores):
```
(5,7): 37    (7,7): 1100
(3,5): 23    (5,5): 138
(0,4): 528
(1,3): 449   (4,3): 16
(1,2): 750   (3,2): 88   (5,2): 272   (6,2): 1
(0,0): 0  (start)
```

Regions (top row printed first, i.e. y=7 at top; H = 2x2 tetromino):
```
y=7  A A A A A B B B
y=6  C C C D D E E B
y=5  C F C D D D E B
y=4  G F F H H I E E
y=3  G G F H H I I J
y=2  G K F L I I M J
y=1  G K L L L M M J
y=0  K K K L M M J J
     x=0 ...     x=7
```

## Move types (altitude 1 = ground, 2 = tower)
- flat L move (dx,dy) in {(±1,±2),(±2,±1)}, dz=0: both squares same altitude → +N
- straight 2-step (dx,dy) in {(±2,0),(0,±2)}, dz=±1: ground→tower (×N) or tower→ground (÷N)
- L move between different altitudes: illegal (would need 3 nonzero dims)

## Plan / notes (mine)
- `possible_moves()`: loop knight deltas from cur_pos, bounds check 0 <= nx <= 7, filter seen.
- If on number square, can't jump directly to another number.
- On move 3n+2, next move (3n+3) must land on numbered square → filter.
- Find relationships between numbers (e.g. 88 | 528), identify primes.
- Find which number squares are a knight's move apart (can't go directly between them).
- Max 63 moves = recursion depth bound; branching up to ~8.
- First jump to (2,1)?? (see open questions)
- Go sequentially, prune with running_score.
- Step 1: only solve first 18 moves; rest later.

## Open questions / corrections
- Towers unknown → part of search state (which square in each region). Move set depends on altitude.
- First move not forced to (2,1): (2,0)/(0,2) legal if tower there (0*1 = 0). Tower could even be on (0,0). ((1,2) ruled out, see below.)
- Which number goes with which move not given → match: score at move 3k must equal number on landing square.
- Moves 3k (k<=6) land on number squares; other moves in 1..18 land on unnumbered squares.
- 11 nonzero numbers: 6 at moves 3..18, 5 at moves 18+K, 18+2K, ..., 18+5K.

## Verified (session 2)
- 11 written numbers (0 at start is not a record): 6 at moves 3..18, 5 at 18+K..18+5K.
- "up until #18" read as inclusive (RECORD_UNTIL constant in knight.py if wrong).
- K bound: 18+5K <= 62 (need unvisited squares, so < 63 moves) -> K in {4..8}.
- Heights stored as 0 (ground) / 1 (tower); only differences matter.
- Move 1 can't be (1,2): it holds 750 and move 1 must land unnumbered.
  Options: (2,1) flat, or (2,0)/(0,2) if tower there (0*1 = 0).
- State: pos = (x,y), height = dict[(x,y)] -> 0/1.

## Number facts (from knight.py)
- primes: 23, 37, 449
- divisibility: 16|272 (x17), 16|528 (x33), 23|138 (x6), 88|528 (x6)
- flat-knight-adjacent number squares: 23-16, 138-16, 528-750, 449-88, 16-1
- straight-2 apart (only via tower): 37-1100, 37-138, 23-138, 750-88, 88-272

## knight.py
- BOARD_ROWS / REGION_ROWS drawn top row first; NUMBERS, REGION, TARGETS keyed by (x,y).
- possible_moves(pos, move_num, score, seen, height, K=None) yields (next, new_score).
  Handles flat/straight moves, altitude rule, divide legality, numbered-square
  filter for moves <= 18 (and past 18 if K given), exact score match on record moves.
- Towers: not handled yet (height dict passed in).

## Towers (session 3)
- towers[(x,y)] = tower_id: region letter A..M -> id 0..12. Every square maps to its region's id.
- tower_location[tower_id] = (x,y): empty at start, set when a tower gets placed (one per id).
- Grid of ids (top row y=7; verify against image):
```
y=7   0  0  0  0  0  1  1  1
y=6   2  2  2  3  3  4  4  1
y=5   2  5  2  3  3  3  4  1
y=4   6  5  5  7  7  8  4  4
y=3   6  6  5  7  7  8  8  9
y=2   6 10  5 11  8  8 12  9
y=1   6 10 11 11 11 12 12  9
y=0  10 10 10 11 12 12  9  9
```
- Sizes: all 5 except id 7 (2x2 tetromino) = 4. Total 64.
- Start (0,0) is tower_id 10.
- (0,0) counted as numbered square (12 numbered incl. 0). Can't return there anyway (in seen).
  11 of them are written scores (moves 3..18 and 18+jK).
- Undecided: how height is stored (currently dict, missing = 0). Could be derived from
  tower_location instead (pos in tower_location.values() -> tower).

## First 3 hops (session 4) — forced, unique
- path: (0,0) -> (2,1) -> (4,2) -> (6,2), score after move 3 = 1
- towers: id 10 at (0,0), id 11 at (2,1), id 8 at (4,2)
- why: only reachable record value at move 3 is 1 (at (6,2)). Need score 3 after move 2
  then down (3/3). Score 3 = 0+1+2 -> moves 1,2 flat. Down into (6,2) must come from
  straight-2 neighbor; only (4,2) reachable in 2 knight moves ((1,2) route blocked by 750).
  Flat chain needs (0,0),(2,1),(4,2) all towers.
- code: expand(start_states(), 1, 3) in knight.py
- viz.py: draw(path, tower_location, out, title) -> PNG. Shaded = visited, corner = hop #,
  orange triangle = tower, thick lines = regions. `python3 viz.py` renders first 3 hops to board.png.
- viz.html: interactive explorer (open in browser). Click green = legal hop (shows type→score),
  undo (z), reset, tower mode (t) places/removes region tower, free mode for illegal hops,
  K input for >18 record rule, "Load first 3 hops" preset. Path replays when towers change; bad steps red.

## Moves 4-6 (session 5) — 3 options, all score 16 at (4,3)
- all flat: 1 +4 +5 +6 = 16, no new towers
- A: (6,2) -> (7,0) -> (5,1) -> (4,3)
- B: (6,2) -> (5,0) -> (3,1) -> (4,3)
- C: (6,2) -> (4,1) -> (2,2) -> (4,3)
- code: expand(expand(start_states(), 1, 3), 4, 3)

## Moves 7-9 (session 6) — forced, same for A/B/C
- (4,3) -> (4,5) up x7 = 112 -> (4,7) down /8 = 14 -> (3,5) flat +9 = 23
- new tower: id 3 at (4,5)
- strategy: queue of states; take first, keep it unless next 3 moves dead-end, then pop next.
  code: next_chunk(queue, first_move, n_moves=3, K=None) -> (chosen, expanded, rest_of_queue)
- queue after 9: chose A, B/C left (all give same 7-9, differ only in squares used at moves 4-5)

## Moves 10-12 (session 7) — 5 options, all score 528 at (0,4)
- 23 +10 = 33 +11 = 44, then up x12 = 528 onto (0,4) -> new tower id 6 at (0,4)
- options (moves 10, 11):
  1. (2,3), (0,2)
  2. (1,4), (0,2)
  3. (1,4), (0,6)
  4. (1,6), (2,4)
  5. (2,7), (0,6)
- A/B/C each give same 5 (moves 4-5 squares don't interact yet). Queue at 12: 5 states (took 1st).

## Moves 13-18 (session 8)
- 13-15: (0,4) -> (1,6) or (2,5) [tower, flat +13 = 541] -> (3,7) [tower, flat +14 = 555] -> (5,7) down /15 = 37
  - new towers: id 0 at (3,7); id 2 at (1,6) OR (2,5)
- 16-18: all flat +16 +17 +18 -> 37 -> 53 -> 70 -> 88 at (3,2), via varying middle squares
- queue run: 4 states at 18 (moves 16-17 vary: (6,5)/(3,6) then (5,3)/(4,4)/(2,4))
- full search (no queue): 105 states after 18, ALL end at (3,2) score 88
  - towers fixed: 0:(3,7) 3:(4,5) 6:(0,4) 8:(4,2) 10:(0,0) 11:(2,1); only id 2 varies: (1,6) [48] / (2,5) [57]
  - rest of variation = which filler squares used at moves 4-5, 10-11, 16-17
- 7 of 13 towers placed after 18. Remaining regions: 1, 4, 5, 7, 9, 12.

## 105 states breakdown (session 9)
- 105 = 3 x 35 (not 3x5x7). Moves 4-5 choice (A/B/C) independent: 35 each.
- 35 = 4 x 8 + 3: moves 10-11 option 4 [(1,6),(2,4)] conflicts later:
  (1,6) visited as ground -> region 2 tower can't be (1,6); (2,4) used -> blocks one move-17 route.
- 8 combos for 13-17: region 2 tower (1,6)/(2,5) x move 16 (6,5)/(3,6) x move 17 (2 each).
- Differences = visited filler squares + region 2 tower only. All 105 visited sets distinct.
- Stored: states_18.json via save_states/load_states in knight.py. Each = path (19 squares incl start), score 88, towers.

## Brute force per K (session 10)
- solve_K(states, K) in knight.py: DFS from the 105 states_18 states. Prunes: K record rule,
  stop at 13th tower (must be >= 18+5K), dead region (all squares visited, no tower).
- run_K.py results:
  - K=4: 0 (9k nodes)   K=5: 0 (24k)   K=6: 0 (58k)   K=7: 1 (696k, 4.7s)   K=8: 0 (311k)
- K=7 unique solution -> solutions_K7.json. 54 moves, 9 unvisited squares.
  - records at 25:138, 32:272, 39:449, 46:750, 53:1100; 13th tower reached at move 54.
- final answer (neighbor sums) NOT computed yet.
- viz.html: "Load K=7 solution" button (solution embedded as SOLUTION const; sets K=7). Undo steps back.
- viz.html stepping: ←/→ back/forward (redo stack), ↑/Home start, ↓/End end. Load buttons start at move 0 with hops queued.

## Result check (session 11)
- Path, towers, all scores match official solution image exactly.
- 59400 = knight's score after move 54 (final SCORE), NOT the puzzle answer.
- Puzzle answer = sum of neighbor sums over 9 unvisited squares = 33609 (matches official).
