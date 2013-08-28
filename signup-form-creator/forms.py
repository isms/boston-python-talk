from wtforms import Form, validators
from flask.ext.wtf import TextField, TextAreaField, PasswordField, BooleanField


class PageForm(Form):
    """ This class extends the base Form class from the wtforms package,
        which takes care of validation and other details for us. """
    title = TextField('Event title (e.g. Lowell GOTV Rally)',
                      [validators.Required()])

    date = TextField('Date (e.g. June 24, 2013)')

    time = TextField('Time (e.g. 2:30 pm)')

    address = TextAreaField('Address')

    description = TextAreaField('Description')

    entry = TextAreaField('Event info to be submitted to the Google Doc')

    filename = TextField('Short name for this signup page, to be used for the '
                         'filename (e.g. lowell-rally)',
                         [validators.Length(min=6, max=35)])

    production = BooleanField('I have previewed by submitting once without '
                              'checking this box, and am now ready to upload '
                              'it as final (if left unchecked, the page will '
                              'be uploaded to the staging bucket for preview)')

    password = PasswordField('Password')
