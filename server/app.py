#!/usr/bin/env python

import shelve
from subprocess import check_output
import flask
from flask import request, Flask, render_template #This seems unneccessary
import os
import string
import random

app = flask.Flask(__name__)
app.debug = True

db = shelve.open("shorten.db")      # this is an artifact from jblomo's code
urldb = shelve.open("urlkey.db")    # this is our database that uses url as a key
codedb = shelve.open("codekey.db")  # this is our database that uses the short code as a key

###
#Useful functions
###
def random_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

###
# Home Resource:
# Only supports the GET method, returns a homepage represented as HTML
###
@app.route('/home', methods=['GET'])
def home():
    return flask.redirect(flask.url_for('form_method_handling'))


###
# Wiki Resource:
# GET method will redirect to the resource stored by PUT, by default: Wikipedia.org
# POST/PUT method will update the redirect destination
###
@app.route('/wiki', methods=['GET'])
def wiki_get():
    """Redirects to wikipedia."""
    destination = db.get('wiki', 'http://en.wikipedia.org')
    app.logger.debug("Redirecting to " + destination)
    return flask.redirect(destination)

@app.route("/wiki", methods=['PUT', 'POST'])
def wiki_put():
    """Set or update the URL to which this resource redirects to. Uses the
    `url` key to set the redirect destination."""
    wikipedia = request.form.get('url', 'http://en.wikipedia.org')
    db['wiki'] = wikipedia
    return "Stored wiki => " + wikipedia

###
# i253 Resource:
# Information on the i253 class. Can be parameterized with `relationship`,
# `name`, and `adjective` information
##/
@app.route('/i253')
def i253():
    """Returns a PNG image of madlibs text"""
    relationship = request.args.get("relationship", "friend")
    name = request.args.get("name", "Jim")
    adjective = request.args.get("adjective", "fun")

    resp = flask.make_response(
            check_output(['convert', '-size', '600x400', 'xc:transparent',
                '-frame', '10x30',
                '-font', '/usr/share/fonts/liberation/LiberationSerif-BoldItalic.ttf',
                '-fill', 'black',
                '-pointsize', '32',
                '-draw',
                  "text 30,60 'My %s %s said i253 was %s'" % (relationship, name, adjective),
                '-raise', '30',
                'png:-']), 200);
    # Comment in to set header below
    # resp.headers['Content-Type'] = '...'

    return resp

###
# global variables for use within various routes
###
form_full_url = None
form_url_code = None

###
# this is our input form for the shortener
###
@app.route('/crisco', methods=['GET'])   
def form_method_handling(): 
    return flask.render_template('crisco_input.html')

###
# when the crisco form is submitted, it sends a post to this route for processing
###
@app.route('/shorts', methods=['POST'])
def confirm_submission():
    form_full_url = str(request.form.get('full_url')).strip() #previously request.form['full_url']
    form_url_code = str(request.form.get('url_code')).strip() #flask does weird shit. Stringification?
    if urldb.has_key(form_full_url):
        # this is not a true confirmation - the user is informed that a code already exists
        return flask.render_template('confirmation2.html', input_full_url=form_full_url, input_url_code=urldb[form_full_url])
    elif codedb.has_key(form_url_code):
        # this is not a true confirmation - the user is informed that the url has already been shortened
        return flask.render_template('confirmation3.html', input_full_url=form_full_url, input_url_code=form_url_code)
    else:
        # this one is a true confirmation!
        codedb[form_url_code] = form_full_url
        urldb[form_full_url] = form_url_code
        return flask.render_template('confirmation.html', input_full_url=form_full_url, input_url_code=form_url_code)

###
# this is the route that handles redirects when a user enters a short code as part of the url
###
@app.route('/short/<short_code>', methods=['GET'])
def redirection(short_code=None):
    short_code = str(short_code)
    if codedb.has_key(short_code):
        # full url was found - redirect
        destination = codedb[short_code]
        return flask.redirect(destination)
    else:
        # full url not found - direct them to the sassy 404 page
        return flask.render_template('404.html')

if __name__ == "__main__":
    app.run(debug=True)
