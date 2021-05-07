def get_bit(num: int, index: int) -> bool:
    """
    Get the index-th bit of num.
    """
    mask = 1 << index
    return bool(num & mask)


def set_bit(num: int, index: int, value: bool) -> int:
    """
    Set the index-th bit of num to 1 if value is truthy, else to 0, and return the new value.
    From https://stackoverflow.com/a/12174051/1076564 .
    """
    mask = 1 << index   # Compute mask, an integer with just bit 'index' set.
    num &= ~mask          # Clear the bit indicated by the mask (if x is False)
    if value:
        num |= mask         # If x was True, set the bit indicated by the mask.
    return num            # Return the result, we're done.
