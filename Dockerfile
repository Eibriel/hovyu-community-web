FROM grahamdumpleton/mod-wsgi-docker:python-3.4

WORKDIR /app

RUN pip install Flask
RUN pip install requests

COPY . /app

RUN mod_wsgi-docker-build

EXPOSE 80
ENTRYPOINT [ "mod_wsgi-docker-start" ]

CMD [ "--working-directory", "web_server", \
      "--url-alias", "/web_server/static", "static", \
      "web_server.wsgi" ]
