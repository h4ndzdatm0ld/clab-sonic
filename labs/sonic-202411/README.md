# SONiC 202411 Dual Lab

Two SONiC containers (202411 image) configured with EBGP peering across two interconnect links. Use this lab to validate features specific to the 202411 drop or to regression test automation against a locked image tag.

## Usage

1. Deploy from this directory:
   ```bash
   containerlab deploy -t topology.yml
   ```
2. SSH to the nodes via the forwarded ports (`22` and `2022`).
3. Tear down when finished:
   ```bash
   containerlab destroy -t topology.yml
   ```

Startup configurations live under `./configs/` and already enable BGP between the peers.
