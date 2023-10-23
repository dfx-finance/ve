# @version 0.3.3
"""
@title Root-Chain Gauge CCTP Transfer
@author DFX Finance
@license MIT
@notice Receives total allocated weekly DFX emission
        mints and sends to L2 gauge
"""
from vyper.interfaces import ERC20


struct EVMTokenAmount:
    token: address # token address on the local chain.
    amount: uint256 # Amount of tokens.

struct EVM2AnyMessage:
    receiver: Bytes[32] # abi.encode(receiver address) for dest EVM chains
    data: Bytes[32] # Data payload
    tokenAmounts: EVMTokenAmount[1] # Token transfers
    feeToken: address # Address of feeToken. address(0) means you will send msg.value.
    extraArgs: Bytes[32] # Populate this with _argsToBytes(EVMExtraArgsV1)

interface CctpRouter:
    def ccipSend(chain_selector: uint256, message: EVM2AnyMessage): payable
    def getFee(chain_selector: uint256, message: EVM2AnyMessage) -> uint256: pure

WEEK: constant(uint256) = 604800

name: public(String[64])
symbol: public(String[32])

DFX: public(address)
controller: public(address)
distributor: public(address)
start_epoch_time: public(uint256)

period: public(uint256)

admin: public(address)

router: public(address)
destination_chain: public(uint256)
destination: public(address)
fee_token: public(address)

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
    _distributor: address,
    _router: address,
    _destinationChain: uint256,
    _destination: address,
    _feeToken: address,
    _admin: address,
):
    """
    @notice Contract initializer
    @param _symbol Gauge base symbol
    @param _DFX Address of the DFX token
    @param _distributor Address of the mainnet rewards distributor
    @param _router Address of the CCIP message router
    @param _destinationChain Chain ID of the chain with the destination gauge. CCIP uses its own set of chain selectors to identify blockchains
    @param _destination Address of the destination gauge on the sidechain
    @param _admin Admin who can kill the gauge
    """

    assert _DFX != ZERO_ADDRESS

    self.name = concat("DFX ", _symbol, " Gauge")
    self.symbol = concat(_symbol, "-gauge")    

    self.DFX = _DFX
    self.distributor = _distributor
    self.router = _router
    self.destination_chain = _destinationChain # destination chain selector
    self.destination = _destination # destination address on l2
    self.fee_token = _feeToken
    self.admin = _admin

    self.period = block.timestamp / WEEK - 1


@external
def update_destination(_new_destination: address):
    assert msg.sender == self.admin

    self.destination = _new_destination

@external
def update_distributor(_new_distributor: address):
    assert msg.sender == self.admin

    self.distributor = _new_distributor

@internal
def _notify_reward(amount: uint256):
    assert msg.sender == self.distributor

    self.start_epoch_time = block.timestamp

    token: ERC20 = ERC20(self.DFX)
    router: CctpRouter = CctpRouter(self.router)

    # Max approve spending of rewards tokens by router
    if token.allowance(self, router.address) < amount:
        token.approve(router.address, MAX_UINT256)


    message: EVM2AnyMessage = EVM2AnyMessage({
        receiver: _abi_encode(self.destination),
        data: empty(Bytes[32]),  # no data
        tokenAmounts: [
            EVMTokenAmount({
                token: self.DFX,
                amount: amount,
            })            
        ],
        feeToken: self.fee_token,
        extraArgs: empty(Bytes[32])
    })

    fees: uint256 = router.getFee(self.destination_chain, message)

    # When fee token is set, send messages across CCIP using token. Otherwise,
    # use the native gas token
    if self.fee_token != ZERO_ADDRESS:
        fee_token: ERC20 = ERC20(self.fee_token)
        
        # Max approve spending of gas tokens by router
        if fee_token.allowance(self, router.address) < fees:
            fee_token.approve(router.address, MAX_UINT256)

        router.ccipSend(self.destination_chain, message)
    else:
        router.ccipSend(self.destination_chain, message, value=fees)    

@external
def notify_reward(amount: uint256):
    self._notify_reward(amount)

@external
def notifyReward(gauge: address, amount: uint256):
    # gaugeAddr parameter for compatibility, but unused
    self._notify_reward(amount)

@view
@external
def test_fee(amount: uint256) -> EVM2AnyMessage:
    router: CctpRouter = CctpRouter(self.router)

    message: EVM2AnyMessage = EVM2AnyMessage({
        receiver: _abi_encode(self.destination),
        data: empty(Bytes[32]),  # no data
        tokenAmounts: [EVMTokenAmount({
            token: self.DFX,
            amount: amount,
        })],
        feeToken: self.fee_token,
        extraArgs: empty(Bytes[32])
    })
    # fees: uint256 = router.getFee(self.destination_chain, message)
    return message


@external
def emergency_withdraw(_token: address, _amount: uint256):
    """
    @notice Emergency withdraw
    @param _token Address of token to withdraw
    """    
    assert msg.sender == self.admin
    ERC20(_token).transfer(self.admin, _amount)
