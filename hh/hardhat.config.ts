require("dotenv").config(); // eslint-disable-line
import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";

const chainId = 1;

const RpcUrls: Record<string, string> = {
  1: process.env.ETH_RPC_URL as string,
  1337: process.env.ETH_RPC_URL as string,
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
const ethBlock = 15_941_971; // post-attack

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
        url: RpcUrls[chainId] || "http://127.0.0.1:8545",
        blockNumber: BlockNumbers[chainId],
      },
      allowUnlimitedContractSize: true,
      hardfork: "london",
    },
  },
};

export default config;
