import os

from boto.s3.key import Key
from boto.s3.connection import S3Connection
from flask import Flask, request, render_template
from pbkdf2 import crypt

import forms
import filters
import models
import settings


app = Flask(__name__)
app.config.update(SECRET_KEY=settings.FLASK_SECRET_KEY)
app.add_template_filter(filters.nl2br)


@app.route('/', methods=['GET', 'POST'])
def create_page():
    """ Main view to present the user with a form to create a signup page. """
    form = forms.PageForm(request.form)
    error = None

    if request.method == 'POST' and form.validate():

        # if password incorrect or not entered, show an error
        if not valid_password(form.password.data):
            error = "Must enter correct password."
            return render_template('main.html', form=form, error=error)

        # password was correct; render and upload the signup page
        event = models.Event(form.title.data, form.description.data,
                             form.date.data, form.time.data,
                             form.address.data, form.entry.data)
        page_to_upload = render_template('signup_page.html', event=event)
        bucket = (settings.PRODUCTION_BUCKET if form.production.data
                  else settings.STAGING_BUCKET)
        key = clean_key(form.filename.data)
        upload(bucket, key, page_to_upload)
        url = settings.S3_URL % (bucket, key)
        return render_template('main.html', form=form, success=True, url=url)

    # if request was a GET just return the main page
    return render_template('main.html', form=form, error=error)


def upload(bucket_name, page_key, content):
    """ Upload the generated page to S3 as a file. """
    conn = S3Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
    bucket = conn.get_bucket(bucket_name)
    k = Key(bucket)
    k.key = page_key # key is what S3 calls the filename
    k.set_metadata('Content-Type', 'text/html; charset=utf-8')
    k.set_contents_from_string(content)
    return True


def clean_key(filename):
    """ Make sure the file goes where we want it in S3, with a good key. """
    cleaned = filename.split('.')[0].strip().lower()
    return settings.S3_KEY_FORMAT % cleaned


def valid_password(user_pw_entry):
    """ Without SSL this is not secure!

    This is a demonstration of the idea behind password hashing, NOT a full
    implementation. Flask already offers login functionality in the flask-login
    package (https://flask-login.readthedocs.org/en/latest/).
    """
    user_entry_pw_hash = crypt(user_pw_entry, settings.FLASK_SECRET_KEY)
    app.logger.info(user_entry_pw_hash)
    return user_entry_pw_hash == settings.PASSWORD_HASH

# This will never be run by Gunicorn, only if we start the app with `python app.py`
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
