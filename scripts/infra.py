from .common import load_axelar_cgp, load_axelar_utils
from .const_address_deployer import deploy as deploy_const_address_deployer
from .gas_receiver import deploy as deploy_gas_receiver
from .gateway import deploy as deploy_gateway


def deploy():
    axelar_cgp = load_axelar_cgp()
    axelar_utils = load_axelar_utils()
    gateway_address = (deploy_gateway(axelar_cgp)).address
    cad_address = (deploy_const_address_deployer(axelar_utils)).address
    gas_receiver_address = (deploy_gas_receiver(axelar_cgp)).address
    print("SUMMARY")
    print("----------------------------------------------------")
    print(f"-> Gateway: {gateway_address}")
    print(f"-> ConstAddressDeployer: {cad_address}")
    print(f"-> GasService: {gas_receiver_address}")
    print("----------------------------------------------------")
