import os
from typing import Any, NewType, Optional

from brownie import accounts, config, network, project, web3
from brownie.network.contract import ContractTx
from eth_abi import encode
from eth_account import Account
from eth_utils import keccak, to_bytes

Project = NewType("Project", Any)

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
LOCAL_DEV_SUBNETS = ["local-dev1", "local-dev2"]
SUBNET_ENVIRONMENTS = [
    "highrise-local",
    "highrise-devnet",
]
HIGHRISE_TESTNET = "highrise-testnet"

AXELAR_DEPLOYER = "this is a random string to get a random account. You need to provide the private key for a funded account here."
CONST_ADDRESS_DEPLOYER = "const-address-deployer-deployer"


def get_account() -> Account:
    active_network = network.show_active()
    if active_network in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    elif active_network in LOCAL_DEV_SUBNETS:
        return accounts.load(os.getenv("DEV_ACCOUNT_NAME"))
    elif active_network == HIGHRISE_TESTNET:
        return accounts.load(os.getenv("TESTNET_ACCOUNT_NAME"))
    else:
        raise Exception("Unsupported network")


def load_axelar_cgp() -> Project:
    axelar = project.load(config["dependencies"][0])
    return axelar


def load_axelar_utils() -> Project:
    axelar = project.load(config["dependencies"][1])
    return axelar


def axelar_deployer() -> Account:
    active_network = network.show_active()
    if active_network in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    elif active_network == HIGHRISE_TESTNET:
        raise Exception("Forbidden on testnet")
    else:
        deployer_private_key = keccak(
            encode(
                ["string"],
                [AXELAR_DEPLOYER],
            )
        )
        account = accounts.add(deployer_private_key)
    print(f"Deployer: {account.address} {account.balance()}")
    return account


def const_address_deployer_deployer() -> Account:
    active_network = network.show_active()
    if active_network in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        account = get_account()
    elif active_network == HIGHRISE_TESTNET:
        raise Exception("Forbidden on testnet")
    else:
        deployer_private_key = keccak(bytes(CONST_ADDRESS_DEPLOYER, "utf-8"))
        account = accounts.add(deployer_private_key)
    print(f"Deployer: {account.address} {account.balance()}")
    return account


def fund_account(account: str):
    funded_account = get_account()
    funded_account.transfer(account, web3.toWei(1, "ether")).wait(1)


def encode_function_data(initializer: Optional[ContractTx] = None, *args) -> bytes:
    """Encodes the function call so we can work with an initializer.
    Args:
        initializer - The initializer function we want to call
        args - Arguments to pass to the initalizer function
    Returns:
        Encoded bytes
    """
    if not args or not initializer:
        return to_bytes(hexstr="0x")
    return initializer.encode_input(*args)
