import time
import json
import ast
import random
from eliza import Eliza
from tools import connection
# from .eliza import Eliza

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

@app.route('/adduser/', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        emailaddr=request.form['emailaddr']
        return render_template('adduser.html', success=False)
    return render_template('adduser.html')


@app.route('/verify/', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        return render_template('verify.html', success=False)
    return render_template('verify.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST'
        username=request.form['username']
        password=request.form['password']
        
        return render_template('login.html', success=True)
    return render_template('login.html')

@app.route('/logout/')
def logout():
    return render_template('logout.html')

@app.route('/listconv/')
def listconv():
    pass

@app.route('/getconv/')
def getconv():
    pass

if __name__ == '__main__':
    app.run()



