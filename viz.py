import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from knight import N, NUMBERS, towers


def draw(path, tower_location=None, out="board.png", title=None):
    """Shade visited cells, hop number in top-left corner, numbers centered.

    Towers (if given) marked with a small triangle in the top-right corner.
    """
    tower_location = tower_location or {}
    hop = {p: i for i, p in enumerate(path)}
    tower_squares = set(tower_location.values())

    fig, ax = plt.subplots(figsize=(6, 6))
    for x in range(N):
        for y in range(N):
            p = (x, y)
            color = "#9ecae1" if p in hop else "white"
            ax.add_patch(Rectangle((x, y), 1, 1, facecolor=color, edgecolor="#bbbbbb", lw=0.5))
            if p in hop:
                ax.text(x + 0.06, y + 0.94, str(hop[p]), ha="left", va="top", fontsize=8, color="#08306b")
            if p in NUMBERS:
                ax.text(x + 0.5, y + 0.45, str(NUMBERS[p]), ha="center", va="center", fontsize=12)
            if p in tower_squares:
                ax.plot(x + 0.85, y + 0.85, marker="^", color="#d94801", markersize=7)

    # thick region borders
    for x in range(N):
        for y in range(N):
            if x + 1 < N and towers[(x, y)] != towers[(x + 1, y)]:
                ax.plot([x + 1, x + 1], [y, y + 1], color="black", lw=2.5)
            if y + 1 < N and towers[(x, y)] != towers[(x, y + 1)]:
                ax.plot([x, x + 1], [y + 1, y + 1], color="black", lw=2.5)
    ax.add_patch(Rectangle((0, 0), N, N, fill=False, edgecolor="black", lw=3))

    # path line
    if len(path) > 1:
        xs = [p[0] + 0.5 for p in path]
        ys = [p[1] + 0.5 for p in path]
        ax.plot(xs, ys, color="#08519c", lw=1, alpha=0.5)

    ax.set_xlim(0, N)
    ax.set_ylim(0, N)
    ax.set_xticks([i + 0.5 for i in range(N)], range(N))
    ax.set_yticks([i + 0.5 for i in range(N)], range(N))
    ax.set_aspect("equal")
    if title:
        ax.set_title(title)
    fig.savefig(out, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return out


if __name__ == "__main__":
    from knight import expand, start_states

    states = expand(start_states(), 1, 3)
    path, score, tl = states[0]
    print(draw(path, tl, title=f"after move {len(path) - 1}, score {score}"))
