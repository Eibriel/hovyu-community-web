from web_server.config.default import Config

class Local(Config):
    DEBUG = False
    
    PAYMENT_SMTP_SERVER = ''
    PAYMENT_MAIL_FROM = ''
    PAYMENT_MAIL_USERNAME = ''
    PAYMENT_MAIL_PASSWORD = ''
