#!/usr/bin/env python


# live deployments--Ethereum
class Ethereum:
    DFX = "0x888888435FDe8e7d4c54cAb67f206e4199454c60"
    DFX_MULTISIG_0 = "0x27E843260c71443b4CC8cB6bF226C3f77b9695AF"
    DFX_MULTISIG_1 = "0x26f539A0fE189A7f228D7982BF10Bc294FA9070c"
    VEDFX = "0x3AC91A7A2d30Fa25AdA4616d337a28ea988988BE"
    VEBOOST = "0x07d1FfdcF06e32EDd964E15bcaD59BADde6c7D08"
    VEBOOST_PROXY = "0x71EB1046607a2496A2fD48AB73D1973ee9FaDFf0"
    GAUGE_LOGIC = "0x71c0ddBF6da72a67C29529d6f67f97C00c4751D5"
    GAUGE_CONTROLLER = "0x3C56A223fE8F61269E25eF1116f9f185074c6C44"
    DFX_DISTRIBUTOR = "0x86E8C4e7549fBCa7eba1AefBdBc23993F721e5CA"
    CCIP_ROUTER = "0xE561d5E02207fb5eB32cca20a699E0d8919a1476"

    DFX_CADC_USDC_LP = "0xDA9dcc7fd51F0D9Aa069a82647A5F3ba594edAED"
    DFX_EURC_USDC_LP = "0x8cd86fbC94BeBFD910CaaE7aE4CE374886132c48"
    DFX_GBPT_USDC_LP = "0x7d1bA2c18CbDE0D790Cc1d626F0c70b3c13C9eec"
    DFX_GYEN_USDC_LP = "0x9aFD65013770525E43a84e49c87B3015C2C32517"
    DFX_NZDS_USDC_LP = "0xc147cee0F6BB0e56240868c9f53aE916D3b86073"
    DFX_TRYB_USDC_LP = "0x38F818fCd57F8A1782bBCC1C90CB0FD03e7f0bd1"
    DFX_XIDR_USDC_LP = "0xb7dB2F8d25C51A26799bE6765720c3C6D84CD2f2"
    DFX_XSGD_USDC_LP = "0xACC5Dca0B684f444bC6b4be30B95Ca7D928A4B9c"

    DFX_CADC_USDC_GAUGE = "0xBE5869c78668B2c49C571005f3754a92472D9E1b"
    DFX_EURC_USDC_GAUGE = "0x1e07D4dad0614A811A12BDCD66016f48c6942A60"
    DFX_GBPT_USDC_GAUGE = "0xB41ab47a724fB24f1DC0e57380411C7FC5cDD00B"
    DFX_GYEN_USDC_GAUGE = "0xA2Bc5552A5A083E78ec820A91e97933133255572"
    DFX_NZDS_USDC_GAUGE = "0x45C38b5126eB70e8B0A2c2e9FE934625641bF063"
    DFX_TRYB_USDC_GAUGE = "0xb0de1886dD949b5DBFB9feBF7ba283f5Ff87c7EB"
    DFX_XIDR_USDC_GAUGE = "0x520B0284bCD3Fb0BA427Df1fCd1DE444c7c676A5"
    DFX_XSGD_USDC_GAUGE = "0xE7006808E855F3707Ec58bDfb66A096A7a6155e1"

    ARBITRUM_CADC_USDC_ROOT_GAUGE = "0x0eE2C90746110CE2C13b44CC779b7232cF127a30"
    ARBITRUM_GYEN_USDC_ROOT_GAUGE = "0x73725CD88C92B67619a8e403E9F8E75ed0dE9E32"
    POLYGON_CADC_USDC_ROOT_GAUGE = "0xFDAd1Faa0F8Ab7342E061040246c2D802b1ceca2"
    POLYGON_NGNC_USDC_ROOT_GAUGE = "0xC28423742bb6daf3d9D111a9b3BfA9e8a26c052F"
    POLYGON_TRYB_USDC_ROOT_GAUGE = "0xB9c445BE34E7C5f1055A0bfd5d18245F0d009cf1"
    POLYGON_XSGD_USDC_ROOT_GAUGE = "0xB70CCEe4eDED08141c25C52F5DEB680e5991Bd86"


class Arbitrum:
    BRIDGED_DFX = "0xE7804D91dfCDE7F776c90043E03eAa6Df87E6395"
    CCIP_ROUTER = "0xE92634289A1841A979C11C2f618B33D376e4Ba85"
    CCIP_DFX = "0xc4Fe39a1588807CfF8d8897050c39F065eBAb0B8"  # clCCIP-LnM / DFX

    DFX_CADC_USDC_LP = "0x8731d45ff9684d380302573cCFafd994Dfa7f7d3"
    DFX_GYEN_USDC_LP = "0x969E3128DB078b179E9F3b3679710d2443cCDB72"

    CCIP_CADC_USDC_RECEIVER = "0x0000000000000000000000000000000000000000"
    CCIP_GYEN_USDC_RECEIVER = "0x0000000000000000000000000000000000000000"

    CCIP_CADC_USDC_STREAMER = ""
    CCIP_GYEN_USDC_STREAMER = ""

    DFX_CADC_USDC_GAUGE = ""
    DFX_GYEN_USDC_GAUGE = ""


class Polygon:
    BRIDGED_DFX = "0xE7804D91dfCDE7F776c90043E03eAa6Df87E6395"
    CCIP_ROUTER = "0x3C3D92629A02a8D95D5CB9650fe49C3544f69B43"
    CCIP_DFX = "0xc4Fe39a1588807CfF8d8897050c39F065eBAb0B8"

    DFX_CADC_USDC_LP = "0x8731d45ff9684d380302573cCFafd994Dfa7f7d3"
    DFX_NGNC_USDC_LP = "0x969E3128DB078b179E9F3b3679710d2443cCDB72"
    DFX_TRYB_USDC_LP = "0x20Dc424c5fa468CbB1c702308F0cC9c14DA2825C"
    DFX_XSGD_USDC_LP = "0x4653251486a57f90Ee89F9f34E098b9218659b83"

    CCIP_CADC_USDC_RECEIVER = "0x0000000000000000000000000000000000000000"
    CCIP_NGNC_USDC_RECEIVER = "0x0000000000000000000000000000000000000000"
    CCIP_TRYB_USDC_RECEIVER = "0x0000000000000000000000000000000000000000"
    CCIP_XSGD_USDC_RECEIVER = "0x0000000000000000000000000000000000000000"

    CCIP_CADC_USDC_STREAMER = ""
    CCIP_NGNC_USDC_STREAMER = ""
    CCIP_TRYB_USDC_STREAMER = ""
    CCIP_XSGD_USDC_STREAMER = ""

    DFX_CADC_USDC_GAUGE = ""
    DFX_NGNC_USDC_GAUGE = ""
    DFX_TRYB_USDC_GAUGE = ""
    DFX_XSGD_USDC_GAUGE = ""


# fork deployments
# ETH block: 18_262_000
class EthereumLocalhost:
    DFX = "0x888888435FDe8e7d4c54cAb67f206e4199454c60"
    DFX_MULTISIG_0 = "0x27E843260c71443b4CC8cB6bF226C3f77b9695AF"
    DFX_MULTISIG_1 = "0x26f539A0fE189A7f228D7982BF10Bc294FA9070c"
    VEDFX = "0xc4Fe39a1588807CfF8d8897050c39F065eBAb0B8"
    VEBOOST = None
    VEBOOST_PROXY = "0x8731d45ff9684d380302573cCFafd994Dfa7f7d3"
    GAUGE_CONTROLLER = "0x969E3128DB078b179E9F3b3679710d2443cCDB72"
    DFX_DISTRIBUTOR = "0x89ec9355b1Bcc964e576211c8B011BD709083f8d"
    CCIP_ROUTER = "0xE561d5E02207fb5eB32cca20a699E0d8919a1476"  # forked

    # forked live addresses
    DFX_CADC_USDC_LP = "0xDA9dcc7fd51F0D9Aa069a82647A5F3ba594edAED"
    DFX_EURC_USDC_LP = "0x8cd86fbC94BeBFD910CaaE7aE4CE374886132c48"
    DFX_GBPT_USDC_LP = "0x7d1bA2c18CbDE0D790Cc1d626F0c70b3c13C9eec"
    DFX_GYEN_USDC_LP = "0x9aFD65013770525E43a84e49c87B3015C2C32517"
    DFX_NZDS_USDC_LP = "0xc147cee0F6BB0e56240868c9f53aE916D3b86073"
    DFX_TRYB_USDC_LP = "0x38F818fCd57F8A1782bBCC1C90CB0FD03e7f0bd1"
    DFX_XIDR_USDC_LP = "0xb7dB2F8d25C51A26799bE6765720c3C6D84CD2f2"
    DFX_XSGD_USDC_LP = "0xACC5Dca0B684f444bC6b4be30B95Ca7D928A4B9c"

    DFX_CADC_USDC_GAUGE = "0x52bad4A8584909895C22bdEcf8DBF33314468Fb0"
    DFX_EURC_USDC_GAUGE = "0xed12bE400A07910E4d4E743E4ceE26ab1FC9a961"
    DFX_GBPT_USDC_GAUGE = "0x1B25157F05B25438441bF7CDe38A95A55ccf8E50"
    DFX_GYEN_USDC_GAUGE = "0xc775bF567D67018dfFac4E89a7Cf10f0EDd0Be93"
    DFX_NZDS_USDC_GAUGE = "0x3489745eff9525CCC3d8c648102FE2cf3485e228"
    DFX_TRYB_USDC_GAUGE = "0x43b9Ef43D415e84aD9964567002d648b11747A8f"
    DFX_XIDR_USDC_GAUGE = "0xFCa5Bb3732185AE6AaFC65aD8C9A4fBFf21DbaaD"
    DFX_XSGD_USDC_GAUGE = "0x32cd5ecdA7f2B8633C00A0434DE28Db111E60636"

    ARBITRUM_CADC_USDC_ROOT_GAUGE = "0x55027d3dBBcEA0327eF73eFd74ba0Af42A13A966"
    ARBITRUM_GYEN_USDC_ROOT_GAUGE = "0x9eb52339B52e71B1EFD5537947e75D23b3a7719B"

    POLYGON_CADC_USDC_ROOT_GAUGE = "0x92b0d1Cc77b84973B7041CB9275d41F09840eaDd"
    POLYGON_NGNC_USDC_ROOT_GAUGE = "0x996785Fe937d92EDBF420F3Bf70Acc62ecD6f655"
    POLYGON_TRYB_USDC_ROOT_GAUGE = "0x1Dbbf529D78d6507B0dd71F6c02f41138d828990"
    POLYGON_XSGD_USDC_ROOT_GAUGE = "0xf18774574148852771c2631d7d06E2A6c8b44fCA"


# Arbitrum block:
class ArbitrumLocalhost:
    BRIDGED_DFX = "0xE7804D91dfCDE7F776c90043E03eAa6Df87E6395"
    CCIP_ROUTER = "0xE92634289A1841A979C11C2f618B33D376e4Ba85"
    CCIP_DFX = "0xc4Fe39a1588807CfF8d8897050c39F065eBAb0B8"  # clCCIP-LnM / DFX

    DFX_CADC_USDC_LP = "0x8731d45ff9684d380302573cCFafd994Dfa7f7d3"
    DFX_GYEN_USDC_LP = "0x969E3128DB078b179E9F3b3679710d2443cCDB72"

    CCIP_CADC_USDC_RECEIVER = "0x0000000000000000000000000000000000000000"
    CCIP_GYEN_USDC_RECEIVER = "0x0000000000000000000000000000000000000000"

    CCIP_CADC_USDC_STREAMER = ""
    CCIP_GYEN_USDC_STREAMER = ""

    DFX_CADC_USDC_GAUGE = ""
    DFX_GYEN_USDC_GAUGE = ""


# Polygon block:
class PolygonLocalhost:
    BRIDGED_DFX = "0xE7804D91dfCDE7F776c90043E03eAa6Df87E6395"
    CCIP_ROUTER = "0x3C3D92629A02a8D95D5CB9650fe49C3544f69B43"
    CCIP_DFX = "0xc4Fe39a1588807CfF8d8897050c39F065eBAb0B8"

    DFX_CADC_USDC_LP = "0x8731d45ff9684d380302573cCFafd994Dfa7f7d3"
    DFX_NGNC_USDC_LP = "0x969E3128DB078b179E9F3b3679710d2443cCDB72"
    DFX_TRYB_USDC_LP = "0x20Dc424c5fa468CbB1c702308F0cC9c14DA2825C"
    DFX_XSGD_USDC_LP = "0x4653251486a57f90Ee89F9f34E098b9218659b83"

    CCIP_CADC_USDC_RECEIVER = "0x0000000000000000000000000000000000000000"
    CCIP_NGNC_USDC_RECEIVER = "0x0000000000000000000000000000000000000000"
    CCIP_TRYB_USDC_RECEIVER = "0x0000000000000000000000000000000000000000"
    CCIP_XSGD_USDC_RECEIVER = "0x0000000000000000000000000000000000000000"

    CCIP_CADC_USDC_STREAMER = ""
    CCIP_NGNC_USDC_STREAMER = ""
    CCIP_TRYB_USDC_STREAMER = ""
    CCIP_XSGD_USDC_STREAMER = ""

    DFX_CADC_USDC_GAUGE = ""
    DFX_NGNC_USDC_GAUGE = ""
    DFX_TRYB_USDC_GAUGE = ""
    DFX_XSGD_USDC_GAUGE = ""


# test deployments CCIP--Sepolia to Mumbai
class Sepolia:
    CCIP_ROUTER = "0xD0daae2231E9CB96b94C8512223533293C3693Bf"
    CCIP_DFX = "0x466D489b6d36E7E3b824ef491C225F5830E81cC1"  # clCCIP-LnM / Sepolia

    MUMBAI_ETH_BTC_ROOT_GAUGE = "0x871C25055aB1d212a31B5b2E8088dca63384EEb3"


class Mumbai:
    CCIP_ROUTER = "0x70499c328e1E2a3c41108bd3730F6670a44595D1"
    CCIP_DFX = (
        "0xc1c76a8c5bFDE1Be034bbcD930c668726E7C1987"  # clCCIP-LnM / Polygon Mumbai
    )
    CCIP_RECEIVER = "0x84581C6eF2B5d9D44612b55133DF7d73a4dfA29B"
    CCIP_STREAMER = "0x3669Ee5CC6D1057b0F9544f48B45480e189c834b"

    DFX_ETH_BTC_LP = "0xF15BBC3b5D2DF49b88967d2b574eF3d289a0138f"
    DFX_ETH_BTC_GAUGE = "0x61fb8e66609934231103F5D5Ad3F703a29270dA7"  # proxy
