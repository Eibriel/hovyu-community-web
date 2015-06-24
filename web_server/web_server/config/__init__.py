try:
    from web_server.config.local import Local as Config
except :
    from web_server.config.default import Config
