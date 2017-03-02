import time
import json
import ast
import random
from eliza import Eliza
from tools import connection

from flask import Flask
from flask import request
from flask import render_template
from flask import send_from_directory

app = Flask(__name__, static_url_path="")
therapist = Eliza();


def eliza_response(user_input):
    return '{"eliza": "' +  str(therapist.respond(user_input)) + ' "}'


@app.route('/eliza/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/eliza/DOCTOR/', methods=['POST'])
def doctor():
    json_object = request.get_data().decode("utf-8") 
    dict_json_object = json.loads(json_object)
    return eliza_response(dict_json_object["human"])


@app.route('/eliza/', methods=['GET', 'POST'])
def eliza_page():
    if request.method == 'POST':
        name=request.form['name']
        return render_template('eliza.html', name=name, date=time.strftime('%d/%m %H:%M'))
    return render_template('eliza.html')

@app.route('/adduser/', methods=['POST'])
def add_user():
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        emailaddr=request.form['emailaddr']
        # TODO - check the database for email uniqueness

        return render_template('adduser.html', success=False)
    return render_template('adduser.html')


@app.route('/verify/', methods=['POST'])
def verify():
    if request.method == 'POST':
        # TODO - check the database for the correct email and key
        # TODO - update the databse after the email has been verified
        return render_template('verify.html', success=False)
    return render_template('verify.html')

@app.route('/login/', methods=['POST'])
def login():
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        # TODO - check for username, password and real-user-verification
        #      - after login send a cookie to the user
        # TODO - if chat history does not exist create it
        return render_template('login.html', success=True)
    return render_template('login.html')

@app.route('/logout/', methods=['POST'])
def logout():
    # TODO - pop the cookie
    #      - save the chat history
    return render_template('logout.html')

@app.route('/listconv/', methods=['POST'])
def listconv():
    # TODO - return the entire chat history in a JSON format
    pass

@app.route('/getconv/', methods=['POST'])
def getconv():
    # TODO - 
    pass

if __name__ == '__main__':
    app.run()



