# VeDFX Contracts

This veDFX is an implementation of Curve's Vote Escrow + Gauge contracts in Vyper. These use Vyper
for smart contract code and brownie + ganache for testing and deployments.
![veDFX](https://user-images.githubusercontent.com/25423613/178617916-680ef134-c076-4e9b-a946-c26b557d27f5.png)

Implementation working doc: https://docs.google.com/document/d/1t5nprPEhhA1amXQ8VWf-PuXaP0dcPcHz2an-eM0Lg2o/

Calculations on VE emissions: https://docs.google.com/spreadsheets/d/1k1yAvAW_a6bHn4slPboGRl8ONsBEvO66YMWSOva_7MM/edit?usp=sharing

### References

1. https://eth-brownie.readthedocs.io
2. https://developers.angle.money/governance-and-cross-module-contracts/governance-contracts/gauge-controller
3. https://github.com/curvefi/curve-dao-contracts/

### External Audits

#### Curve:

1. https://curve.fi/files/00-ToB.pdf
2. https://curve.fi/files/01-ToB.pdf

#### Angle:

1. https://github.com/AngleProtocol/angle-core/blob/main/audits/Sigma%20Prime%20Audit%20Report%20July%2021.pdf
2. https://github.com/AngleProtocol/angle-core/blob/main/audits/Chainsecurity%20Audit%20Report%20December%2021.pdf

## Getting Started

1. [Testing of VE Contracts](./docs/testing.md)
2. [Deploy VE Contracts](./docs/deploy.md)
3. [Operation Guide](./docs/operation.md)
