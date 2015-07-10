import re

from web_server import app

from web_server.modules.wid import wid_chars

from jinja2 import evalcontextfilter, Markup, escape

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
        for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result

@app.template_filter()
@evalcontextfilter
def char2emoji(eval_ctx, value, size='36'):
    for wid_char in wid_chars:
        img_name = "{0:x}".format(wid_char)
        img_tag = '<img src="/static/twemoji/{2}x{2}/{0}.png" alt="{1}"/>'.format(img_name, chr(wid_char), size)
        value = value.replace(chr(wid_char), img_tag)
    if eval_ctx.autoescape:
        value = Markup(value)
    return value

@app.template_filter()
@evalcontextfilter
def money_scale_inverse(eval_ctx, value, currency):
    if type(value) != int:
        return "ERROR"
    if currency == 'btc':
        return "{0}".format(value / 100000000)
    else:
        return "{0}".format(value / 1000)
    return value
