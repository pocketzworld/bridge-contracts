from typing import Optional

from brownie import config, network
from brownie.network.contract import Contract
from eth_abi import encode
from .common import Project

from .common import axelar_deployer, load_axelar_cgp


def deploy(axelar: Optional[Project] = None) -> Contract:
    print(f"Deploying Axelar Gateway contracts for {network.show_active()}")
    if not axelar:
        axelar = load_axelar_cgp()
    account = axelar_deployer()
    auth = axelar.AxelarAuthWeighted.deploy(
        [encode(["address[]", "uint256[]", "uint256"], [[account.address], [1], 1])],
        {"from": account},
    )
    print(f"Auth deployed to {auth.address}")
    token_deployer = axelar.TokenDeployer.deploy({"from": account})
    print(f"TokenDeployer deployed to {token_deployer.address}")
    gateway = axelar.AxelarGateway.deploy(
        auth.address, token_deployer.address, {"from": account}
    )
    print(f"AxelarGateway deployed to {gateway.address}")
    params = encode(["address[]", "uint8", "bytes"], [[account.address], 1, bytes()])
    proxy = axelar.AxelarGatewayProxy.deploy(gateway.address, params, {"from": account})
    print(f"AxelarGatewayProxy deployed to {proxy.address}")
    auth.transferOwnership(proxy.address).wait(1)
    print("Transfered auth ownership to proxy")
    # Gateway should be accessed through proxy address
    # Interface is IAxelarGateway
    return Contract.from_abi("AxelarGateway", proxy.address, axelar.AxelarGateway.abi)


def gateway(axelar: Optional[Project] = None) -> Contract:
    if not axelar:
        axelar = load_axelar_cgp()
    if address := config["networks"][network.show_active()].get("gateway"):
        print(f"Gateway at: {address}")
        return Contract.from_abi("AxelarGateway", address, axelar.AxelarGateway.abi)
    else:
        return deploy(axelar)
