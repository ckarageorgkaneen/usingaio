# Example 3-19. A utility function for coercing input into a list
from typing import Any, List


def listify(x: Any) -> List:
    """ Try hard to convert x into a list """
    if isinstance(x, (str, bytes)):
        return [x]
    try:
        return [_ for _ in x]
    except TypeError:
        return [x]
