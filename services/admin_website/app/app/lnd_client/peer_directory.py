from collections import namedtuple, defaultdict

Peer = namedtuple('Peer', ['pub_key', 'address', 'name'])


def build_directory():
    htlc_dot_me = Peer(
        '03193d512b010997885b232ecd6b300917e5288de8785d6d9f619a8952728c78e8',
        '18.205.112.169:9735',
        'htlc.me')

    yalls = Peer(
        '02212d3ec887188b284dbb7b2e6eb40629a6e14fb049673f22d2a0aa05f902090e',
        'testnet-lnd.yalls.org',
        "Y'alls"
    )

    peers = [
        htlc_dot_me,
        yalls
    ]

    def peer_factory():
        return Peer(None, None, '')

    directory = defaultdict(peer_factory)
    for peer in peers:
        directory[peer.pub_key] = peer
    return directory


peer_directory = build_directory()
