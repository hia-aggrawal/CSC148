"""Locations for the simulation"""

from __future__ import annotations


class Location:
    """A two-dimensional location.
    === Attributes ===
    location: location of the vehicle. (number of blocks from
    the bottom edge, number of blocks from the left edge."""
    # Attribute types
    location: tuple[int, int]

    def __init__(self, row: int, column: int) -> None:
        """Initialize a location.

        """
        self.location = (row, column)

    def __str__(self) -> str:
        """Return a string representation.

        """
        return f'({self.location[0]},{self.location[1]})'

    def __eq__(self, other: Location) -> bool:
        """Return True if self equals other, and false otherwise.

        """
        return self.location == other.location


def manhattan_distance(origin: Location, destination: Location) -> int:
    """Return the Manhattan distance between the origin and the destination.

    """
    x_distance = abs(origin.location[0] - destination.location[0])
    y_distance = abs(origin.location[1] - destination.location[1])
    return x_distance + y_distance


def deserialize_location(location_str: str) -> Location:
    """Deserialize a location.

    location_str: A location in the format 'row,col'
    """
    row, col = location_str.split(",")
    row, col = int(row), int(col)
    return Location(row, col)


if __name__ == '__main__':
    import python_ta
    python_ta.check_all()
