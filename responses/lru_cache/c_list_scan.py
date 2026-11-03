# Sample response C — behaviourally correct, but tracks order in a Python list,
# so every get/put does an O(n) list.remove(). Fine for tiny caches, far too slow at scale.
class LRUCache:
    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        self.capacity = capacity
        self.values = {}
        self.order = []  # least recently used at index 0

    def get(self, key):
        if key not in self.values:
            return -1
        self.order.remove(key)
        self.order.append(key)
        return self.values[key]

    def put(self, key, value):
        if key in self.values:
            self.order.remove(key)
        elif len(self.values) >= self.capacity:
            oldest = self.order.pop(0)
            del self.values[oldest]
        self.values[key] = value
        self.order.append(key)
