class MaxHeap:
    """Custom Binary Max Heap for task priority scheduling."""

    def __init__(self):
        self.heap = []

    def __len__(self):
        return len(self.heap)

    def is_empty(self):
        return len(self.heap) == 0

    @staticmethod
    def _higher_priority(a, b):
        if a["score"] != b["score"]:
            return a["score"] > b["score"]

        if a["deadline"] != b["deadline"]:
            return a["deadline"] < b["deadline"]

        return a["id"] < b["id"]

    def push(self, item):
        self.heap.append(item)
        self._heapify_up(len(self.heap) - 1)

    def peek(self):
        return self.heap[0] if self.heap else None

    def pop(self):
        if not self.heap:
            return None

        if len(self.heap) == 1:
            return self.heap.pop()

        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        return root

    def _heapify_up(self, index):
        while index > 0:
            parent = (index - 1) // 2

            if self._higher_priority(
                self.heap[index], self.heap[parent]
            ):
                self.heap[index], self.heap[parent] = (
                    self.heap[parent], self.heap[index]
                )
                index = parent
            else:
                break

    def _heapify_down(self, index):
        size = len(self.heap)

        while True:
            left = 2 * index + 1
            right = 2 * index + 2
            highest = index

            if left < size and self._higher_priority(
                self.heap[left], self.heap[highest]
            ):
                highest = left

            if right < size and self._higher_priority(
                self.heap[right], self.heap[highest]
            ):
                highest = right

            if highest == index:
                break

            self.heap[index], self.heap[highest] = (
                self.heap[highest], self.heap[index]
            )
            index = highest