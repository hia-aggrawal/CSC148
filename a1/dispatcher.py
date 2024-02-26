"""Dispatcher for the simulation"""

from typing import Optional
from driver import Driver
from rider import Rider


class Dispatcher:
    """A dispatcher fulfills requests from riders and drivers for a
    ride-sharing service.

    When a rider requests a driver, the dispatcher assigns a driver to the
    rider. If no driver is available, the rider is placed on a waiting
    list for the next available driver. A rider that has not yet been
    picked up by a driver may cancel their request.

    When a driver requests a rider, the dispatcher assigns a rider from
    the waiting list to the driver. If there is no rider on the waiting list
    the dispatcher does nothing. Once a driver requests a rider, the driver
    is registered with the dispatcher, and will be used to fulfill future
    rider requests.
    """
    # # === Private Attributes ===
    # _riders_waiting: a priority-based waiting list for riders
    # _drivers: a list of drivers available to pickup

    # Attribute types
    _riders_waiting: list
    _drivers: list

    def __init__(self) -> None:
        """Initialize a Dispatcher.

        """
        self._riders_waiting = []
        self._drivers = []

    def __str__(self) -> str:
        """Return a string representation.

        """
        return f"There are {len(self._riders_waiting)} riders waiting and " \
               f"{len(self._drivers)} drivers are to pick up."

    def request_driver(self, rider: Rider) -> Optional[Driver]:
        """Return a driver for the rider, or None if no driver is available.

        Add the rider to the waiting list if there is no available driver.

        """
        min_distance = float('inf')
        chosen_driver = None
        for driver in self._drivers:
            distance = driver.get_travel_time(rider.origin)
            if distance < min_distance:
                min_distance = distance
                chosen_driver = driver
        if chosen_driver is None and rider not in self._riders_waiting:
            self._riders_waiting.append(rider)
        if chosen_driver is not None:
            return chosen_driver
        else:
            return None

    def request_rider(self, driver: Driver) -> Optional[Rider]:
        """Return a rider for the driver, or None if no rider is available.

        If this is a new driver, register the driver for future rider requests.

        """
        if driver not in self._drivers:
            self._drivers.append(driver)
        if self._riders_waiting != []:
            return self._riders_waiting.pop(0)
        else:
            return None

    def cancel_ride(self, rider: Rider) -> None:
        """Cancel the ride for rider.

        """
        rider.status = "cancelled"
        if rider in self._riders_waiting:
            self._riders_waiting.remove(rider)


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={'extra-imports': ['typing', 'driver', 'rider']})
