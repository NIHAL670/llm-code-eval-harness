def merge_intervals(intervals):
    """Merge overlapping (or touching) closed intervals. O(n log n), does not mutate input."""
    for start, end in intervals:
        if start > end:
            raise ValueError(f"invalid interval [{start}, {end}]: start > end")

    merged = []
    for start, end in sorted(intervals, key=lambda iv: iv[0]):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged
