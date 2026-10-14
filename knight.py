from itertools import combinations

N = 8
RECORD_EVERY = 3
RECORD_UNTIL = 18  # inclusive: scores written at moves 3, 6, ..., 18

# Board as drawn, TOP row first (y=7). None = blank square.
BOARD_ROWS = [
    [None, None, None, None, None,   37, None, 1100],  # y=7
    [None, None, None, None, None, None, None, None],  # y=6
    [None, None, None,   23, None,  138, None, None],  # y=5
    [ 528, None, None, None, None, None, None, None],  # y=4
    [None,  449, None, None,   16, None, None, None],  # y=3
    [None,  750, None,   88, None,  272,    1, None],  # y=2
    [None, None, None, None, None, None, None, None],  # y=1
    [   0, None, None, None, None, None, None, None],  # y=0
]

# Regions as drawn, TOP row first. H = 2x2 tetromino.
REGION_ROWS = [
    "AAAAABBB",  # y=7
    "CCCDDEEB",  # y=6
    "CFCDDDEB",  # y=5
    "GFFHHIEE",  # y=4
    "GGFHHIIJ",  # y=3
    "GKFLIIMJ",  # y=2
    "GKLLLMMJ",  # y=1
    "KKKLMMJJ",  # y=0
]

# (x, y) lookups, (0,0) bottom-left
NUMBERS = {
    (x, N - 1 - r): v
    for r, row in enumerate(BOARD_ROWS)
    for x, v in enumerate(row)
    if v is not None
}
REGION = {
    (x, N - 1 - r): ch
    for r, row in enumerate(REGION_ROWS)
    for x, ch in enumerate(row)
}

# towers[(x,y)] = tower_id (0..12), one id per region: A=0, B=1, ..., M=12
towers = {pos: ord(ch) - ord("A") for pos, ch in REGION.items()}

# tower_location[tower_id] = (x,y), filled in as towers get placed
tower_location = {}

START = (0, 0)
TARGETS = {p: v for p, v in NUMBERS.items() if p != START}  # the 11 written scores

FLAT_DELTAS = [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]
STRAIGHT_DELTAS = [(2, 0), (-2, 0), (0, 2), (0, -2)]  # only legal with altitude change


def in_bounds(x, y):
    return 0 <= x < N and 0 <= y < N


def must_record(move_num, K=None):
    """True if the score is written on the square landed on at this move."""
    if move_num <= RECORD_UNTIL:
        return move_num % RECORD_EVERY == 0
    if K is None:
        return None  # unknown past move 18
    return (move_num - RECORD_UNTIL) % K == 0


def apply_score(score, n, dz):
    """New score after move n with altitude change dz, or None if illegal."""
    if dz == 0:
        return score + n
    if dz == 1:
        return score * n
    if score % n != 0:
        return None
    return score // n


def possible_moves(pos, move_num, score, seen, height, K=None):
    """Yield (next_pos, new_score) for move number move_num from pos.

    height: dict[(x,y)] -> 0 (ground) or 1 (tower); missing = 0.
    """
    x, y = pos
    z = height.get(pos, 0)
    record = must_record(move_num, K)

    candidates = [(d, 0) for d in FLAT_DELTAS] + [(d, 1) for d in STRAIGHT_DELTAS]
    for (dx, dy), need_dz in candidates:
        nxt = (x + dx, y + dy)
        if not in_bounds(*nxt) or nxt in seen:
            continue
        dz = height.get(nxt, 0) - z
        if abs(dz) != need_dz:
            continue

        numbered = nxt in TARGETS
        if record is not None and numbered != record:
            continue

        new_score = apply_score(score, move_num, dz)
        if new_score is None:
            continue
        if record and new_score != TARGETS[nxt]:
            continue

        yield nxt, new_score


def height_of(pos, tower_location):
    return 1 if tower_location.get(towers[pos]) == pos else 0


def moves_with_towers(pos, move_num, score, seen, tower_location, K=None):
    """Like possible_moves, but places towers lazily.

    Towers only sit on path squares (knight visits all of them), so landing on a
    square whose region has no tower yet branches: tower here, or not.
    Yields (next_pos, new_score, new_tower_location).
    """
    x, y = pos
    z = height_of(pos, tower_location)
    record = must_record(move_num, K)

    candidates = [(d, 0) for d in FLAT_DELTAS] + [(d, 1) for d in STRAIGHT_DELTAS]
    for (dx, dy), need_dz in candidates:
        nxt = (x + dx, y + dy)
        if not in_bounds(*nxt) or nxt in seen:
            continue
        numbered = nxt in TARGETS
        if record is not None and numbered != record:
            continue

        tid = towers[nxt]
        if tid in tower_location:
            options = [(height_of(nxt, tower_location), tower_location)]
        else:
            options = [(0, tower_location), (1, {**tower_location, tid: nxt})]

        for nz, tl in options:
            dz = nz - z
            if abs(dz) != need_dz:
                continue
            new_score = apply_score(score, move_num, dz)
            if new_score is None:
                continue
            if record and new_score != TARGETS[nxt]:
                continue
            yield nxt, new_score, tl


def start_states():
    """(path, score, tower_location) at move 0: tower on start square or not."""
    tid = towers[START]
    return [([START], 0, {}), ([START], 0, {tid: START})]


def expand(states, first_move, n_moves, K=None):
    """Advance every state by n_moves hops, starting at move number first_move."""
    for step in range(n_moves):
        move_num = first_move + step
        nxt_states = []
        for path, score, tl in states:
            for nxt, s, ntl in moves_with_towers(path[-1], move_num, score, set(path), tl, K):
                nxt_states.append((path + [nxt], s, ntl))
        states = nxt_states
    return states


def next_chunk(queue, first_move, n_moves=3, K=None):
    """Take states off the front of queue until one expands to something.

    Returns (chosen_state, expanded_states, rest_of_queue).
    chosen_state is None if every state in queue dead-ends.
    """
    queue = list(queue)
    while queue:
        state = queue.pop(0)
        out = expand([state], first_move, n_moves, K)
        if out:
            return state, out, queue
    return None, [], []


N_TOWERS = 13
N_RECORDS_AFTER = 5  # numbers left after move 18


def region_dead(path, tower_location):
    """True if some region has no tower and every one of its squares is visited."""
    visited = set(path)
    for tid in range(N_TOWERS):
        if tid in tower_location:
            continue
        if all(p in visited for p, t in towers.items() if t == tid):
            return True
    return False


def solve_K(states, K, max_nodes=None):
    """DFS from each state (at move 18) for a fixed K. Returns list of full solutions.

    Knight stops the moment it reaches the 13th tower; that must be at or after
    the last record move 18 + 5K.
    """
    last_record = RECORD_UNTIL + N_RECORDS_AFTER * K
    solutions = []
    nodes = 0

    def dfs(path, score, tl):
        nonlocal nodes
        nodes += 1
        if max_nodes and nodes > max_nodes:
            raise RuntimeError(f"node budget hit ({max_nodes})")
        move_num = len(path)  # number of the NEXT move
        if len(tl) == N_TOWERS:
            if move_num - 1 >= last_record:
                solutions.append((path, score, tl))
            return
        if move_num > N * N - 1 or region_dead(path, tl):
            return
        for nxt, s, ntl in moves_with_towers(path[-1], move_num, score, set(path), tl, K):
            dfs(path + [nxt], s, ntl)

    for path, score, tl in states:
        dfs(path, score, tl)
    return solutions, nodes


def save_states(states, fname):
    """Write states as JSON: list of {path: [[x,y],...], score, towers: {id: [x,y]}}."""
    import json
    data = [
        {"path": [list(p) for p in path], "score": score,
         "towers": {str(t): list(p) for t, p in sorted(tl.items())}}
        for path, score, tl in states
    ]
    with open(fname, "w") as f:
        json.dump(data, f)


def load_states(fname):
    """Inverse of save_states -> list of (path, score, tower_location)."""
    import json
    with open(fname) as f:
        data = json.load(f)
    return [
        ([tuple(p) for p in d["path"]], d["score"],
         {int(t): tuple(p) for t, p in d["towers"].items()})
        for d in data
    ]


# ---------- analysis helpers ----------

def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def factorize(n):
    out, d = [], 2
    while d * d <= n:
        while n % d == 0:
            out.append(d)
            n //= d
        d += 1
    if n > 1:
        out.append(n)
    return out


def number_relations():
    vals = sorted(TARGETS.values())
    print("factorizations:")
    for v in vals:
        print(f"  {v:>5}: {factorize(v)}{'  PRIME' if is_prime(v) else ''}")
    print("divisibility (a | b):")
    for a, b in combinations(vals, 2):
        if a > 1 and b % a == 0:
            print(f"  {a} | {b}  (x{b // a})")


def knight_adjacent_numbers():
    """Pairs of numbered squares a flat knight move apart (or straight-2 apart)."""
    pts = list(TARGETS)
    print("flat knight-adjacent number squares:")
    for p, q in combinations(pts, 2):
        d = (abs(p[0] - q[0]), abs(p[1] - q[1]))
        if d in ((1, 2), (2, 1)):
            print(f"  {p}={TARGETS[p]}  <->  {q}={TARGETS[q]}")
    print("straight-2 apart (adjacent only via tower):")
    for p, q in combinations(pts, 2):
        d = (abs(p[0] - q[0]), abs(p[1] - q[1]))
        if d in ((2, 0), (0, 2)):
            print(f"  {p}={TARGETS[p]}  <->  {q}={TARGETS[q]}")


def print_board():
    for y in range(N - 1, -1, -1):
        cells = []
        for x in range(N):
            v = NUMBERS.get((x, y))
            cells.append(f"{REGION[(x, y)]}{'' if v is None else v:<5}")
        print(f"y={y}  " + " ".join(cells))


def print_towers():
    for y in range(N - 1, -1, -1):
        print(f"y={y}  " + " ".join(f"{towers[(x, y)]:>2}" for x in range(N)))
    sizes = {}
    for tid in towers.values():
        sizes[tid] = sizes.get(tid, 0) + 1
    print("squares per tower_id:", dict(sorted(sizes.items())))


if __name__ == "__main__":
    print_board()
    print()
    print_towers()
    print()
    number_relations()
    print()
    knight_adjacent_numbers()
    print()
    print("move 1 options, no towers:", list(possible_moves(START, 1, 0, {START}, {})))
