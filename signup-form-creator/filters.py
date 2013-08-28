""" In the `forms.py` file, our PageForm allows users to enter a description
    of their event. One of the things Flask does for us is sanitize user input
    to protect us from malicious entries. However, we want a user to be able
    to enter an address as multi-line input (without having a bunch of fields
    that may or may not be used, such as address1, address2, suite, city,
    state, zip).

    We use the nl2br filter (adapted from http://flask.pocoo.org/snippets/28/)
    to change line breaks in the user's entered text into HTML <br> tags, and
    mark that HTML as safe so it won't be escaped.
"""
import re

from jinja2 import evalcontextfilter, Markup, escape


@evalcontextfilter
def nl2br(eval_ctx, value):
    """ Maintain HTML safety but turn line breaks back into <br> """
    _paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')
    result = u'\n\n'.join(u'%s</br>' % p
                          for p in _paragraph_re.split(escape(value)))

    if eval_ctx.autoescape:
        result = Markup(result)

    return result
