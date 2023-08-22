# @version 0.3.3
"""
@title Root-Chain Gauge CCTP Transfer
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

name: public(String[64])
symbol: public(String[32])

DFX: public(address)
controller: public(address)
distributor: public(address)
start_epoch_time: public(uint256)

period: public(uint256)

admin: public(address)

destinationChain: public(uint256)
destination: public(address)

initialized: public(bool)

@external
def __init__():
    """
    @notice Contract constructor
    @dev The contract has an initializer to prevent the take over of the implementation
    """
    assert self.initialized == False #dev: contract is already initialized
    self.initialized = True


@external
def initialize(
    _symbol: String[26],
    _DFX: address,
    _controller: address,
    _distributor: address,
    _destinationChain: uint256,
    _destination: address,
    _admin: address,
):
    """
    @notice Contract initializer
    @param _symbol Gauge base symbol
    @param _DFX Address of the DFX token
    @param _controller Address of the mainnet gauge controller
    @param _distributor Address of the mainnet rewards distributor
    @param _destinationChain Chain ID of the chain with the destination gauge
    @param _destination Address of the destination gauge on the sidechain
    @param _admin Admin who can kill the gauge
    """

    assert _DFX != ZERO_ADDRESS

    self.name = concat("DFX ", _symbol, " Gauge")
    self.symbol = concat(_symbol, "-gauge")    

    self.DFX = _DFX
    self.controller = _controller
    self.distributor = _distributor
    self.destinationChain = _destinationChain
    self.destination = _destination # destination address on l2
    self.admin = _admin

    self.period = block.timestamp / WEEK - 1

@external
def update_destination(_addr: address):
    pass

@external
def notifyReward(gauge: address, amount: uint256):
    assert msg.sender == self.distributor

    # gauge_type: uint256 = GaugeController(self.controller).gauge_types(gauge)

    # CCTP logic here
    token: ERC20 = ERC20(self.DFX)
    rewards: uint256 = token.balanceOf(self)
    token.transfer(self.destination, rewards)
    
