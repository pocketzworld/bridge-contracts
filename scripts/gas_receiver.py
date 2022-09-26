from brownie import network
from eth_abi import encode

from .common import axelar_deployer, load_axelar_cgp

BLACKHOLE_ADDRESS = "0x0100000000000000000000000000000000000000"


def deploy(gateway_address: str):
    print(f"Deploying AxelarGasService for {network.show_active()}")
    axelar = load_axelar_cgp()
    account = axelar_deployer()
    # gas_receiver = axelar.AxelarGasService.deploy(BLACKHOLE_ADDRESS, {"from": account})
    # print(f"AxelarGasService deployed at: {gas_receiver.address}")
    proxy = axelar.AxelarGasServiceProxy.deploy({"from": account})
    proxy.init(
        "0x2529bf1c546D3B7dB269B74F124e24b2435dD87A",
        account.address,
        bytes(),
        {"from": account},
    )
    print(f"AxelarGasService deployed at: {proxy.address}")
