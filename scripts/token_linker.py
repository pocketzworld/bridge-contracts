from typing import Optional

from brownie import (
    TokenLinkerFactory,
    TokenLinkerFactoryProxy,
    TokenLinkerLockUnlockFactoryLookup,
    TokenLinkerLockUnlockUpgradable,
    TokenLinkerMintBurnExternalFactoryLookup,
    TokenLinkerMintBurnExternalUpgradable,
    TokenLinkerMintBurnFactoryLookup,
    TokenLinkerMintBurnUpgradable,
    TokenLinkerNativeFactoryLookup,
    TokenLinkerNativeUpgradable,
    TokenLinkerSelfLookupProxy,
    network,
)
from brownie.network.contract import Contract, ContractContainer, ContractConstructor
from eth_account import Account
from eth_hash.auto import keccak
from eth_abi import encode

from .common import get_account
from .const_address_deployer import (
    const_address_deployer,
    deploy_and_init_contract,
)

TOKEN_LINKERS_FM = {
    "LockUnlockFM": TokenLinkerLockUnlockFactoryLookup,
    "MintBurnFM": TokenLinkerMintBurnFactoryLookup,
    "MintBurnExternalFM": TokenLinkerMintBurnExternalFactoryLookup,
    "NativeFM": TokenLinkerNativeFactoryLookup,
}

TOKEN_LINKERS_UPGRADEABLE = {
    "LockUnlock": TokenLinkerLockUnlockUpgradable,
    "MintBurn": TokenLinkerMintBurnUpgradable,
    "MintBurnExternal": TokenLinkerMintBurnExternalUpgradable,
    "Native": TokenLinkerNativeUpgradable,
}


def deploy_token_linker(contract: ContractContainer, account: Account) -> str:
    if not account:
        account = get_account()
    contract_name = contract._name
    print(f"Deploying {contract_name} for {network.show_active()}")
    token_linker = contract.deploy(account.address, account.address, {"from": account})
    print(f"{contract_name} deployed at: {token_linker.address}")
    return token_linker.address


def deploy_fm() -> list[str]:
    account = get_account()
    fm_linkers: list[str] = []
    for _, value in TOKEN_LINKERS_FM.items():
        fm_linkers.append(deploy_token_linker(value, account))
    return fm_linkers


def deploy_upgradeable() -> list[str]:
    account = get_account()
    upgradeable: list[str] = []
    for _, value in TOKEN_LINKERS_UPGRADEABLE.items():
        upgradeable.append(deploy_token_linker(value, account))
    return upgradeable


def deploy_factory_implementation(account: Optional[Account] = None) -> str:
    print(f"Deploying TokenLinkerFactory for {network.show_active()}")
    if not account:
        account = get_account()
    # Prepare codehash for proxies
    fm_proxy_bytecode = bytes(TokenLinkerFactoryProxy.bytecode, "utf-8")
    fm_proxy_codehash = keccak(fm_proxy_bytecode)
    self_lookup_proxy_bytecode = bytes(TokenLinkerSelfLookupProxy.bytecode, "utf-8")
    upgradeable_proxy_codehash = keccak(self_lookup_proxy_bytecode)

    # TODO(@mculinovic)
    # Fetch gateway and gas service addresses
    gateway_address = account.address
    gas_service_address = account.address

    # Deploy factory implementation
    factory = TokenLinkerFactory.deploy(
        fm_proxy_codehash,
        upgradeable_proxy_codehash,
        gateway_address,
        gas_service_address,
        {"from": account},
    )
    print(f"TokenLinkerFactory deployed at: {factory.address}")
    return factory.address


def deploy_factory_proxy(
    const_address_deployer: Contract,
    factory_impl_address: str,
    upgradeable_impl_addresses: list[str] = [],
    fm_impl_addresses: list[str] = [],
    account: Optional[Account] = None,
) -> str:
    print(f"Deploying TokenLinkerFactoryProxy for {network.show_active()}")
    init_params = [
        factory_impl_address,
        account.address,
        encode(
            [
                "address[]",
                "address[]",
            ],
            [fm_impl_addresses, upgradeable_impl_addresses],
        ),
    ]
    proxy_address = deploy_and_init_contract(
        TokenLinkerFactoryProxy, account, const_address_deployer, *init_params
    )
    print(f"TokenLinkerFactoryProxy deployed at: {proxy_address}")
    return proxy_address


def deploy():
    account = get_account()
    fms = deploy_fm()
    upgradeable = deploy_upgradeable()
    cad_contract = const_address_deployer(account)
    factory_impl_address = deploy_factory_implementation(account)
    factory_proxy_address = deploy_factory_proxy(
        cad_contract, factory_impl_address, upgradeable, fms, account=account
    )
