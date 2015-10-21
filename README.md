# hovyu-community-web
Web server for HOVYU Community
Running at http://Hovyu.com

extract -F babel.cfg -o messages.pot .
pybabel init -i messages.pot -d translations -l es
Translate
pybabel compile -d translations
