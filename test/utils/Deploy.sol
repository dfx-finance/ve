// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@snekmate/utils/VyperDeployer.sol";

import "../../src/DfxUpgradeableProxy.sol";
import "../../src/interfaces/IGaugeController.sol";
import "../../src/interfaces/IVeDfx.sol";
import "../../src/interfaces/IVeBoostProxy.sol";
import "../../src/interfaces/ILiquidityGaugeV4.sol";
import "../../src/mainnet/CcipRootGauge.sol";
import "../../src/mainnet/CcipSender.sol";
import "../../src/mainnet/DfxDistributor.sol";
import {DFX as DFX_} from "../../src/mocks/DFX.sol";
import "../../src/mocks/MockCcipRouter.sol";

import "./Constants.sol";

contract Deploy is Constants {
    VyperDeployer vyperDeployer = new VyperDeployer();

    function deployDfx(uint256 mintAmount) public returns (DFX_) {
        return new DFX_(mintAmount);
    }

    function deployLpt(string memory name, string memory symbol) public returns (IERC20) {
        return IERC20(vyperDeployer.deployContract("src/mocks/", "ERC20LP", abi.encode(name, symbol, 18, 1e9)));
    }

    function deployVeDfx(address DFX) public returns (IVeDfx) {
        return
            IVeDfx(vyperDeployer.deployContract("src/mocks/", "MockVeDFX", abi.encode(DFX, "veDFX", "veDFX", "0.0.1")));
    }

    function deployVeBoostProxy(address veDFX, address admin) public returns (IVeBoostProxy) {
        return IVeBoostProxy(
            vyperDeployer.deployContract("src/mainnet/", "VeBoostProxy", abi.encode(veDFX, address(0), admin))
        );
    }

    function deployGaugeController(address DFX, address veDFX, address admin) public returns (IGaugeController) {
        return IGaugeController(
            vyperDeployer.deployContract(
                "src/mainnet/", "GaugeController", abi.encode(address(DFX), address(veDFX), admin)
            )
        );
    }

    function deployDistributor(address DFX, address gaugeController, address admin0, address admin1, address proxyAdmin)
        public
        returns (DfxDistributor)
    {
        // Deploy DfxDistributor logic
        DfxDistributor _distributor = new DfxDistributor();

        // Deploy DfxDistributor proxy
        bytes memory params = abi.encodeWithSelector(
            DfxDistributor.initialize.selector, address(DFX), address(gaugeController), 0, 0, admin0, admin1, address(0)
        );
        DfxUpgradeableProxy proxy = new DfxUpgradeableProxy(address(_distributor), proxyAdmin, params);
        return DfxDistributor(address(proxy));
    }

    function deployMockCcipRouter() public returns (MockCcipRouter) {
        return new MockCcipRouter();
    }

    function deployLiquidityGaugeV4(
        address DFX,
        address veDFX,
        address lpt,
        address veBoostProxy,
        address distributor,
        address admin,
        address proxyAdmin
    ) public returns (ILiquidityGaugeV4) {
        // Deploy LiquidityGaugeV4 implementation
        address _gaugeAddr = vyperDeployer.deployContract("src/mainnet/", "LiquidityGaugeV4", "");

        // Deploy LiquidityGaugeV4 proxy
        bytes memory params = abi.encodeWithSelector(
            ILiquidityGaugeV4.initialize.selector, lpt, admin, DFX, veDFX, veBoostProxy, distributor
        );
        DfxUpgradeableProxy proxy = new DfxUpgradeableProxy(_gaugeAddr, proxyAdmin, params);
        return ILiquidityGaugeV4(address(proxy));
    }

    function deploySender(
        address DFX,
        address router,
        uint256 targetChainSelector,
        address feeToken,
        address admin,
        address proxyAdmin
    ) public returns (CcipSender) {
        // Deploy CcipSender implementation
        CcipSender _sender = new CcipSender(DFX);

        // Deploy CcipSender proxy
        bytes memory params =
            abi.encodeWithSelector(CcipSender.initialize.selector, router, targetChainSelector, feeToken, admin);
        DfxUpgradeableProxy proxy = new DfxUpgradeableProxy(address(_sender), proxyAdmin, params);
        return CcipSender(payable(address(proxy)));
    }

    function deployRootGauge(
        string memory name,
        address DFX,
        address distributor,
        address router,
        address admin,
        address proxyAdmin
    ) public returns (CcipRootGauge) {
        // Deploy CcipRootGauge implementation
        CcipRootGauge _gauge = new CcipRootGauge(DFX);

        // Deploy CcipRootGauge gauge
        bytes memory params = abi.encodeWithSelector(
            CcipRootGauge.initialize.selector,
            name,
            distributor,
            router,
            TARGET_CHAIN_SELECTOR, // mock target chain selector
            address(0), // mock fee token address
            admin
        );
        DfxUpgradeableProxy proxy = new DfxUpgradeableProxy(address(_gauge), proxyAdmin, params);
        return CcipRootGauge(payable(address(proxy)));
    }
}
