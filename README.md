# Project setup

For compilation to work add the following into `~/.brownie/packages/axelarnetwork/token-linker@1.0.0/brownie-config.yaml`

```
dependencies:
  - axelarnetwork/axelar-utils-solidity@1.3.0
  - axelarnetwork/axelar-cgp-solidity@4.4.0
compiler:
  solc:
    remappings:
      - '@axelar-network/axelar-gmp-sdk-solidity=axelarnetwork/axelar-utils-solidity@1.3.0'
      - '@axelar-network/axelar-cgp-solidity=axelarnetwork/axelar-cgp-solidity@4.4.0'
```
