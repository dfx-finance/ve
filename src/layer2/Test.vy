# @version 0.3.7

stored_data: public(uint256)
val: public(uint256)
owner: public(address)

@external
def __init__(_val: uint256, _owner: address):
    """
    Initializes the contract by setting the stored data to a default value.
    """
    self.stored_data = 0

    self.val = _val
    self.owner = _owner

@external
def set(new_value: uint256):
    """
    Sets the value of `stored_data` to a new value.
    """
    self.stored_data = new_value

@view
@external
def get() -> uint256:
    """
    Retrieves the value of `stored_data`.
    """
    return self.stored_data