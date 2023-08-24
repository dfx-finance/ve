import "@nomicfoundation/hardhat-toolbox";
import "./tasks";

const ethers = require("ethers");
const wallet = ethers.Wallet.createRandom();

const PRIVATE_KEY = wallet.privateKey;
const ETHEREUM_SEPOLIA_RPC_URL = process.env.ETHEREUM_SEPOLIA_RPC_URL;
const POLYGON_MUMBAI_RPC_URL = process.env.POLYGON_MUMBAI_RPC_URL;
const OPTIMISM_GOERLI_RPC_URL = process.env.OPTIMISM_GOERLI_RPC_URL;
const ARBITRUM_TESTNET_RPC_URL = process.env.ARBITRUM_TESTNET_RPC_URL;
const AVALANCHE_FUJI_RPC_URL = process.env.AVALANCHE_FUJI_RPC_URL;

module.exports = {
  solidity: "0.8.19",
  typechain: {
    outDir: "typechain",
    target: "ethers-v5",
    externalArtifacts: ["./build/*.json"],
  },
  ethereumSepolia: {
    url: ETHEREUM_SEPOLIA_RPC_URL !== undefined ? ETHEREUM_SEPOLIA_RPC_URL : "",
    accounts: PRIVATE_KEY !== undefined ? [PRIVATE_KEY] : [],
    chainId: 11155111,
  },
  polygonMumbai: {
    url: POLYGON_MUMBAI_RPC_URL !== undefined ? POLYGON_MUMBAI_RPC_URL : "",
    accounts: PRIVATE_KEY !== undefined ? [PRIVATE_KEY] : [],
    chainId: 80001,
  },
  optimismGoerli: {
    url: OPTIMISM_GOERLI_RPC_URL !== undefined ? OPTIMISM_GOERLI_RPC_URL : "",
    accounts: PRIVATE_KEY !== undefined ? [PRIVATE_KEY] : [],
    chainId: 420,
  },
  arbitrumTestnet: {
    url: ARBITRUM_TESTNET_RPC_URL !== undefined ? ARBITRUM_TESTNET_RPC_URL : "",
    accounts: PRIVATE_KEY !== undefined ? [PRIVATE_KEY] : [],
    chainId: 421613,
  },
  avalancheFuji: {
    url: AVALANCHE_FUJI_RPC_URL !== undefined ? AVALANCHE_FUJI_RPC_URL : "",
    accounts: PRIVATE_KEY !== undefined ? [PRIVATE_KEY] : [],
    chainId: 43113,
  },
};
