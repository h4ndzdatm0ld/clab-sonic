# SONiC 202505 Dual Lab

Mirror of the dual-node topology but pinned to the `h4ndzdatm0ld/sonic-vm:202505` image. BGP comes pre-configured so you can focus on image-specific validation.

## Usage

1. Deploy from this directory:
   ```bash
   containerlab deploy -t topology.yml
   ```
2. Connect through the forwarded management ports (`22` and `2022`).
3. Destroy the lab when done:
   ```bash
   containerlab destroy -t topology.yml
   ```

Startup configurations are sourced from `./configs/` and keep BGP sessions up between the peers.
