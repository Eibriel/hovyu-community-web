FROM grahamdumpleton/mod-wsgi-docker:python-3.4

WORKDIR /app

RUN pip install babel

COPY . /app

RUN pybabel compile -d web_server/web_server/translations

RUN mod_wsgi-docker-build

EXPOSE 80
ENTRYPOINT [ "mod_wsgi-docker-start" ]

CMD [ "--compress-responses", "--working-directory", "web_server", \
      "--url-alias", "/web_server/static", "static", \
      "web_server.wsgi" ]
