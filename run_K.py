import time
from knight import load_states, solve_K, save_states

states = load_states("states_18.json")
for K in range(4, 9):
    t = time.time()
    sols, nodes = solve_K(states, K, max_nodes=20_000_000)
    print(f"K={K}: {len(sols)} solutions, {nodes} nodes, {time.time() - t:.1f}s")
    if sols:
        save_states(sols, f"solutions_K{K}.json")
