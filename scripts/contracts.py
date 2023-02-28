#!/usr/bin/env python
import brownie


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
