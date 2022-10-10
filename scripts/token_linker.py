from typing import Optional

from brownie import (
    TokenLinkerFactory,
    TokenLinkerFactoryLookupProxy,
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
    web3,
)
from brownie.network.contract import Contract, ContractContainer
from eth_abi import encode
from eth_account import Account
from eth_hash.auto import keccak

from .common import Project, get_account, load_axelar_cgp, load_axelar_utils
from .const_address_deployer import const_address_deployer, deploy_and_init_contract
from .gas_receiver import gas_receiver
from .gateway import gateway

FACTORY_DEPLOYMENT_KEY = "factory"

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

TOKEN_LINKERS_INFO = {
    0: {
        "name": "Lock/Unlock",
        "factoryRef": "lockUnlock",
    },
    1: {
        "name": "Mint/Burn",
        "factoryRef": "mintBurn",
    },
    3: {
        "name": "Native",
        "factoryRef": "native",
        "value": True,
    },
}


def deploy_token_linker(
    contract: ContractContainer, account: Account, axelar_cgp: Optional[Project] = None
) -> str:
    if not account:
        account = get_account()
    if not axelar_cgp:
        axelar_cgp = load_axelar_cgp()
    contract_name = contract._name
    print(f"Deploying {contract_name} for {network.show_active()}")
    gateway_address = gateway(axelar_cgp).address
    gas_service_address = gas_receiver(axelar_cgp).address
    token_linker = contract.deploy(
        gateway_address, gas_service_address, {"from": account}
    )
    print(f"{contract_name} deployed at: {token_linker.address}")
    return token_linker.address


def deploy_fm(
    account: Optional[Account] = None, axelar_cgp: Optional[Project] = None
) -> list[str]:
    if not account:
        account = get_account()
    if not axelar_cgp:
        axelar_cgp = load_axelar_cgp()
    fm_linkers: list[str] = []
    for _, value in TOKEN_LINKERS_FM.items():
        fm_linkers.append(deploy_token_linker(value, account, axelar_cgp))
    return fm_linkers


def deploy_upgradeable(
    account: Optional[Account] = None, axelar_cgp: Optional[Project] = None
) -> list[str]:
    if not account:
        account = get_account()
    if not axelar_cgp:
        axelar_cgp = load_axelar_cgp()
    upgradeable: list[str] = []
    for _, value in TOKEN_LINKERS_UPGRADEABLE.items():
        upgradeable.append(deploy_token_linker(value, account, axelar_cgp))
    return upgradeable


def deploy_factory_implementation(
    account: Optional[Account] = None, axelar_cgp: Optional[Project] = None
) -> str:
    print(f"Deploying TokenLinkerFactory for {network.show_active()}")
    if not account:
        account = get_account()
    # Prepare codehash for proxies
    fm_proxy_bytecode = web3.toBytes(hexstr=TokenLinkerFactoryLookupProxy.bytecode)
    fm_proxy_codehash = keccak(fm_proxy_bytecode)
    self_lookup_proxy_bytecode = web3.toBytes(
        hexstr=TokenLinkerSelfLookupProxy.bytecode
    )
    upgradeable_proxy_codehash = keccak(self_lookup_proxy_bytecode)

    # Fetch gateway and gas service addresses
    if not axelar_cgp:
        axelar_cgp = load_axelar_cgp()
    gateway_address = gateway(axelar_cgp).address
    gas_service_address = gas_receiver(axelar_cgp).address

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
        TokenLinkerFactoryProxy,
        account,
        const_address_deployer,
        FACTORY_DEPLOYMENT_KEY,
        *init_params,
    )
    print(f"TokenLinkerFactoryProxy deployed at: {proxy_address}")
    return proxy_address


def deploy():
    account = get_account()
    axelar_cgp = load_axelar_cgp()
    axelar_utils = load_axelar_utils()
    fms = deploy_fm(account, axelar_cgp)
    upgradeable = deploy_upgradeable(account, axelar_cgp)
    cad_contract = const_address_deployer(axelar_utils)
    factory_impl_address = deploy_factory_implementation(account, axelar_cgp)
    factory_proxy_address = deploy_factory_proxy(
        cad_contract, factory_impl_address, upgradeable, fms, account=account
    )
    print("SUMMARY")
    print("----------------------------------------------------")
    print(f"-> Factory Proxy: {factory_proxy_address}")
    print("----------------------------------------------------")
