"""
The passenger module contains the Passenger class. It also contains
constants that represent the status of the passenger.

=== Constants ===
WAITING: A constant used for the waiting passenger status.
CANCELLED: A constant used for the cancelled passenger status.
SATISFIED: A constant used for the satisfied passenger status
"""

from location import Location

WAITING = "waiting"
CANCELLED = "cancelled"
SATISFIED = "satisfied"


class Passenger:
    """A passenger for a trip-sharing service.

    === Attributes ===
    id:
        A unique identifier for the passenger.
    patience:
        The amount of time the passenger will wait for a driver.
    origin:
        The initial location of the passenger.
    destination:
        The destination for the passenger.
    status:
        The current status of the passenger.

    === Representation Invariants ===
    -  status: "waited" | "cancelled" | "satisfied"
    """
    id: str
    patience: int
    origin: Location
    destination: Location
    status: str

    def __init__(self, identifier: str, patience: int, origin: Location,
                 destination: Location) -> None:
        """Initialize a Passenger.

        """
        # TO-DO
        self.id = identifier
        self.patience = patience
        self.origin = origin
        self.destination = destination
        self.status = WAITING

    # TO-DO
    def __str__(self) -> str:
        """ Return a string representation.

        """
        return f"ID: {self.id} " \
               f"\nPatience: {self.patience} " \
               f"\nOrigin: {self.origin} " \
               f"\nDestination: {self.destination} " \
               f"\nStatus: {self.status}"

    def status_change(self, new_state: str) -> None:
        """Changes the status of the passenger into a new desired status.

        """
        if new_state == WAITING or CANCELLED or SATISFIED:
            self.status = new_state


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={'extra-imports': ['location']})
