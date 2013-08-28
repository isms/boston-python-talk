""" Normally in a Flask project, this file would hold database models,
    typically using SQLAlchemy. That is overkill for us, so we are using
    a namedtuple instead. In fact, we don't even really need to split this
    into a separate file, but it's a good habit to be in since it mirrors
    the directory pattern for any project that uses a database (which is
    most).
"""
from collections import namedtuple

Event = namedtuple('Event', 'title description date time address entry')
