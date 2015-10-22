from web_server import app

from flask import g
from flask import render_template
from web_server.modules.localization import domain_selector


# ABOUT
@app.route('/about')
def about():
    located_urls, redirect_response = domain_selector()
    if redirect_response:
        return redirect_response
    return render_template('about.html',
                            subtitle = "",
                            located_urls = located_urls,
                            locale = g.get('locale'))
