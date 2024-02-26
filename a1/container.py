"""Containers of objects"""


class Container:
    """A container that holds objects.

    This is an abstract class.  Only child classes should be instantiated.
    """

    def add(self, item: object) -> None:
        """Add <item> to this Container.

        """
        raise NotImplementedError("Implemented in a subclass")

    def remove(self) -> object:
        """Remove and return a single item from this Container.

        """
        raise NotImplementedError("Implemented in a subclass")

    def is_empty(self) -> bool:
        """Return True iff this Container is empty.

        """
        raise NotImplementedError("Implemented in a subclass")


class PriorityQueue(Container):
    """A queue of items that operates in priority order.

    Items are removed from the queue according to priority; the item with the
    highest priority is removed first. Ties (between same priority) are
    resolved in FIFO order,
    meaning the item which was inserted *earlier* is the first one to be
    removed.

    Priority is defined by the rich comparison methods for the objects in the
    container (__lt__, __le__, __gt__, __ge__).

    If x < y, then x has a *HIGHER* priority than y.

    All objects in the container must be of the same type.
    """

    # === Private Attributes ===
    _items: list
    #     The items stored in the priority queue.
    #
    # === Representation Invariants ===
    # _items is a sorted list, where the first item in the queue is the
    # item with the highest priority.

    def __init__(self) -> None:
        """Initialize an empty PriorityQueue.

        """
        self._items = []

    def remove(self) -> object:
        """Remove and return the next item from this PriorityQueue.

        Precondition: <self> should not be empty.

        >>> pq = PriorityQueue()
        >>> pq.add("red")
        >>> pq.add("blue")
        >>> pq.add("yellow")
        >>> pq.add("green")
        >>> pq.remove()
        'blue'
        >>> pq.remove()
        'green'
        >>> pq.remove()
        'red'
        >>> pq.remove()
        'yellow'
        """
        priority_item = self._items[0]
        for item in self._items:
            if item.__lt__(priority_item):
                priority_item = item
        self._items.remove(priority_item)
        return priority_item

    def is_empty(self) -> bool:
        """
        Return true iff this PriorityQueue is empty.

        >>> pq = PriorityQueue()
        >>> pq.is_empty()
        True
        >>> pq.add("thing")
        >>> pq.is_empty()
        False
        """
        return len(self._items) == 0

    def add(self, item: object) -> None:
        """Add <item> to this PriorityQueue.

        >>> pq = PriorityQueue()
        >>> pq.add("yellow")
        >>> pq.add("blue")
        >>> pq.add("red")
        >>> pq.add("green")
        >>> pq._items
        ['blue', 'green', 'red', 'yellow']
        """
        if self.is_empty():
            self._items.append(item)
        else:
            i = 0
            while i < len(self._items):
                if item.__lt__(self._items[i]):
                    self._items.insert(i, item)
                    return
                elif item.__le__(self._items[i]):
                    self._items.insert(i + 1, item)
                    return
                i += 1
            if item not in self._items:
                self._items.append(item)

        # ["yellow"]
        # ["blue", "yellow"]
        # ["blue", "red", "yellow"]
        # ["blue", "green", "red", "yellow"]


if __name__ == '__main__':
    import python_ta
    python_ta.check_all()
