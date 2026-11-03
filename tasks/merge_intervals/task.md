# Task: Merge Intervals

## Prompt given to the model

> Write a Python function `merge_intervals(intervals)` that takes a list of closed integer
> intervals `[start, end]` and returns a new list with all overlapping intervals merged.
>
> Requirements:
> 1. The result must be sorted by start.
> 2. Intervals that **touch** (e.g. `[1, 3]` and `[3, 5]`) count as overlapping and must be merged.
> 3. The input list and its inner lists must **not be modified**.
> 4. Return `[]` for an empty input.
> 5. If any interval has `start > end`, raise `ValueError`.
> 6. The function must handle up to 200,000 intervals in well under a few seconds.
>
> Return only the code.

## Why this task

Interval merging is short, but it has several places where plausible-looking answers go wrong:
touching endpoints (`<` vs `<=`), in-place sorting that silently mutates the caller's data, and
quadratic "merge until nothing changes" loops that pass small tests but time out at scale. A good
rubric must catch each of these independently, so the score explains *which* requirement failed.

## Spec decisions (made explicit to avoid false negatives)

| Ambiguity | Decision |
|---|---|
| Do touching intervals merge? | **Yes** — stated in requirement 2. |
| Output type | `list[list[int]]`; tuples are not accepted for inner items. |
| Invalid interval | `ValueError`, not silent correction. |
| Duplicates / nested intervals | Merged like any other overlap. |
