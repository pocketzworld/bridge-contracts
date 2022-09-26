from brownie import network

from .common import const_address_deployer_deployer, load_axelar_utils


def deploy():
    print(f"Deploying ConstAddressDeployer for {network.show_active()}")
    deployer = const_address_deployer_deployer()
    axelar = load_axelar_utils()
    const_deployer_contract = axelar.ConstAddressDeployer.deploy({"from": deployer})
    print(f"ConstAddressDeployer deployed at: {const_deployer_contract.address}")
