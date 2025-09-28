# SONiC Containerlab Samples

This repository carries two minimal Containerlab scenarios that boot pre-configured SONiC virtual routers. Use them to validate h4ndzdatm0ld images tagged for the 202411 and 202505 releases.

## Layout

- `labs/sonic-202411/` — dual-node topology pinned to `h4ndzdatm0ld/sonic-vm:202411`
- `labs/sonic-202505/` — dual-node topology pinned to `h4ndzdatm0ld/sonic-vm:202505`
- `labs/sonic-202411/configs/` and `labs/sonic-202505/configs/` — startup `config_db.json` files consumed by each lab (BGP already enabled between peers)

## Quick Start

```bash
cd labs/sonic-202411
containerlab deploy -t topology.yml
# test things…
containerlab destroy -t topology.yml
```

Switch to `labs/sonic-202505` to test the newer image. Update the configs under each lab's `configs/` directory if you need to tweak BGP peers, interfaces, or feature flags.
