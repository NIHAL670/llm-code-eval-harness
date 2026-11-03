# Sample response C — correct on small inputs, but sorts the caller's list in place
# and repeatedly rescans until nothing changes (O(n^2) in the worst case).
def merge_intervals(intervals):
    for s, e in intervals:
        if s > e:
            raise ValueError("bad interval")
    intervals.sort()
    merged = [list(iv) for iv in intervals]
    changed = True
    while changed:
        changed = False
        for i in range(len(merged)):
            for j in range(i + 1, len(merged)):
                a, b = merged[i], merged[j]
                if a[0] <= b[1] and b[0] <= a[1]:
                    merged[i] = [min(a[0], b[0]), max(a[1], b[1])]
                    del merged[j]
                    changed = True
                    break
            if changed:
                break
    return merged
