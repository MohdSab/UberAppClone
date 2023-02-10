"""Locations for the simulation"""

from __future__ import annotations


class Location:
    """A two-dimensional location.

    === Attributes ===
    row:
        A value representing the horizontal index
    col:
        A value representing the vertical index
    """
    row: int
    col: int

    def __init__(self, row: int, column: int) -> None:
        """Initialize a location.

        """
        # TO-DO
        self.row = row
        self.col = column

    def __str__(self) -> str:
        """Return a string representation.

        """
        # TO-DO
        return f"({self.row}, {self.col})"

    def __eq__(self, other: Location) -> bool:
        """Return True if self equals other, and false otherwise.

        """
        # TO-DO
        return self.col == other.col and self.row == other.row


def manhattan_distance(origin: Location, destination: Location) -> int:
    """Return the Manhattan distance between the origin and the destination.

    """
    # TO-DO
    travel_row = abs(destination.row - origin.row)
    travel_col = abs(destination.col - origin.col)
    return travel_col + travel_row


def deserialize_location(location_str: str) -> Location:
    """Deserialize a location.

    location_str: A location in the format 'row,col'
    """
    # TO-DO
    broken_down = location_str.split(',')
    row_int = int(broken_down[0])
    col_int = int(broken_down[1])
    return Location(row_int, col_int)


if __name__ == '__main__':
    import python_ta
    python_ta.check_all()
