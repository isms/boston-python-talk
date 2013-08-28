import os


AWS_ACCESS_KEY = os.environ['AWS_ACCESS_KEY']
AWS_SECRET_KEY = os.environ['AWS_SECRET_KEY']
STAGING_BUCKET = os.environ['STAGING_BUCKET']
PRODUCTION_BUCKET = os.environ['PRODUCTION_BUCKET']
PASSWORD_HASH = os.environ['PASSWORD_HASH']
FLASK_SECRET_KEY = os.environ['FLASK_SECRET_KEY']

S3_URL = 'http://%s.s3-website-us-east-1.amazonaws.com/%s'
S3_KEY_FORMAT = 'signups/%s.html'