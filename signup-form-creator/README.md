# Flask to S3 Page Creator

Takes user input in a form, renders a template based on that input into an HTML page, then uploads the rendered page to
your Amazon S3 bucket for hosting.

## Description

This app was originally created for use by the Data and Reporting team in [Ed Markey's](http://en.wikipedia.org/wiki/Ed_Markey)
2013 Massachusetts Senate campaign. It was used to automate the deployment of multiple themed event signup pages, so
that non-technical campaign staff could create individualized signup pages for their regions without touching
HTML/CSS/JS or having an S3 login.

These static, generated signup forms ([here's an example](http://boston-python-talk.s3-website-us-east-1.amazonaws.com/signups/test-page.html))
were hosted on S3, so links could be e-mailed out and spread through social media, and were used to gather commitments
from volunteers throughout the state. When submitted, all of these customized forms fed into the same Google Form
spreadsheet (explanation of how to submit from an arbitrary page to a Google Form [here](http://www.immersionmedia.com/blog/customizing-and-styling-google-forms/)).

The original app has been adapted and generalized to accompany a talk for the [Boston Python User Group](http://www.meetup.com/bostonpython/)
August 2013 Presentation Night. The idea is to demonstrate some useful Flask techniques and building blocks, such as:

*  Setting up a Flask app for deployment to Heroku.
*  Using `foreman` to test locally, defining a `Procfile`, and keeping configuration variables separated from
   application logic using a `.env` file.
*  Using `boto` to interact with Amazon S3.
*  Using `wtforms` for form rendering and validation.
*  Using `pbkdf2` for a simple example of password hashing.
*  Defining a custom template filter.
*  Defining a template macro.
*  Using [BootstrapCDN](http://www.bootstrapcdn.com/) to serve your Bootstrap assets for free, including versions
   of Bootstrap with [different themes](http://www.bootstrapcdn.com/#tab_bootswatch).

## Installation

### Additional accounts and tools

In addition to installing the packages listed in `requirements.txt` to your [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs.html),
you will need:

*  A free [Amazon AWS](http://aws.amazon.com/) account with two S3 buckets set up, one for production and one for
   staging.
*  A free [Heroku](http://www.heroku.com/) account and the Heroku [tools](https://toolbelt.heroku.com/).
   Follow Steps 1 to 3 of [these instructions](https://devcenter.heroku.com/articles/quickstart).

### Configuration variables

We use configuration variables to keep certain settings and secrets separate from our application logic, and out of
version control. One file that is not stored in this repository, and that you should not store in your public
repository, is the `.env` file that Foreman uses to establish configuration variables before launching an application
locally.

First, create a `.env` file in the top directory of this repository. These are the keys that the `.env` file should
contain:

```
FLASK_SECRET_KEY=yoursecretkey
AWS_ACCESS_KEY=your-aws-access-key
AWS_SECRET_KEY=your-aws-secret-key
STAGING_BUCKET=your-staging-bucket
PRODUCTION_BUCKET=your-production-bucket
PASSWORD_HASH=$p5k2$$yoursecretkey$LWF4bX66WyoCTo7R0lf/AFm/WG2SLh5I
```

#### Explanation:

* `FLASK_SECRET_KEY` is the secret key Flask uses to encrypt cookies. The Flask docs have a good [explanation](http://flask.pocoo.org/docs/quickstart/#sessions)
of how the secret key is used and how to generate a secret key. It doesn't play much of a role in our example app here,
but we will use is as the salt for our password hashing.

* `AWS_ACCESS_KEY` and `AWS_SECRET_KEY` are unique to your Amazon AWS account, which you can get (once logged in)
[here](https://portal.aws.amazon.com/gp/aws/securityCredentials).

* `STAGING_BUCKET` and `PRODUCTION_BUCKET` are buckets that you create in your S3 acccount. They can be named anything
that conforms to S3's rules, for example `my-flask-bucket`. These will be part of the URL for your hosted pages, for
example `http://my-flask-bucket.s3.amazonaws.com/example-page.html`.

* `PASSWORD_HASH` allows us to store a password without keeping it in plaintext.

  > DISCLAIMER: I'm not a security professional, and you probably aren't either. This is just intended to demonstrate
  the basics of password hashing, not actually to be considered secure. For starters, we are not even using SSL for this
  example app. That means that the password a user enters will be transmitted in plaintext. Do not rely solely only this
  protection in production.

  Let's assume we want the password for this app to be `yourpassword`. We're using the [PBKDF2](https://github.com/dlitz/python-pbkdf2)
  key derivation function to hash the password, with the default of 400 iterations, and we're using our app's secret key
  as a [salt](https://en.wikipedia.org/wiki/Salt_(cryptography)). To create the password hash we'll be storing in
  `.env`, open a Python interpreter:

  ```python
  from pbkdf2 import crypt
  crypt('yourpassword', 'yoursecretkey')
  ```

  What we get out is a hash, `u'$p5k2$$yoursecretkey$LWF4bX66WyoCTo7R0lf/AFm/WG2SLh5I'`. In this string, we can see the
  crypt format identifier `p5k2`, our salt, and the hash. If you want to read more about this, there is some good
  information [here](http://pythonhosted.org/passlib/lib/passlib.hash.dlitz_pbkdf2_sha1.html).

  Now, when a user submits a password, we can hash it right away and compare the new hash with our stored hash,
  without ever storing the password in plaintext. Even better, we don't even expose the hash because we're going to
  keep `.env` in our `.gitignore`.

## Running locally

To run this app locally, navigate to the root directory and run:

`foreman start`

Foreman is one of the tools that comes with the Heroku install. It will use the file called `Procfile` to figure out how
to serve our Flask app. Right now, our Procfile says this:

`web: gunicorn app:app`

That tells Foreman that there is a web process, and to use [Gunicorn](http://docs.gunicorn.org/en/latest/) to serve the
app.

#### Why do we have to use a different server like Gunicorn? Why don't we just run `python app.py`?

As the Flask docs [explain](http://flask.pocoo.org/docs/deploying/), the built-in server was not designed for use in
production. This is important because as we will discuss in the next section, Heroku uses your `Procfile` to figure out
how to run the app in production.

#### But what if we want to use the great debugging functionality that the Flask server comes with?

Well, we can set up another file for Foreman to use -- we'll call it `Procfile.dev` -- and it will contain the following:

`web: python app.py`

Because we know we'll only be using the built-in server for development, we've already set ourselves up so we get those
nice debug features if we ever run the app with `python app.py`. This is at the bottom of our `app.py`:

```python
# This will never be run by Gunicorn, only if we start the app with `python app.py`
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
```

Notice that we tell the app to run in debug mode -- that means we will get the interactive traceback page if there are
any errors. Now we're ready to run with our "dev" setup. Since we're using a config file named something other than
`Procfile`, we run Foreman with one extra argument:

`foreman start -f Procfile.dev`

If you do that, you should see something like the following:

```
22:33:51 web.1  | started with pid 7161
22:33:51 web.1  |  * Running on http://0.0.0.0:5000/
22:33:51 web.1  |  * Restarting with reloader
```

This tells us that the app is running. If you open up a browser, and type in `http://localhost:5000/` you should see our
page.

#### If Foreman is just running `python app.py`, why don't we just skip Foreman and run the server with `python app.py`?

Don't forget about the `.env` file Foreman uses to set up your configuration variables. If you try to run plain old
`python app.py`, you'll get a traceback because code in `settings.py` will fail to find the environment variables we try
to access, such as `FLASK_SECRET_KEY`.

## Deploying to Heroku

Heroku has excellent documentation. They have an [nice walkthrough](https://devcenter.heroku.com/articles/python)
of deploying a Flask app. You should read that -- it covers just about everything.

The relevant sections for us though are [getting the Heroku tools set up](https://devcenter.heroku.com/articles/python#local-workstation-setup),
and then [deploying](https://devcenter.heroku.com/articles/python#deploy-your-application-to-heroku). (We can skip the
middle since that is setting up stuff we already took care of).

We'll also use [these directions](https://devcenter.heroku.com/articles/config-vars#using-foreman-and-heroku-config)
on pushing all the configuration variables in `.env` directly to Heroku without doing it one-by-one.

Here's the TL;DR version:

```
# you don't need the git commands if you cloned this repo
git init
git add .
git commit -m "initial commit"
# set up a new, randomly-named Heroku app, and create a git remote called heroku we can push to
heroku create
# push our config vars from .env to our new Heroku app
heroku plugins:install git://github.com/ddollar/heroku-config.git
heroku config:push
# push this last commit to Heroku to be run
git push heroku master
# open the newly deployed site in your default browser
heroku open
```
