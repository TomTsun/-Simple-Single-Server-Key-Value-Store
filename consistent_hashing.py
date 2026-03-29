import hashlib
import bisect

class ConsistentHashRing:
    def __init__(self, nodes=None, replicas=100):
        self.replicas = replicas
        self.ring = {}
        self.sorted_keys = []
        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key: str) -> int:
        """Standard MD5 hash to determine position on the 0 to 2^128 ring."""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add_node(self, node: str):
        """Adds a node and its virtual replicas to the ring."""
        for i in range(self.replicas):
            h_key = self._hash(f"{node}:{i}")
            self.ring[h_key] = node
            bisect.insort(self.sorted_keys, h_key)

    def remove_node(self, node: str):
        """Removes a node and all its virtual replicas."""
        for i in range(self.replicas):
            h_key = self._hash(f"{node}:{i}")
            self.ring.pop(h_key)
            self.sorted_keys.remove(h_key)

    def get_node(self, key: str) -> str:
        """Finds the first node clockwise from the key's hash position."""
        if not self.ring:
            return None
        h_key = self._hash(key)
        idx = bisect.bisect_left(self.sorted_keys, h_key)
        # Wrap around to the start of the ring if at the end
        return self.ring[self.sorted_keys[idx % len(self.sorted_keys)]]