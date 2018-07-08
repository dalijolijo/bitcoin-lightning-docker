# Similar projects
 
* [Satoshi Portal Dockerfiles](https://github.com/SatoshiPortal/dockers)
 
* [How to dockerise a lightning app](https://github.com/schulterklopfer/howto_dockerise_a_lapp)

* [Bitcoin Cache Machine](https://github.com/farscapian/bitcoincachemachine)

* [Lightning Charge Docker-Compose](https://github.com/NicolasDorier/lightning-charge-docker)

# Quick Start Guide

1. `cp docker/sample_dot_env docker/.env` 

2. Update `RPCUSER`, `RPCPASSWORD`, & `RPCAUTH` entries in `docker/.env` with credentials obtained by following [these instructions](https://github.com/ruimarinho/docker-bitcoin-core#using-rpcauth-for-remote-authentication).

2. `cd docker && docker-compose up`

3. Open [http://127.0.0.1:5000/admin/](http://127.0.0.1:5000/admin/).



![Bitcoin Admin](https://raw.githubusercontent.com/PierreRochard/bitcoin-lightning-docker/master/readme_images/bitcoin_admin.png)



![Lightning Admin](https://raw.githubusercontent.com/PierreRochard/bitcoin-lightning-docker/master/readme_images/lightning_admin.png)

