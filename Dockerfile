FROM grahamdumpleton/mod-wsgi-docker:python-3.4-onbuild

CMD [ "--working-directory", "web_server", \
      "--url-alias", "/web_server/static", "static", \
      "web_server.wsgi" ]
