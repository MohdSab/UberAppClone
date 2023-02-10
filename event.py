"""Simulation Events

This file should contain all of the classes necessary to model the different
kinds of original events in the simulation.
"""
from __future__ import annotations
from typing import List
from passenger import Passenger, WAITING, CANCELLED, SATISFIED
from dispatcher import Dispatcher
from driver import Driver
from location import deserialize_location
from monitor import Monitor, PASSENGER, DRIVER, REQUEST, CANCEL, PICKUP, DROPOFF


class Event:
    """An event.

    Events have an ordering that is based on the event timestamp: Events with
    older timestamps are less than those with newer timestamps.

    This class is abstract; subclasses must implement do().

    You may, if you wish, change the API of this class to add
    extra public methods or attributes. Make sure that anything
    you add makes sense for ALL original events, and not just a particular
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
    # same comparison on the 'timestamp' attribute of the two original events.
    def __eq__(self, other: Event) -> bool:
        """Return True iff this Event is equal to <other>.

        Two original events are equal iff they have the same timestamp.

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

        Return a list of new original events spawned by this event (making
        sure the
        timestamps are correct).

        Note: the "business logic" of what actually happens should not be
        handled in any Event classes.

        """
        raise NotImplementedError("Implemented in a subclass")


class PassengerRequest(Event):
    """A passenger requests a driver.

    === Attributes ===
    passenger: The passenger.
    """

    passenger: Passenger

    def __init__(self, timestamp: int, passenger: Passenger) -> None:
        """Initialize a PassengerRequest event.

        """
        super().__init__(timestamp)
        self.passenger = passenger

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """Assign the passenger to a driver or add the passenger to a
        waiting list.
        If the passenger is assigned to a driver, the driver starts driving to
        the passenger.

        Return a Cancellation event. If the passenger is assigned to a driver,
        also return a Pickup event.

        """
        monitor.notify(self.timestamp, PASSENGER, REQUEST,
                       self.passenger.id, self.passenger.origin)

        events = []
        driver = dispatcher.request_driver(self.passenger)
        if driver is not None:
            travel_time = driver.start_drive(self.passenger.origin)
            events.append(Pickup(self.timestamp + travel_time,
                                 self.passenger, driver))
        events.append(Cancellation(self.timestamp + self.passenger.patience,
                                   self.passenger))
        return events

    def __str__(self) -> str:
        """Return a string representation of this event.

        """
        return f"{self.timestamp} -- {self.passenger}: Request a driver"


class DriverRequest(Event):
    """A driver requests a passenger.

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
        assign a passenger to the driver, if one is available.

        If a passenger is available, return a Pickup event.

        """
        # Notify the monitor about the request.

        # Request a passenger from the dispatcher.
        # If there is one available, the driver starts driving towards the
        # passenger, and the method returns a Pickup event for when the driver
        # arrives at the passengers location.
        # TO-DO
        monitor.notify(self.timestamp, DRIVER, REQUEST,
                       self.driver.id, self.driver.location)

        events = []
        passenger = dispatcher.request_passenger(self.driver)
        if passenger is not None:
            self.driver.is_idle = False
            travel_time = self.driver.start_drive(passenger.origin)
            if passenger.status is not CANCELLED:
                events.append(Pickup(self.timestamp + travel_time,
                                     passenger, self.driver))
        else:
            self.driver.is_idle = True
        return events

    def __str__(self) -> str:
        """Return a string representation of this event.

        """
        return f"{self.timestamp} -- {self.driver}: Request a passenger"


class Cancellation(Event):
    # TO-DO
    """The passenger patience has run low and cancels the trip.
    The driver arrives to passenger origin but does not find
    the passenger to pickup.

    === Attributes ===
    passenger: the cancelling passenger with no patience

    """

    passenger: Passenger

    def __init__(self, timestamp: int, passenger: Passenger) -> None:
        """Initialize the cancellation request.

        """
        super().__init__(timestamp)
        self.passenger = passenger

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """Cancel the trip is the passenger patience has run out.
        Notify the monitor of the event, and do nothing if the status of
        the passenger is satisfied.

        If the patience has run out, return a cancellation event.

        """
        if self.passenger.status == WAITING:
            self.passenger.status = CANCELLED
            monitor.notify(self.timestamp, PASSENGER, CANCEL, self.passenger.id,
                           self.passenger.origin)
            dispatcher.cancel_ride(self.passenger)
        return []

    def __str__(self) -> str:
        """Return a string representation of the cancellation event.

        """
        return f"{self.timestamp} -- {self.passenger.id}: Passenger Cancelled"


class Pickup(Event):
    # TO-DO
    """The Driver arrives to the passenger origin within
    the passenger patience limit.
    Notify the monitor of the event,
    change the statues of the passenger to satisfied,
    and set driver destination to the passenger destination.

    === Attributes ===
    passenger: the passenger getting picked up, within their patience meter
    driver: driver that picks up the passenger

    """
    passenger: Passenger
    driver: Driver

    def __init__(self, timestamp: int,
                 passenger: Passenger, driver: Driver) -> None:
        """Initialize the pickup event.

        """
        super().__init__(timestamp)
        self.passenger = passenger
        self.driver = driver

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """Set the driver location to the passenger origin.
        If the passenger statues is waiting, the driver destination become the
        passenger destination.

        A dropoff event is also created with timestamp of pickup + driving time.

        Change the passenger status to satisfied.

        If Passenger status is cancelled, set a new event for the driver
        requesting a new passenger, and the driver destination becomes None.

        """
        events = []
        self.driver.location = self.passenger.origin
        self.driver.end_drive()
        if self.passenger.status == WAITING:
            travel_time = self.driver.start_trip(self.passenger)
            events.append(Dropoff(self.timestamp + travel_time,
                                  self.passenger, self.driver))
            self.passenger.status = SATISFIED
            monitor.notify(self.timestamp, DRIVER, PICKUP, self.driver.id,
                           self.passenger.origin)
            monitor.notify(self.timestamp, PASSENGER, PICKUP, self.passenger.id,
                           self.passenger.origin)
        else:
            self.driver.end_drive()
            self.driver.is_idle = True
            self.driver.location = self.passenger.origin
            events.append(DriverRequest(self.timestamp, self.driver))
        return events

    def __str__(self) -> str:
        """Return string representation of the pickup event

        """
        return f"{self.timestamp} -- {self.driver.id}: Driver Picked Up" \
               f" {self.passenger.id}"


class Dropoff(Event):
    # TO-DO
    """The driver drops off the passenger at their desired destination.
    The location of the driver is updated as well as their passenger.

    === Attributes ===
    passenger: the passenger that is getting dropped off.
    driver: the driver that just finished the trip.

    """
    passenger: Passenger
    driver: Driver

    def __init__(self, timestamp: int,
                 passenger: Passenger, driver: Driver) -> None:
        """Initialize the drop off event.

        """
        super().__init__(timestamp)
        self.passenger = passenger
        self.driver = driver

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """Arrive to the passenger destination.
        Notify the monitor of this event.
        Driver become idle (with no destination) and looks for more work.

        """
        events = []
        if self.passenger.status is not CANCELLED:
            monitor.notify(self.timestamp, DRIVER, DROPOFF,
                           self.driver.id, self.passenger.destination)

            self.driver.end_trip()
            self.driver.location = self.passenger.destination
            self.driver.is_idle = True

        events.append(DriverRequest(self.timestamp, self.driver))
        return events

    def __str__(self) -> str:
        """ Return the string representation of the dropoff event

        """
        return f"{self.timestamp} -- {self.driver.id}: Driver Dropped Off " \
               f"{self.passenger.id}"


def create_event_list(filename: str) -> List[Event]:
    """Return a list of Events based on raw list of original events
    in <filename>.

    Precondition: the file stored at <filename> is in the format specified
    by the assignment handout.

    filename: The name of a file that contains the list of original events.
    """
    events = []
    with open(filename, "r") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                # Skip lines that are blank or start with #.
                continue

            # Create a list of words in the line, e.g.
            # ['10', 'PassengerRequest', 'Cerise', '4,2', '1,5', '15'].
            # Note that these are strings, and you'll need to convert some
            # of them to a different type.
            tokens = line.split()
            timestamp = int(tokens[0])
            event_type = tokens[1]

            # HINT: Use Location.deserialize to convert the location string to
            # a location.
            event = []
            if event_type == "DriverRequest":
                # TO-DO
                # Create a DriverRequest event.
                event = DriverRequest(
                    timestamp,
                    Driver(tokens[2],
                           deserialize_location(tokens[3]),
                           int(tokens[4])))

            elif event_type == "PassengerRequest":
                # TO-DO
                # Create a PassengerRequest event.
                event = PassengerRequest(
                    timestamp,
                    Passenger(tokens[2],
                              int(tokens[5]),
                              deserialize_location(tokens[3]),
                              deserialize_location(tokens[4])))

            events.append(event)

    return events


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(
        config={
            'allowed-io': ['create_event_list'],
            'extra-imports': ['passenger', 'dispatcher', 'driver',
                              'location', 'monitor']})
