require("dotenv").config(); // eslint-disable-line
import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";

const chainId = 11155111;

const RpcUrls: Record<string, string> = {
  1: "https://eth-mainnet.g.alchemy.com/v2/1kJC91jDERDpdr_ykBgAdyjYAG-Iw0D0" as string,
  1337: "https://eth-mainnet.g.alchemy.com/v2/1kJC91jDERDpdr_ykBgAdyjYAG-Iw0D0" as string,
  11155111:
    "https://eth-sepolia.g.alchemy.com/v2/MvoACHmO6DkI2ZVMI4fjD1r8EGVdUEHb" as string,
};

const ethBlock = 16_723_375; // gbpt deployed
const ETHEREUM_SEPOLIA_RPC_URL =
  "https://eth-sepolia.g.alchemy.com/v2/MvoACHmO6DkI2ZVMI4fjD1r8EGVdUEHb";
const PRIVATE_KEY =
  "0x0ac7fa86be251919f466d1313c31ecb341cbc09d55fcc2ffa18977619e9097fb";
const POLYGON_MUMBAI_RPC_URL =
  "https://polygon-mumbai.g.alchemy.com/v2/xu46eUfiqO1kbfJYIrU9-2dohOJHLMQC";

const config: HardhatUserConfig = {
  solidity: "0.8.17",
  networks: {
    hardhat: {
      chainId: 31337,
    },
    ethereumSepolia: {
      url:
        ETHEREUM_SEPOLIA_RPC_URL !== undefined ? ETHEREUM_SEPOLIA_RPC_URL : "",
      accounts: PRIVATE_KEY !== undefined ? [PRIVATE_KEY] : [],
      chainId: 11155111,
    },
    polygonMumbai: {
      url: POLYGON_MUMBAI_RPC_URL !== undefined ? POLYGON_MUMBAI_RPC_URL : "",
      accounts: PRIVATE_KEY !== undefined ? [PRIVATE_KEY] : [],
      chainId: 80001,
    },
  },
};

export default config;
