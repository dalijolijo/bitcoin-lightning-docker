import bitcoin
import time

proxy = bitcoin.rpc.Proxy(btc_conf_file='bitcoin.conf')

while True:
    block_hashes = proxy.call('generate', 1)
    time.sleep(10)
