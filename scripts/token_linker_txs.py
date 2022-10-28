from brownie import Contract, config, network, web3
from eth_abi import encode
from eth_hash.auto import keccak

from .common import get_account, load_axelar_token_linker, load_axelar_utils
from .token_linker_assets import AVAX_SALT, RISE_SALT, USDC_SALT

token_linker_project = load_axelar_token_linker()
axelar = load_axelar_utils()


def get_token_linker_native(account_address: str, salt: str) -> Contract:
    factory_address = config["networks"][network.show_active()].get(
        "tokenLinkerFactory"
    )
    factory = token_linker_project.interface.ITokenLinkerFactory(factory_address)
    salt = keccak(encode(["string"], [salt]))
    id = factory.getTokenLinkerId(account_address, salt)
    address = factory.tokenLinker(id, True)
    print(address)
    token_linker = Contract.from_abi(
        "Native", address, token_linker_project.TokenLinkerNativeFactoryLookup.abi
    )
    return token_linker


def get_salt(asset_type: str) -> str:
    if asset_type == "RISE":
        salt = RISE_SALT
    elif asset_type == "AVAX":
        salt = AVAX_SALT
    elif asset_type == "USDC":
        salt = USDC_SALT
    else:
        raise Exception("Asset not supported")
    return salt


def get_native_balance(asset_type: str):
    salt = get_salt(asset_type)
    account = get_account()
    token_linker = get_token_linker_native(account.address, salt)
    balance = token_linker.getNativeBalance()
    print(web3.fromWei(balance, "ether"))


def update_native_balance(asset_type: str, amount: int):
    salt = get_salt(asset_type)
    account = get_account()
    token_linker = get_token_linker_native(account.address, salt)
    balance = token_linker.getNativeBalance()
    print(f"Balance before {web3.fromWei(balance, 'ether')}")
    token_linker.updateBalance(
        {"from": account, "value": web3.toWei(amount, "ether")}
    ).wait(1)
    balance = token_linker.getNativeBalance()
    print(f"Balance after {web3.fromWei(balance, 'ether')}")


def get_token_linker(
    account_address: str, salt: str
) -> token_linker_project.interface.ITokenLinker:
    factory_address = config["networks"][network.show_active()].get(
        "tokenLinkerFactory"
    )
    factory = token_linker_project.interface.ITokenLinkerFactory(factory_address)
    salt = keccak(encode(["string"], [salt]))
    id = factory.getTokenLinkerId(account_address, salt)
    address = factory.tokenLinker(id, True)
    token_linker = token_linker_project.interface.ITokenLinker(address)
    print(f"Token linker at: {address}")
    return token_linker


def approve_token(asset_type: str, amount: int):
    salt = get_salt(asset_type)
    amount = web3.toWei(amount, "ether")
    account = get_account()
    token_linker = get_token_linker(account.address, salt)
    token_address = token_linker.token()
    token = axelar.interface.IERC20(token_address)
    token.approve(token_linker.address, amount, {"from": account}).wait(1)


def send_token(asset_type: str, amount: int, to_chain: str):
    salt = get_salt(asset_type)
    amount = web3.toWei(amount, "ether")
    account = get_account()
    token_linker = get_token_linker(account.address, salt)
    value = 3000000
    value = value + amount if token_linker.implementationType() == 3 else value
    token_linker.sendToken(
        to_chain,
        account.address,
        amount,
        {
            "from": account,
            "value": value,
            "gas_limit": 10000000,
        },
    )


def send_erc20(asset_type: str, amount: int, to_chain: str):
    approve_token(asset_type, amount)
    send_token(asset_type, amount, to_chain)
