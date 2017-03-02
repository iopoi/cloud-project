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


from MySQLdb import escape_string as thwart

app = Flask(__name__, static_url_path="")
therapist = Eliza();


def eliza_response(user_input):
    return '{"eliza": "' +  str(therapist.respond(user_input)) + ' "}'


chat_history = dict()  # this dictionary will hold usernames and chat history
                       # each chat history will be a list of messages(str)

@app.route('/eliza/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/eliza/DOCTOR/', methods=['POST'])
def doctor():
    json_object = request.get_data().decode("utf-8")
    dict_json_object = json.loads(json_object)
    # user message
    u_msg = dict_json_object["human"]
#TODO chat_history[user_id].append(u_msg)
    
    # eliza message
    e_msg = eliza_response(u_msg)
#TODO chat_history[user_id].append(e_msg)
    
    return e_msg


@app.route('/eliza/', methods=['GET', 'POST'])
def eliza_page():
    if request.method == 'POST':
        name=request.form['name']
        return render_template('eliza.html', name=name, date=time.strftime('%d/%m %H:%M'))
    return render_template('eliza.html')

@app.route('/adduser/', methods=['POST'])
def add_user():
    # get user credentials
    request_json = request.get_json(force=True)
    username=request_json.get('username')
    password=request_json.get('password')
    email=request_json.get('email')
    if not (username and password and email):
        return json.dumps('{"status": "ERROR"}')
    print(username, password, email)
    # insert user into database
    c,conn = connection()
    x = c.execute("SELECT * FROM users WHERE username = (%s);", (thwart(username),))
    if x > 0 :  # checks for existing username
        return json.dumps('{"status": "ERROR"}')
    x = c.execute("SELECT * FROM users WHERE email = (%s)", (thwart(email),))
    if x > 0 :  # checks for existing email
        return json.dumps('{"status": "ERROR"}')
    c.execute("INSERT INTO users (username, password, email, disable) VALUES (%s, %s, %s, True)", (thwart(username), thwart(password), thwart(email)))
    conn.commit()
    c.close()
    conn.close()
    return json.dumps('{"status": "OK"}')


@app.route('/verify/', methods=['POST','GET'])
def verify():
    # get verification credentials
    if request.method == 'GET':
        email = request.args.get('email')
        key = request.args.get('key')
    else:
        request_json = request.get_json(force=True)
        email = request_json.get('email')
        key = request_json.get('key')
    print(email, key)
    if not (email and key):
        return json.dumps('{"status": "ERROR"}')
    # verify user
    c,conn = connection()
    x = c.execute("SELECT * FROM users WHERE email = (%s) and disable = True", (thwart(email),))
    if x != 1 or key != 'abracadabra':  # check for existence of unverified user
        return json.dumps('{"status": "ERROR"}')
    c.execute("UPDATE users SET disable = False where email = (%s)", (thwart(email),))
    conn.commit()
    c.close()
    conn.close()
    return json.dumps('{"status": "OK"}') 

@app.route('/login/', methods=['POST'])
def login():
    # get login credentials
    request_json = request.get_json(force=True)
    username=request_json.get('username')
    password=request_json.get('password')
    if not (username and password):
        return json.dumps('{"status": "ERROR"}')
    c,conn = connection()
    x = c.execute("SELECT * FROM users WHERE username = (%s) and password = (%s) and disable = False", (thwart(username), thwart(password)))
    if x != 1:  # check for existance of a valid user
        return json.dumps('{"status": "ERROR"}')
    # TODO - set cookie

    # TODO - restore old chat
    x = c.execute("SELECT history FROM chat_history WHERE userid = (%s)", (thwart(username), thwart(password)))
    
    return json.dumps('{"status": "OK"}')

@app.route('/logout/', methods=['POST'])
def logout():
    # TODO - pop the cookie

    # TODO - save the chat history
    u_hist = chat_history[user_id]
    
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
    app.run(debug=True)
