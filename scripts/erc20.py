from brownie import network, web3
from brownie.network.contract import Contract

from .common import get_account, load_axelar_utils


def deploy(name: str, symbol: str, decimals: int):
    print(f"Deploying ERC20: {name} {symbol} {decimals} to {network.show_active()}")
    axelar = load_axelar_utils()
    account = get_account()
    contract = axelar.ERC20MintableBurnable.deploy(
        name, symbol, decimals, {"from": account}
    )
    print(f"Deployed ERC20: {name} {symbol} {decimals} to address {contract.address}")


def mint(erc20_address: str, amount: int):
    account = get_account()
    print(f"Minting {amount} {erc20_address} tokens to {account}")
    axelar = load_axelar_utils()
    contract = Contract.from_abi(
        "ERC20MintableBurnable", erc20_address, axelar.ERC20MintableBurnable.abi
    )
    contract.mint(account, web3.toWei(amount, "ether"), {"from": account}).wait(1)
    print(f"Minted {amount} {erc20_address} tokens to {account}")


def get_balance(erc20_address: str, account: str):
    axelar = load_axelar_utils()
    contract = Contract.from_abi(
        "ERC20MintableBurnable", erc20_address, axelar.ERC20MintableBurnable.abi
    )
    print(contract.balanceOf(account))
