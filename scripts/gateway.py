from brownie import network
from eth_abi import encode

from .common import axelar_deployer, load_axelar_cgp


def deploy():
    print(f"Deploying ConstAddressDeployer for {network.show_active()}")
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
