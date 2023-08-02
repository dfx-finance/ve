# Deployment

| Network  | Network Name   |
| -------- | -------------- |
| Ethereum | `ethereum`     |
| Polygon  | `polygon-main` |
| Hardhat  | `hardhat`      |

## Steps

1. Add deploy accounts to brownie with private key

   ```bash
   $ brownie accounts new deployve
   $ brownie accounts new deployve-proxyadmin
   ```

2. Edit deploy scripts (_step 3_) to load account with wallets named `deployve` and `deployve-proxyadmin`

3. Edit `gas_strategy` in `./scripts/helper.py` with recent gas prices from Etherscan

4. Deploy veDFX contract (if necessary)

   ```bash
   $ brownie run 0_deploy_vedfx.py --network <network-name>
   ```

5. Run VE deploy scripts

   ```bash
   $ brownie run 1_deploy_gaugecontroller.py --network <network-name>
   $ brownie run 2_deploy_distributor.py --network <network-name>
   $ brownie run 3_deploy_liquidity_gauges_v4.py --network <network-name>
   ```
