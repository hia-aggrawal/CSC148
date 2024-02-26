"""
The rider module contains the Rider class. It also contains
constants that represent the status of the rider.

=== Constants ===
WAITING: A constant used for the waiting rider status.
CANCELLED: A constant used for the cancelled rider status.
SATISFIED: A constant used for the satisfied rider status
"""

from location import Location

WAITING = "waiting"
CANCELLED = "cancelled"
SATISFIED = "satisfied"


class Rider:

    """A rider for a ride-sharing service.
    === Attributes ===
    id: a unique id associated with the rider
    origin: the initial location of the rider
    destination: the final (desired) location of the rider
    patience: the time units that rider will wait before they cancel their trip
    status: the mood of the rider; it is either waiting, cancelled or satisfied.
    """
    # Attribute types
    id: str
    origin: Location
    destination: Location
    patience: int
    status: str

    def __init__(self, identifier: str, patience: int, origin: Location,
                 destination: Location) -> None:
        """Initialize a Rider.

        """
        self.id = identifier
        self.origin = origin
        self.destination = destination
        self.patience = patience
        self.status = WAITING


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={'extra-imports': ['location']})
