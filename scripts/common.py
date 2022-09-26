import os
from typing import Any, NewType

from brownie import accounts, config, network, project, web3
from eth_abi import encode
from eth_account import Account
from eth_utils import keccak

Project = NewType("Project", Any)

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
SUBNET_ENVIRONMENTS = [
    "highrise-local",
    "highrise-devnet",
    "highrise-tesnet",
]


def get_account() -> Account:
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    else:
        return accounts.load(os.getenv("DEV_ACCOUNT_NAME"))


def load_axelar_cgp() -> Project:
    axelar = project.load(config["dependencies"][0])
    return axelar


def load_axelar_utils() -> Project:
    axelar = project.load(config["dependencies"][1])
    return axelar


AXELAR_DEPLOYER = "this is a random string to get a random account. You need to provide the private key for a funded account here."


def axelar_deployer() -> Account:
    deployer_private_key = keccak(
        encode(
            ["string"],
            [AXELAR_DEPLOYER],
        )
    )
    account = accounts.add(deployer_private_key)
    print(f"Deployer: {account.address} {account.balance()}")
    return account


CONST_ADDRESS_DEPLOYER = "const-address-deployer-deployer"


def const_address_deployer_deployer() -> Account:
    deployer_private_key = keccak(bytes(CONST_ADDRESS_DEPLOYER, "utf-8"))
    account = accounts.add(deployer_private_key)
    print(f"Deployer: {account.address} {account.balance()}")
    return account


def fund_account(account: str):
    funded_account = get_account()
    funded_account.transfer(account, web3.toWei(1, "ether")).wait(1)
