# Task: LRU Cache

## Prompt given to the model

> Implement a class `LRUCache` in Python:
>
> - `LRUCache(capacity)` — create a cache holding at most `capacity` items. Raise `ValueError` if `capacity <= 0`.
> - `get(key)` — return the value for `key`, or `-1` if absent. A successful `get` marks the key as **most recently used**.
> - `put(key, value)` — insert or update `key`. Updating an existing key also marks it most recently used.
>   If inserting a new key would exceed capacity, evict the **least recently used** key first.
> - Both operations must run in **O(1)** average time.
>
> Return only the code.

## Why this task

The classic failure modes are behavioural, not syntactic: forgetting that `get` refreshes recency,
treating an update as a new insert (evicting the wrong key), and list-based implementations that are
correct but O(n) per operation. The rubric isolates each one, plus a seeded randomized check against a
reference implementation to catch anything the targeted checks miss.

## Spec decisions

| Ambiguity | Decision |
|---|---|
| Does `get` on a missing key change order? | No. |
| Does `put` on an existing key count as "use"? | Yes — it becomes most recently used. |
| Missing-key return value | `-1` (keys and values in tests are non-negative ints). |
