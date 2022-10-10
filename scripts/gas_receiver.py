from typing import Optional

from brownie import config, network
from brownie.network.contract import Contract

from .common import Project, axelar_deployer, load_axelar_cgp

BLACKHOLE_ADDRESS = "0x0100000000000000000000000000000000000000"


def deploy(axelar: Optional[Project] = None) -> Contract:
    print(f"Deploying AxelarGasService for {network.show_active()}")
    if not axelar:
        axelar = load_axelar_cgp()
    account = axelar_deployer()
    gas_receiver = axelar.AxelarGasService.deploy(BLACKHOLE_ADDRESS, {"from": account})
    print(f"AxelarGasService implementation deployed at: {gas_receiver.address}")
    proxy = axelar.AxelarGasServiceProxy.deploy({"from": account})
    proxy.init(
        gas_receiver.address,
        account.address,
        bytes(),
        {"from": account},
    )
    print(f"AxelarGasService deployed at: {proxy.address}")
    return Contract.from_abi(
        "AxelarGasService", proxy.address, axelar.AxelarGasService.abi
    )


def gas_receiver(axelar: Optional[Project] = None) -> Contract:
    if not axelar:
        axelar = load_axelar_cgp()
    if address := config["networks"][network.show_active()].get("gasService"):
        print(f"Gas Service at: {address}")
        return Contract.from_abi(
            "AxelarGasService", address, axelar.AxelarGasService.abi
        )
    else:
        return deploy(axelar)
