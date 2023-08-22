require("dotenv").config(); // eslint-disable-line
import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";

const chainId = 1;

const RpcUrls: Record<string, string> = {
  1: "https://eth-mainnet.g.alchemy.com/v2/1kJC91jDERDpdr_ykBgAdyjYAG-Iw0D0" as string,
  1337: "https://eth-mainnet.g.alchemy.com/v2/1kJC91jDERDpdr_ykBgAdyjYAG-Iw0D0" as string,
  11155111:
    "https://eth-sepolia.g.alchemy.com/v2/MvoACHmO6DkI2ZVMI4fjD1r8EGVdUEHb" as string,
};

// const ethBlock = 14_443_000; // dfxCad deployed
// const ethBlock = 14_572_523; // curve dfxCad/cadc staking deployed
// const ethBlock = 14_725_000; // veDFX deployed
// const ethBlock = 15_051_000; // euroc/usdc pool deployed
// const ethBlock = 15_504_570; // ve deployed
// const ethBlock = 15_742_070; // ammv2 deployed
// const ethBlock = 15_749_200; // ammv2 redeployed
// const ethBlock = 15_765_345; // ammv2 seeded
// const ethBlock = 15_816_440; // during epoch 1
// const ethBlock = 15_848_000; // during epoch 2
// const ethBlock = 15_941_646; // pre-attack
// const ethBlock = 15_941_971; // post-attack
// const ethBlock = 15_983_915; // last DfxDistributor update
// const ethBlock = 16_685_597; // ammv2.1 seeded, gauges staked
const ethBlock = 16_723_375; // gbpt deployed

const BlockNumbers: Record<string, number> = {
  1: ethBlock,
  1337: ethBlock,
};

const config: HardhatUserConfig = {
  solidity: "0.8.17",
  networks: {
    localhost: {
      url: "http://127.0.0.1:8545",
    },
    hardhat: {
      chainId,
      forking: {
        enabled: true,
        url: RpcUrls[11155111],
      },
      allowUnlimitedContractSize: true,
      hardfork: "london",
    },
  },
};

export default config;
