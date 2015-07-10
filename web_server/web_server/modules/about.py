from web_server import app

from flask import render_template


# ABOUT
@app.route('/about')
def about():
    return render_template('about.html')
