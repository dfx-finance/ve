# Operating VE Contracts

## Logging

```bash
$ brownie run run/log_ve_status.py --network <network-name>
```

## Initial Rewards

1. Provide rewards to the Distributor contract

```bash
$ brownie run run/provide_distributor_rewards.py --network <network-name>
```

_\*Edit `provide_distributor_rewards.py` script with amount of DFX rewards to add and its initial distribution rate before running_

2. Activate distributions to gauges

```bash
$ brownie run run/toggle_gauge_distributor.py --network <network-name>
```

# Weekly Epoch Rewards

1. Poke to update mining rate

   ```bash
   $ brownie run run/poke_distributor_mining_parameters.py --network <network-name>
   ```

2. Distribute rewards to all gauges

   ```bash
   $ brownie run run/distribute_gauge_rewards.py --network <network-name>
   ```

## Distributions & Updates

1. Reward distributions happen in 2 parts
   - ~80% from DfxDistributor / ~20% manually distributed to each gauge from Safe
   - Thursdays @ 00:00 UTC
   - Automated task: https://app.gelato.network/task/0x162f6a580ca19af3cebc99152b9a7df26289b05933334c8d7bcd413f293fd444?chainId=1
2. Update mining params
   - Fridays @ 00:35 UTC
   - Automated task: https://app.gelato.network/task/0x4f74788bbf6f3aa81424c71bf9eb7d7ba4d8d0ead8caad1bdb8194e106ca1939?chainId=1
