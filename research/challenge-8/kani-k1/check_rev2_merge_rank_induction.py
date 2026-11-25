"""Check the REV2 N32 rank formulas on sorted halves over a small alphabet."""

from itertools import combinations_with_replacement, product


HALF = 16
N = 2 * HALF
ALPHABET = (0, 1, 255)
THRESHOLDS = (0, 1, 2, 255)


def check_pair(left, right):
    source = tuple(
        (value, side, i)
        for side, half in enumerate((left, right))
        for i, value in enumerate(half)
    )
    ranks = sorted(source)
    scratch = [None] * N
    a = b = c = d = 0
    up_tie = down_tie = opposite_read = False

    for k in range(HALF):
        assert a + b == c + d == k
        assert all(0 <= used <= k for used in (a, b, c, d))
        up_left, up_right = source[a], source[HALF + b]
        down_left, down_right = source[HALF - 1 - c], source[N - 1 - d]
        back = N - 1 - k

        up_tie |= up_left[0] == up_right[0]
        down_tie |= down_left[0] == down_right[0]
        opposite_read |= up_left in ranks[N - k :] or up_right in ranks[N - k :]
        opposite_read |= down_left in ranks[:k] or down_right in ranks[:k]

        up_takes_left = up_right[0] >= up_left[0]
        down_takes_left = down_right[0] < down_left[0]
        assert k < back and scratch[k] is None and scratch[back] is None
        scratch[k] = up_left if up_takes_left else up_right
        scratch[back] = down_left if down_takes_left else down_right
        assert scratch[: k + 1] == ranks[: k + 1]
        assert scratch[back:] == ranks[back:]
        assert all(item is None for item in scratch[k + 1 : back])

        a += up_takes_left
        b += not up_takes_left
        c += down_takes_left
        d += not down_takes_left

    assert a == (HALF - 1 - c) + 1
    assert HALF + b == (N - 1 - d) + 1
    assert scratch == ranks
    for q in THRESHOLDS:
        below = sum(value < q for value, _, _ in source)
        mask = sum((value >= q) << i for i, (value, _, _) in enumerate(scratch))
        assert mask == (1 << N) - (1 << below)
        assert all((value < q) == (i < below) for i, (value, _, _) in enumerate(scratch))
    return a, up_tie, down_tie, opposite_read


def main():
    if not __debug__:
        raise SystemExit("Run without Python optimization to enable assertions.")

    halves = tuple(combinations_with_replacement(ALPHABET, HALF))
    cuts = set()
    saw_up_tie = saw_down_tie = saw_opposite_read = False
    for left, right in product(halves, repeat=2):
        cut, up_tie, down_tie, opposite_read = check_pair(left, right)
        cuts.add(cut)
        saw_up_tie |= up_tie
        saw_down_tie |= down_tie
        saw_opposite_read |= opposite_read

    assert cuts == set(range(HALF + 1))
    assert saw_up_tie and saw_down_tie and saw_opposite_read
    print(f"{len(halves) ** 2} pairs; all {len(cuts)} cuts; both ties and opposite-side reads observed")


if __name__ == "__main__":
    main()
