from typing import Optional

from brownie import config, interface, network
from eth_abi import encode
from eth_account import Account
from eth_hash.auto import keccak

from .common import get_account

RISE_SALT = "RISE"
AVAX_SALT = "AVAX"
USDC_SALT = "USDC"


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


def deploy_with_factory(
    account: Account, token_linker_type: int, salt: str, **kwargs
) -> str:
    factory_address = config["networks"][network.show_active()].get(
        "tokenLinkerFactory"
    )
    factory = interface.ITokenLinkerFactory(factory_address)
    salt = keccak(encode(["string"], [salt]))
    factory.deploy(
        token_linker_type,
        salt,
        token_linker_params(
            token_linker_type,
            **kwargs,
        ),
        True,
        {"from": account},
    ).wait(1)
    id = factory.getTokenLinkerId(account.address, salt)
    address = factory.tokenLinker(id, True)
    return address


def deploy_native(asset_type: str, account: Optional[Account] = None):
    if asset_type == "AVAX":
        salt = AVAX_SALT
    elif asset_type == "RISE":
        salt = RISE_SALT
    print(f"Deploying TokenLinkerNative to {network.show_active()}")
    if not account:
        account = get_account()
    factory_address = config["networks"][network.show_active()].get(
        "tokenLinkerFactory"
    )
    if not factory_address:
        raise Exception("Factory not deployed")
    token_linker_type = 3
    address = deploy_with_factory(account, token_linker_type, salt)
    print(f"Deployed TokenLinkerNative at {address}")


def deploy_lock_unlock(asset: str, account: Optional[Account] = None):
    if asset == "RISE":
        asset_address = config["networks"][network.show_active()]["riseERC20"]
        salt = RISE_SALT
    elif asset == "USDC":
        asset_address = config["networks"][network.show_active()]["usdcERC20"]
        salt = USDC_SALT
    else:
        raise Exception("Not supported asset")
    print(f"Deploying TokenLinkerLockUnlock to {network.show_active()}")
    if not account:
        account = get_account()
    token_linker_type = 0
    address = deploy_with_factory(
        account, token_linker_type, salt, address=asset_address
    )
    print(f"Deployed TokenLinkerLockUnlock at {address}")


def deploy_mint_burn(asset: str, account: Optional[Account] = None):
    if asset == "AVAX":
        asset_name = "Avalanche Token"
        asset_symbol = "AVAX"
        asset_decimals = 18
        salt = AVAX_SALT
    elif asset == "USDC":
        asset_name = "USD Coin"
        asset_symbol = "USDC"
        asset_decimals = 6
        salt = USDC_SALT
    else:
        raise Exception("Not supported asset")
    print(f"Deploying TokenLinkerMintBurn to {network.show_active()}")
    if not account:
        account = get_account()
    token_linker_type = 1
    address = deploy_with_factory(
        account,
        token_linker_type,
        salt,
        name=asset_name,
        symbol=asset_symbol,
        decimals=asset_decimals,
    )
    print(f"Deployed TokenLinkerMintBurn at {address}")
