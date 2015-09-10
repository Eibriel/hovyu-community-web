from web_server.config.default import Config

class Local(Config):
    DEBUG = False
    CANONICAL_DOMAIN = 'http://hovyu.com'
