from markupsafe import Markup

from app.lnd_client.peer_directory import peer_directory

def format_pub_key(long_pub_key: str):
    if long_pub_key:
        short_pub_key = long_pub_key[0:20]
        name = ''
        if peer_directory[long_pub_key].name:
            name = '<span class="label label-primary">{0}</span>'.format(peer_directory[long_pub_key].name)
        return Markup('<div style="white-space: nowrap; overflow: hidden;">{0} {1}</div>'.format(short_pub_key, name))
    else:
        return ''


def pub_key_formatter(view, context, model, name):
    long_pub_key = getattr(model, name)
    return format_pub_key(long_pub_key)


def path_formatter(view, context, model, name):
    pub_keys = getattr(model, name)
    formatted = '<br>'.join([format_pub_key(p) for p in pub_keys])
    return Markup(formatted)