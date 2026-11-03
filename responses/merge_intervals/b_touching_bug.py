# Sample response B — looks right, but uses `<` instead of `<=`,
# so intervals that only touch ([1,3] and [3,5]) are not merged.
def merge_intervals(intervals):
    if any(s > e for s, e in intervals):
        raise ValueError("each interval must satisfy start <= end")

    result = []
    for start, end in sorted(intervals):
        if result and start < result[-1][1]:
            result[-1][1] = max(result[-1][1], end)
        else:
            result.append([start, end])
    return result
