# @version 0.3.3
"""
@title Root-Chain Gauge Delegate
@author Curve Finance
@license MIT
@notice Receives total allocated weekly DFX emission
        mints and sends to L2 gauge
"""
from vyper.interfaces import ERC20


interface GaugeController:
    def token() -> address: view
    def gauge_types(addr: address) -> uint256: view

WEEK: constant(uint256) = 604800

DFX: public(address)
controller: public(address)
distributor: public(address)
start_epoch_time: public(uint256)

period: public(uint256)

admin: public(address)

destinations: public(HashMap[uint256, HashMap[address, address]])  # gauge_type -> gauge_addr -> l2_gauge_addr

@external
def __init__(
    _DFX: address,
    _controller: address,
    _distributor: address,
    _admin: address,
):
    """
    @notice Contract constructor
    @param _DFX Address of the DFX token
    @param _admin Admin who can kill the gauge
    """

    assert _DFX != ZERO_ADDRESS

    self.DFX = _DFX
    self.controller = _controller
    self.distributor = _distributor
    self.admin = _admin

    self.period = block.timestamp / WEEK - 1

@external
def notifyReward(gauge: address, amount: uint256):
    assert msg.sender == self.distributor

    gauge_type: uint256 = GaugeController(self.controller).gauge_types(gauge)

