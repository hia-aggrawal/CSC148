"""Simulation Events

This file should contain all of the classes necessary to model the different
kinds of events in the simulation.
"""
from __future__ import annotations
from typing import List
from rider import Rider, WAITING, CANCELLED, SATISFIED
from dispatcher import Dispatcher
from driver import Driver
from location import deserialize_location
from monitor import Monitor, RIDER, DRIVER, REQUEST, CANCEL, PICKUP, DROPOFF


class Event:
    """An event.

    Events have an ordering that is based on the event timestamp: Events with
    older timestamps are less than those with newer timestamps.

    This class is abstract; subclasses must implement do().

    You may, if you wish, change the API of this class to add
    extra public methods or attributes. Make sure that anything
    you add makes sense for ALL events, and not just a particular
    event type.

    Document any such changes carefully!

    === Attributes ===
    timestamp: A timestamp for this event.
    """

    timestamp: int

    def __init__(self, timestamp: int) -> None:
        """Initialize an Event with a given timestamp.

        Precondition: timestamp must be a non-negative integer.

        >>> Event(7).timestamp
        7
        """
        self.timestamp = timestamp

    # The following six 'magic methods' are overridden to allow for easy
    # comparison of Event instances. All comparisons simply perform the
    # same comparison on the 'timestamp' attribute of the two events.
    def __eq__(self, other: Event) -> bool:
        """Return True iff this Event is equal to <other>.

        Two events are equal iff they have the same timestamp.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first == second
        False
        >>> second.timestamp = first.timestamp
        >>> first == second
        True
        """
        return self.timestamp == other.timestamp

    def __ne__(self, other: Event) -> bool:
        """Return True iff this Event is not equal to <other>.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first != second
        True
        >>> second.timestamp = first.timestamp
        >>> first != second
        False
        """
        return not self == other

    def __lt__(self, other: Event) -> bool:
        """Return True iff this Event is less than <other>.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first < second
        True
        >>> second < first
        False
        """
        return self.timestamp < other.timestamp

    def __le__(self, other: Event) -> bool:
        """Return True iff this Event is less than or equal to <other>.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first <= first
        True
        >>> first <= second
        True
        >>> second <= first
        False
        """
        return self.timestamp <= other.timestamp

    def __gt__(self, other: Event) -> bool:
        """Return True iff this Event is greater than <other>.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first > second
        False
        >>> second > first
        True
        """
        return not self <= other

    def __ge__(self, other: Event) -> bool:
        """Return True iff this Event is greater than or equal to <other>.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first >= first
        True
        >>> first >= second
        False
        >>> second >= first
        True
        """
        return not self < other

    def __str__(self) -> str:
        """Return a string representation of this event.

        """
        raise NotImplementedError("Implemented in a subclass")

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """Do this Event.

        Update the state of the simulation, using the dispatcher, and any
        attributes according to the meaning of the event.

        Notify the monitor of any activities that have occurred during the
        event.

        Return a list of new events spawned by this event (making sure the
        timestamps are correct).

        Note: the "business logic" of what actually happens should not be
        handled in any Event classes.

        """
        raise NotImplementedError("Implemented in a subclass")


class RiderRequest(Event):
    """A rider requests a driver.

    === Attributes ===
    rider: The rider.
    """

    rider: Rider

    def __init__(self, timestamp: int, rider: Rider) -> None:
        """Initialize a RiderRequest event.

        """
        super().__init__(timestamp)
        self.rider = rider

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """Assign the rider to a driver or add the rider to a waiting list.
        If the rider is assigned to a driver, the driver starts driving to
        the rider.

        Return a Cancellation event. If the rider is assigned to a driver,
        also return a Pickup event.

        """
        monitor.notify(self.timestamp, RIDER, REQUEST,
                       self.rider.id, self.rider.origin)

        events = []
        driver = dispatcher.request_driver(self.rider)
        if driver is not None:
            travel_time = driver.start_drive(self.rider.origin)
            events.append(Pickup(self.timestamp + travel_time,
                                 self.rider, driver))
        events.append(Cancellation(self.timestamp + self.rider.patience,
                                   self.rider))
        return events

    def __str__(self) -> str:
        """Return a string representation of this event.

        """
        return "{} -- {}: Request a driver".format(self.timestamp, self.rider)


class DriverRequest(Event):
    """A driver requests a rider.

    === Attributes ===
    driver: The driver.
    """

    driver: Driver

    def __init__(self, timestamp: int, driver: Driver) -> None:
        """Initialize a DriverRequest event.

        """
        super().__init__(timestamp)
        self.driver = driver

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """Register the driver, if this is the first request, and
        assign a rider to the driver, if one is available.

        If a rider is available, return a Pickup event.

        """
        events = []
        # Notify the monitor about the request.
        monitor.notify(self.timestamp, DRIVER,
                       REQUEST, self.driver.id, self.driver.location)
        # Request a rider from the dispatcher.
        rider_available = dispatcher.request_rider(self.driver)
        # If there is one available, the driver starts driving towards the
        if rider_available is not None:
            time = self.driver.start_drive(rider_available.origin)
            events += [Pickup(self.timestamp + time,
                              rider_available, self.driver)]
        # rider, and the method returns a Pickup event for when the driver
        # arrives at the riders location.
        return events

    def __str__(self) -> str:
        """Return a string representation of this event.

        """
        return f"{self.timestamp} -- {self.driver}: Request a rider"


class Cancellation(Event):
    """A rider cancels a trip.

    === Attributes ===
    rider: The rider."""
    # Attribute types
    rider: Rider

    def __init__(self, timestamp: int, rider: Rider) -> None:
        """Intialize a Cancellation event.
        """
        super().__init__(timestamp)
        self.rider = rider

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> []:
        """Cancel the trip for the rider. Notify the monitor accordingly.
        If a rider is satisfied, do nothing.
        """
        if self.rider.status == WAITING:
            dispatcher.cancel_ride(self.rider)
            monitor.notify(self.timestamp, RIDER,
                           CANCEL, self.rider.id, self.rider.origin)
        return []

    def __str__(self) -> str:
        """Return a string representation of this event.

        """
        return f"{self.timestamp} -- {self.rider}: Cancel the ride"


class Pickup(Event):
    """A driver picks up a rider

    === Attributes ===
    rider: a rider
    driver: a driver"""
    # Attribute types
    rider: Rider
    driver: Driver

    def __init__(self, timestamp: int, rider: Rider, driver: Driver) -> None:
        """Initialize a Pickup event."""
        super().__init__(timestamp)
        self.driver = driver
        self.rider = rider

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """Initiate a ride for the driver, if the rider has not cancelled.
        Notify the monitor of the pickup, should there be a ride.
        Return a DriverRequest event if the rider has cancelled
        and return a Dropoff event if the ride has started."""
        events = []
        self.driver.end_drive()
        if self.rider.status == CANCELLED:
            events += [DriverRequest(self.timestamp, self.driver)]
        else:
            time = self.driver.start_ride(self.rider)
            self.rider.status = SATISFIED
            monitor.notify(self.timestamp, DRIVER,
                           PICKUP, self.driver.id, self.rider.origin)
            monitor.notify(self.timestamp, RIDER,
                           PICKUP, self.rider.id, self.rider.origin)
            events += [Dropoff(self.timestamp + time, self.rider, self.driver)]
        return events

    def __str__(self) -> str:
        """Return a string representation of this event.

        """
        return f"{self.timestamp} -- {self.driver}: Pickup the rider"


class Dropoff(Event):
    """A driver drops off a rider.
    === Attributes ===
    rider: a rider
    driver: a driver
    """
    # Attribute types
    rider: Rider
    driver: Driver

    def __init__(self, timestamp: int, rider: Rider, driver: Driver) -> None:
        """Initialize a Dropoff event."""
        super().__init__(timestamp)
        self.driver = driver
        self.rider = rider

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """End the ride for the driver and notify the monitor.
        Return a DriverRequest event."""
        events = []
        self.driver.end_ride()
        monitor.notify(self.timestamp, DRIVER,
                       DROPOFF, self.driver.id, self.driver.location)
        monitor.notify(self.timestamp, RIDER,
                       DROPOFF, self.rider.id, self.rider.origin)
        events += [DriverRequest(self.timestamp, self.driver)]
        return events

    def __str__(self) -> str:
        """Return a string representation of this event.

        """
        return f"{self.timestamp} -- {self.rider} -- " \
               f"{self.driver}: Drop the rider"


def create_event_list(filename: str) -> List[Event]:
    """Return a list of Events based on raw list of events in <filename>.

    Precondition: the file stored at <filename> is in the format specified
    by the assignment handout.

    filename: The name of a file that contains the list of events.
    """
    events = []
    with open(filename, "r") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                # Skip lines that are blank or start with #.
                continue

            # Create a list of words in the line, e.g.
            # ['10', 'RiderRequest', 'Cerise', '4,2', '1,5', '15'].
            # Note that these are strings, and you'll need to convert some
            # of them to a different type.
            tokens = line.split()
            timestamp = int(tokens[0])
            event_type = tokens[1]
            # HINT: Use Location.deserialize to convert the location string to
            # a location.

            if event_type == "DriverRequest":
                driver_id = tokens[2]
                driver_location = deserialize_location(tokens[3])
                driver = Driver(driver_id, driver_location, int(tokens[4]))
                event = DriverRequest(timestamp, driver)
            elif event_type == "RiderRequest":
                rider_id = tokens[2]
                rider_origin = deserialize_location(tokens[3])
                rider_destination = deserialize_location(tokens[4])
                rider = Rider(rider_id, int(tokens[5]),
                              rider_origin, rider_destination)
                event = RiderRequest(timestamp, rider)
            else:
                event = None

            if event is not None:
                events.append(event)

    return events


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(
        config={
            'allowed-io': ['create_event_list'],
            'extra-imports': ['rider', 'dispatcher', 'driver',
                              'location', 'monitor']})
