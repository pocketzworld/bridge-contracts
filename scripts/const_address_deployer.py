from typing import Optional

from brownie import config, network, web3
from brownie.network.contract import Contract, ContractContainer
from eth_abi import encode
from eth_account import Account
from eth_hash.auto import keccak

from .common import (
    Project,
    const_address_deployer_deployer,
    get_account,
    load_axelar_utils,
)


def deploy(axelar: Optional[Project] = None) -> Contract:
    print(f"Deploying ConstAddressDeployer for {network.show_active()}")
    if not axelar:
        axelar = load_axelar_utils()
    account = const_address_deployer_deployer()
    const_deployer_contract = axelar.ConstAddressDeployer.deploy({"from": account})
    print(f"ConstAddressDeployer deployed at: {const_deployer_contract.address}")
    return const_deployer_contract


def const_address_deployer(axelar: Optional[Project] = None) -> Contract:
    if not axelar:
        axelar = load_axelar_utils()
    if address := config["networks"][network.show_active()].get("constAddressDeployer"):
        print(f"Const Address Deployer at: {address}")
        return Contract.from_abi(
            "ConstAddressDeployer", address, axelar.ConstAddressDeployer.abi
        )
    else:
        return deploy(axelar)


def get_salt_from_key(key: str) -> bytes:
    return keccak(encode(["string"], [key]))


def deploy_and_init_contract(
    contract_container: ContractContainer,
    account: Account,
    deployer: Contract,
    key: str,
    *args,
) -> str:
    if not account:
        account = get_account()
    # Prepare Deployment
    salt = get_salt_from_key(key)
    factory = web3.eth.contract(
        abi=contract_container.abi, bytecode=contract_container.bytecode
    )
    contract_name = contract_container._name
    print(
        f"ConstAddressDeployer with salt {salt} deploying and initializing {contract_name} for {network.show_active()}"
    )

    bytecode = factory.constructor().build_transaction()["data"]
    # Precalculate contract address
    proxy_address = deployer.deployedAddress(bytecode, account.address, salt)
    # Build init transaction
    contract = web3.eth.contract(proxy_address, abi=contract_container.abi)
    init_data = contract.functions.init(*args).build_transaction()["data"]
    # Deploy and init proxy
    deployer.deployAndInit(bytecode, salt, init_data, {"from": account}).wait(1)
    print(
        f"ConstAddressDeployer deployed and initialized {contract_name} at {proxy_address}"
    )
    return proxy_address
