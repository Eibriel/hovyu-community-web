import hashlib

from flask import request

from web_server import app

from web_server.modules.server_requests import post


def log_access():
    ip = '{1}{0}'.format(app.config['IP_LOG_SALT'], request.environ['REMOTE_ADDR'])
    ip = ip.encode('utf-8')
    ip_md5 = hashlib.sha224( ip ).hexdigest()
    access_log = {
        'page': request.url,
        'ip_md5': ip_md5,
        'useragent': request.user_agent.string,
        'useragent_platform': request.user_agent.platform,
        'useragent_browser': request.user_agent.browser,
        'useragent_version': request.user_agent.version,
        'useragent_language': request.user_agent.language,
        'acceptlanguage': request.accept_languages.to_header(),
        'referrer': request.referrer
    }

    #logging.error( access_log )
    r = post('access_log', access_log)
    #logging.error( r.text )
