class NonExistingAttribute(Exception):
    """
    Raised when attempting to access an attribute that does not exist.
    """

    pass


class InconsistentTrapezoidNeighborhood(Exception):
    """
    Raised when there is a consistency issue between trapezoids.

    This occurs when the `trapezoids_above` or `trapezoids_below` attributes
    are not consistent across connected trapezoids.
    """

    pass


class BadVertexOrder(Exception):
    """
    Raised when attempting to create a triangle from three vertices
    that are not in counter-clockwise order.
    """

    pass


class NotATrapezoid(Exception):
    """
    Raised when attempting to call a trapezoid-specific method on a node
    that does not represent a trapezoid.
    """

    pass


class NotTheRoot(Exception):
    """
    Raised when attempting to call a root-specific method on a node that is not
    the root of the search structure.
    """

    pass


class InconsistentArguments(Exception):
    """
    Raised when a method is called with arguments that are logically inconsistent
    or contradictory.
    """

    pass


class NonExistingExtremePoint(Exception):
    """
    Raised when attempting to access the extreme point of a trapezoid
    in a direction where it extends infinitely.
    """

    pass


class InconsistentTrapezoid(Exception):
    """
    Raised when there is a structural inconsistency in a trapezoid.
    """

    pass
