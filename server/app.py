import sqlite3
from subprocess import check_output
import flask
# This seems unneccessary because of the above, but commenting it out raises errors
from flask import request, Flask, render_template 
import os
import string
import random

app = flask.Flask(__name__)
app.debug = True

###
# global variables for use within various routes
###
form_full_url = None
form_url_code = None



#############################################################################
# DATABASE STUFF
#############################################################################

# ------------------------------------------
# make a sqlite connection to the database file. 
# if it doesn't exist it will be created. 
# create a cursor.
# if the file didn't exist before, create the table structure
#
# note that since these initial statements don't build an insert from
# web input, we're safe from sql injection
# when taking web input, we need to use the format:
# c.execute("select x from ? where z = ?", (TABLEVAR, "blahblah"))
# ------------------------------------------
connection = sqlite3.connect('crisco_db.txt')
db_cursor = connection.cursor()
db_cursor.execute('create table if not exists crisco (tag TEXT, \
                                                        url TEXT, \
                                                        popularity TEXT, \
                                                        random TEXT)')
# testing
# db_cursor.execute("insert into crisco values ('rena','http://renacoen.com','1','Y')")

#connection.commit()
connection.close()

# ------------------------------------------
# given a tag, return Y or N depending on whether it exists in the db
# ------------------------------------------
def tag_exists(in_tag):
    print "in function tag_exists"
    connection = sqlite3.connect('crisco_db.txt')
    db_cursor = connection.cursor()
    db_cursor.execute("select tag from crisco where tag = ?", (str(in_tag),))
    result = db_cursor.fetchall()
    connection.close()
    
    if len(result) == 0:
        return 'N'
    else:
        return 'Y'

# ------------------------------------------
# given a url, return Y or N depending on whether it exists in the db
# ------------------------------------------
def url_exists(in_url):
    print "in function url_exists"
    connection = sqlite3.connect('crisco_db.txt')
    db_cursor = connection.cursor()
    db_cursor.execute("select 'x' from crisco where url = ?", (str(in_url),))
    result = db_cursor.fetchall()
    connection.close()

    if len(result) == 0:
        return 'N'
    else:
        return 'Y'

# ------------------------------------------
# given a url and tag, return Y or N depending on whether there is a full match row
# ------------------------------------------
def full_match_exists(in_url,in_tag):
    print "in function full_match_exists"
    connection = sqlite3.connect('crisco_db.txt')
    db_cursor = connection.cursor()
    db_cursor.execute("select 'x' from crisco where url = ? and tag = ?", (str(in_url),str(in_tag),))
    result = db_cursor.fetchall()
    connection.close()

    if len(result) == 0:
        return 'N'
    else:
        return 'Y'

# ------------------------------------------
# given a single tag, return the url associated with it
# ------------------------------------------
def get_url(in_tag):
    print "in function get_url"
    connection = sqlite3.connect('crisco_db.txt')
    db_cursor = connection.cursor()
    #print db_cursor.execute("select url from crisco where tag = ?", (str(in_tag)))
    for row in db_cursor.execute("select url from crisco where tag = ?", (str(in_tag),)):
        curr_url = str(row[0])
        return curr_url
    connection.close()

# ------------------------------------------
# find the existing random tag for a url, if one exists
# ------------------------------------------
def get_random_tag(in_url):
    print "in function get_random_tag"
    #   tag_list.append(str(row[0]))
    connection = sqlite3.connect('crisco_db.txt')
    db_cursor = connection.cursor()
    db_cursor.execute("select tag from crisco where url = ? and random = 'Y'", (str(in_url),))
    #tag_list = db_cursor.fetchall()
    tag = db_cursor.fetchall()
    connection.close()
    
    if len(tag)==0:
        return ''
    else:
        return tag[0][0]

'''
# ------------------------------------------
# given a url, return the list of tags associated with it
# ------------------------------------------
def get_tags(in_url):
    print "in function get_tags"
    #tag_list = []
    #for row in db_cursor.execute("select tag from crisco where url = ?", (str(in_url))):
    #   tag_list.append(str(row[0]))
    connection = sqlite3.connect('crisco_db.txt')
    db_cursor = connection.cursor()
    db_cursor.execute("select tag from crisco where url = ?", (str(in_url),))
    tag_list = db_cursor.fetchall()
    connection.close()
    return tag_list
'''

# ------------------------------------------
# given a short, url, and random flag, insert a new row (default random to N)
# ------------------------------------------
def insert_row(in_tag, in_url, in_random_flag='N'):
    print "in function insert_row"
    connection = sqlite3.connect('crisco_db.txt')
    db_cursor = connection.cursor()
    db_cursor.execute("insert into crisco values (?,?,'1',?)", (str(in_tag), str(in_url), str(in_random_flag),))
    connection.commit()
    for row in db_cursor.execute("select tag, url, popularity, random from crisco"):
        print row[0] +', '+ row[1] +', '+ row[2] +', '+  row[3]
    connection.close()

# ------------------------------------------
# increment the popularity count for a tag/url combo
# ------------------------------------------
def update_popularity(in_tag):
    print "in function update_popularity"
    connection = sqlite3.connect('crisco_db.txt')
    db_cursor = connection.cursor()
    db_cursor.execute("update crisco set popularity = popularity + 1 where tag = ?", (str(in_tag),))
    connection.commit()
    for row in db_cursor.execute("select tag, popularity from crisco where tag = ?", (str(in_tag),)):
        print row[0] + ', ' + row[1]
    connection.close()


#############################################################################
# OTHER FUNCTIONS
#############################################################################

# ------------------------------------------
# generate a random tag
# ------------------------------------------
def random_generator(size=6, chars=string.ascii_lowercase + string.digits):
    print "in function random_generator"
    random_code = ''.join(random.choice(chars) for x in range(size))
    if tag_exists(random_code) == 'Y':
        # if the random tag magically exists in the db already
        # then call the function again until we find one that doesn't
        return random_generator()
    else:
        return random_code

#############################################################################
# ROUTES
#############################################################################

# ------------------------------------------
# Home Resource:
# Only supports the GET method, returns a homepage represented as HTML
# ------------------------------------------
@app.route('/home', methods=['GET'])
def home():
    return flask.redirect(flask.url_for('form_method_handling'))

# ------------------------------------------
# this is our input form for the shortener
# ------------------------------------------
@app.route('/crisco', methods=['GET'])   
def form_method_handling(): 
    return flask.render_template('crisco_input.html')

# ------------------------------------------
# when the crisco form is submitted, it sends a post to this route for processing
# ------------------------------------------
@app.route('/shorts', methods=['POST'])
def confirm_submission():
    form_full_url = str(request.form.get('full_url')).strip() #previously request.form['full_url']
    form_url_code = str(request.form.get('url_code')).strip() #flask does weird shit. Stringification
    new_code = 'N'

    if form_url_code == '': 
        # first find out whether a random code exists already
        if url_exists(form_full_url) == 'Y':
            # look for a random tag for that url. if one doesn't exist, generate one
            random = get_random_tag(form_full_url)
            if random == '':
                new_code = 'Y'
            else:
                # otherwise just return the existing random code for this url
                form_url_code = random
        else:
            new_code = 'Y'

        if new_code == 'Y':
            # this is a new url, so just generate a random code
            form_url_code = str(random_generator())
            # remember to set the random flag on insert
            insert_row(form_url_code, form_full_url, 'Y')
            # this is not a true confirmation - we have queried the existing random code
        return flask.render_template('confirmation.html', input_full_url=form_full_url, input_url_code=form_url_code)

    elif full_match_exists(form_full_url,form_url_code) == 'Y':
        # this is already in the db but let's let the user believe that we shortened it for them
        # first we'll update the popularity
        update_popularity(form_url_code)
        return flask.render_template('confirmation.html', input_full_url=form_full_url, input_url_code=form_url_code)
    elif tag_exists(form_url_code) == 'Y':
        # if a tag exists and we've fallen through to here, it is in the db for a diff url, so raise an error.
        # this is not a true confirmation - the user is informed that the url has already been shortened
        return flask.render_template('dogdonthunt.html', input_full_url=form_full_url, input_url_code=form_url_code)
    else:
        # this is actually a confirmation - the user is informed that the url has been shortened
        insert_row(form_url_code, form_full_url)
        return flask.render_template('confirmation.html', input_full_url=form_full_url, input_url_code=form_url_code)

# ------------------------------------------
# this is the route that handles redirects when a user enters a short code as part of the url
# ------------------------------------------
@app.route('/short/<short_code>', methods=['GET'])
def redirection(short_code=None):
    short_code = str(short_code)
    if tag_exists(short_code) == 'Y':
        # full url was found - redirect
        destination = get_url(short_code)
        return flask.redirect(destination)
    else:
        # full url not found - direct them to the sassy 404 page
        return flask.render_template('404.html')


connection.close()

if __name__ == "__main__":
    app.run(port=int(environ['FLASK_PORT']))
    


