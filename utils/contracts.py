#!/usr/bin/env python
import brownie
import json

from .network import get_network_addresses


def voting_escrow(address):
    return brownie.interface.IVotingEscrow(address)


def veboost_proxy(address):
    return brownie.interface.IVeBoostProxy(address)


def gauge_controller(address):
    return brownie.interface.IGaugeController(address)


def dfx_distributor(address):
    return brownie.interface.IDfxDistributor(address)


def gauge(address):
    return brownie.interface.ILiquidityGauge(address)


def dfx_curve(address):
    return brownie.interface.IDfxCurve(address)


def erc20(address):
    return brownie.interface.IERC20(address)


def load_dfx_token():
    addrs = get_network_addresses()
    abi = json.load(open("./tests/abis/Dfx.json"))
    return brownie.Contract.from_abi("DFX", addrs.DFX, abi)
