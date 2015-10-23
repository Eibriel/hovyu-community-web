from web_server import app

from flask import g
from flask import request
from flask import redirect


def get_localized_domains():
    available_locales = ['en', 'es', 'pt', 'zh_hans']
    localizations = []
    for loc in available_locales:
        url = '{0}://{1}.{2}'.format(request.scheme, loc.replace('_', '-'), app.config['ALLOWED_HOST'])
        localizations.append( {'url': url, 'locale': loc} )
    return localizations

def get_current_domain():
    current_domain = '{0}://{1}'.format(request.scheme, request.host)
    return current_domain


def locale_to_babel(locale):
    if locale == 'zh':
        locale = 'zh_Hans'
    return locale

def locale_to_url(locale):
    if locale == 'zh':
        locale = 'zh-hans'
    return locale

def domain_selector():
    # lan_domain
    # lan_agent
    # If lan_domain, lan is lan_domain
    # Elif not lan_domain and not lan_agent, lan is en
    # Elif not  lan_domain, la is lan_agent
    available_locales = ['en', 'es', 'pt', 'zh']
    locale = request.accept_languages.best_match( available_locales, 'en' )

    # CLEANUP FULL_PATH
    full_path = request.full_path
    if request.full_path[-1] == '?':
        full_path = request.full_path[:-1]
    if full_path == '/':
        full_path = ''

    located_hosts = []
    located_urls = []
    for loc in available_locales:
        located_host = '{0}.{1}'.format(locale_to_url(loc), app.config['ALLOWED_HOST'])
        located_hosts.append( located_host )
        if request.host == located_host:
            locale = loc

        located_host = {
            'url': '{0}://{1}{2}'.format(request.scheme, located_host, full_path),
            'locale': loc
        }
        located_urls.append(located_host)

    located_host = {
        'url': '{0}://{1}{2}'.format(request.scheme, app.config['ALLOWED_HOST'], full_path),
        'locale': 'x-default'
    }
    located_urls.append(located_host)

    g.locale = locale
    g.locale_babel = locale_to_babel(locale)

    redirect_response = None
    if request.host != '{0}.{1}'.format(locale_to_url(g.get('locale')), app.config['ALLOWED_HOST']):
        url = '{0}://{1}.{2}{3}'.format(request.scheme, locale_to_url(g.get('locale')), app.config['ALLOWED_HOST'], full_path)
        redirect_response = redirect( url, 301 )

    return located_urls, redirect_response
