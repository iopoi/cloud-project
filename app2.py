import time
import json
import ast
import random
from eliza import Eliza
from tools import connection, randomString
from flask import Flask
from flask import request
from flask import render_template
from flask import send_from_directory
from flask import session
from flask import make_response
from MySQLdb import escape_string as thwart

app = Flask(__name__, static_url_path="")
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
therapist = Eliza();

cookies = dict()
histories = dict()

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

@app.route('/adduser', methods=['POST'])
def add_user():
    request_json = request.get_json(force=True)
    username=request_json.get('username')
    password=request_json.get('password')
    email=request_json.get('email')
    if not (username and password and email):
        return json.dumps('{"status": "ERROR"}')
    print(username, password, email)
    c,conn = connection()
    x = c.execute("SELECT * FROM users WHERE username = (%s);", (thwart(username),))
    if x > 0 :
        return json.dumps('{"status": "ERROR"}')
    x = c.execute("SELECT * FROM users WHERE email = (%s)", (thwart(email),))
    if x > 0 :
        return json.dumps('{"status": "ERROR"}')
    c.execute("INSERT INTO users (username, password, email, disable) VALUES (%s, %s, %s, True)", (thwart(username), thwart(password), thwart(email)))
    conn.commit()
    c.close()
    conn.close()
    return json.dumps('{"status": "OK"}')


@app.route('/verify/', methods=['POST','GET'])
def verify():
    if request.method == 'GET':
        email = request.args.get('email')
        key = request.args.get('key')
    else:
        request_json = request.get_json(force=True)
        email = request_json.get('email')
        key = request_json.get('key')
    if not (email and key):
        return json.dumps('{"status": "ERROR"}')
    c,conn = connection()
    x = c.execute("SELECT * FROM users WHERE email = (%s) and disable = True", (thwart(email),))
    if x != 1 or key != 'abracadabra':
        return json.dumps('{"status": "ERROR"}')
    c.execute("UPDATE users SET disable = False where email = (%s)", (thwart(email),))
    conn.commit()
    c.close()
    conn.close()
    return json.dumps('{"status": "OK"}') 

@app.route('/login', methods=['POST'])
def login():
    request_json = request.get_json(force=True)
    username=request_json.get('username')
    password=request_json.get('password')
    if not (username and password):
        return json.dumps('{"status": "ERROR"}')
    c,conn = connection()
    x = c.execute("SELECT uid FROM users WHERE username = (%s) and password = (%s) and disable = False", (thwart(username), thwart(password)))
    if x != 1:
        return json.dumps('{"status": "ERROR"}')
    uid = c.fetchone()[0]
    cookie = randomString()
    cookies[cookie] = uid
    if histories.get(str(uid)) is None:
        histories[str(uid)] = dict()
        histories[str(uid)]["starttime"] = time.strftime('%Y-%m-%d %H:%M:%S')
        histories[str(uid)]["history"] = []
    resp = make_response(json.dumps('{"status": "OK"}'))
    resp.set_cookie('cookie', cookie)
    return resp

@app.route('/logout/', methods=['POST'])
def logout():
    cookie = request.cookies.get('cookie')
    if not cookie:
        return json.dumps('{"status": "ERROR"}')
    resp = make_response(json.dumps('{"status": "OK"}'))
    uid = cookies.pop(cookie)
    starttime = histories[str(uid)]["starttime"]
    history = histories[str(uid)]["history"]
    histories.pop(str(uid))
    c,conn = connection()
    c.execute("INSERT INTO histories (uid, starttime, history) VALUES (%s, %s, %s)", (thwart(uid), thwart(starttime), thwart(json.dumps({"text": history}))))
    resp.set_cookie('cookie', '', expires=0)
    return resp

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
