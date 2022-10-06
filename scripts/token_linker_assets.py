from typing import Optional

from brownie import (
    Contract,
    TokenLinkerNativeFactoryLookup,
    config,
    interface,
    network,
    web3,
)
from eth_abi import encode
from eth_account import Account
from eth_hash.auto import keccak

from .common import get_account

# TODO(@mculinovic)
RISE_SALT = "RISE"
RISE_ERC20_ADDRESS = config["networks"][network.show_active()]["riseERC20"]


def token_linker_params(_type: int, **kwargs) -> bytes:
    if _type == 0:
        return encode(["address"], [kwargs["address"]])
    elif _type == 1:
        return encode(
            ["string", "string", "uint8"],
            [kwargs["name"], kwargs["symbol"], kwargs["decimals"]],
        )
    elif _type == 3:
        return "0x"
    else:
        raise Exception(f"Unsupported token linker type: {_type}")


def deploy_native_rise(account: Optional[Account] = None):
    print(f"Deploying TokenLinkerNative to {network.show_active()}")
    if not account:
        account = get_account()
    factory_address = config["networks"][network.show_active()].get(
        "tokenLinkerFactory"
    )
    if not factory_address:
        raise Exception("Factory not deployed")
    factory = interface.ITokenLinkerFactory(factory_address)
    salt = keccak(encode(["string"], [RISE_SALT]))
    token_linker_type = 3
    (
        tx := factory.deploy(
            token_linker_type,
            salt,
            token_linker_params(token_linker_type),
            True,
            {"from": account},
        )
    ).wait(1)
    print(tx.events)
    id = factory.getTokenLinkerId(account.address, salt)
    address = factory.tokenLinker(id, True)
    print(f"Deployed TokenLinkerNative at {address}")


def deploy_rise_lock_unlock(account: Optional[Account] = None):
    print(f"Deploying TokenLinkerLockUnlock to {network.show_active()}")
    if not account:
        account = get_account()
    factory_address = config["networks"][network.show_active()].get(
        "tokenLinkerFactory"
    )
    factory = interface.ITokenLinkerFactory(factory_address)
    salt = keccak(encode(["string"], [RISE_SALT]))
    token_linker_type = 0
    factory.deploy(
        token_linker_type,
        salt,
        token_linker_params(token_linker_type, address=RISE_ERC20_ADDRESS),
        True,
        {"from": account},
    ).wait(1)
    id = factory.getTokenLinkerId(account.address, salt)
    address = factory.tokenLinker(id, True)
    print(f"Deployed TokenLinkerLockUnlock at {address}")


def get_native_balance():
    account = get_account()
    factory_address = config["networks"][network.show_active()].get(
        "tokenLinkerFactory"
    )
    factory = interface.ITokenLinkerFactory(factory_address)
    salt = keccak(encode(["string"], [RISE_SALT]))
    id = factory.getTokenLinkerId(account.address, salt)
    address = factory.tokenLinker(id, True)
    print(address)
    token_linker = Contract.from_abi(
        "Native", address, TokenLinkerNativeFactoryLookup.abi
    )
    print(token_linker.getNativeBalance())
    balance = token_linker.getNativeBalance()
    print(web3.fromWei(balance, "ether"))


def update_native_balance(amount: int):
    account = get_account()
    factory_address = config["networks"][network.show_active()].get(
        "tokenLinkerFactory"
    )
    factory = interface.ITokenLinkerFactory(factory_address)
    salt = keccak(encode(["string"], [RISE_SALT]))
    id = factory.getTokenLinkerId(account.address, salt)
    address = factory.tokenLinker(id, True)
    print(address)
    token_linker = Contract.from_abi(
        "Native", address, TokenLinkerNativeFactoryLookup.abi
    )
    print(token_linker.getNativeBalance())
    token_linker.updateBalance({"from": account, "value": web3.toWei(amount, "ether")})
    balance = token_linker.getNativeBalance()
    print(web3.fromWei(balance, "ether"))


def send_erc20(amount: int):
    amount = web3.toWei(amount, "ether")
    account = get_account()
    factory_address = config["networks"][network.show_active()].get(
        "tokenLinkerFactory"
    )
    factory = interface.ITokenLinkerFactory(factory_address)
    salt = keccak(encode(["string"], [RISE_SALT]))
    id = factory.getTokenLinkerId(account.address, salt)
    address = factory.tokenLinker(id, True)
    print(address)
    token_linker = interface.ITokenLinker(address)
    token_address = token_linker.token()
    print(token_address)
    token = interface.IERC20(token_address)
    token.approve(token_linker.address, amount, {"from": account}).wait(1)
    chain_name = "Dev"
    token_linker.sendToken(
        chain_name,
        account.address,
        amount,
        {
            "from": account,
            "value": 30000000,
            "gas_limit": 10000000,
        },
    )
