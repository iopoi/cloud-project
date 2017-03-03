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
from datetime import datetime

# global vars
app = Flask(__name__, static_url_path="")
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
therapist = Eliza();
success = json.dumps({"status": "OK"})
error = json.dumps({"status": "ERROR"})
cookies = dict()
histories = dict()  # holds the histories for each userid

# helper methods
def eliza_response(user_input):
    return '{"eliza": "' +  str(therapist.respond(user_input)) + ' "}'


# flask methods
@app.route('/eliza/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/DOCTOR/', methods=['POST'])
def doctor():
    # get user message
    time1 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    json_object = request.get_data().decode("utf-8")
    dict_json_object = json.loads(json_object)
    human = dict_json_object["human"]
    # get eliza message
    time2 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    eliza = eliza_response(human)
    # use cookie to determine the user
    cookie = request.cookies.get('cookie') 
    uid = cookies.get(cookie)
    c, conn = connection()
    c.execute("select username from users where uid = (%s)", (uid,))
    username = c.fetchone()[0]
    history = histories.get(str(uid))['history']
    # append user and eliza responses into chat history
    history.append({"timestamp": time1, "name": username, "text": human})
    history.append({"timestamp": time2, "name": "eliza", "text": eliza}) 
    return eliza_response(dict_json_object["human"])


@app.route('/eliza/', methods=['GET', 'POST'])
def eliza_page():
    # main eliza page
    if request.method == 'POST':
        name=request.form['name']
        return render_template('eliza.html', name=name, date=time.strftime('%d/%m %H:%M'))
    return render_template('eliza.html')

@app.route('/adduser', methods=['POST'])
def add_user():
    # get user credentials
    request_json = request.get_json(force=True)
    username=request_json.get('username')
    password=request_json.get('password')
    email=request_json.get('email')
    if not (username and password and email):
        return error
    print(username, password, email)
    # insert into database
    c, conn = connection()
    x = c.execute("SELECT * FROM users WHERE username = (%s);", (thwart(username),))
    if x > 0 :  # checks for existing username
        return error
    x = c.execute("SELECT * FROM users WHERE email = (%s)", (thwart(email),))
    if x > 0 :  # checks for existing email
        return error
    c.execute("INSERT INTO users (username, password, email, disable) VALUES (%s, %s, %s, True)", (thwart(username), thwart(password), thwart(email)))
    conn.commit()
    c.close()
    conn.close()
    return success


@app.route('/verify', methods=['POST','GET'])
def verify():
    # get verification credentials
    if request.method == 'GET':
        email = request.args.get('email')
        key = request.args.get('key')
    else:
        request_json = request.get_json(force=True)
        email = request_json.get('email')
        key = request_json.get('key')
    if not (email and key):
        return error
    # verify user
    c, conn = connection()
    x = c.execute("SELECT * FROM users WHERE email = (%s) and disable = True", (thwart(email),))
    if x != 1 or key != 'abracadabra':  # check for existance of unverified user
        return error
    c.execute("UPDATE users SET disable = False where email = (%s)", (thwart(email),))
    conn.commit()
    c.close()
    conn.close()
    return success

@app.route('/login', methods=['POST'])
def login():
    # get login credentials
    request_json = request.get_json(force=True)
    username=request_json.get('username')
    password=request_json.get('password')
    if not (username and password):
        return error
    c, conn = connection()
    x = c.execute("SELECT uid FROM users WHERE username = (%s) and password = (%s) and disable = False", (thwart(username), thwart(password)))
    if x != 1:  # check for existance of a valid user
        return error
    uid = c.fetchone()[0]
    # make cookie for user
    cookie = randomString()
    cookies[cookie] = uid
    # if history does not exist for a user then make it
    if histories.get(str(uid)) is None:
        histories[str(uid)] = dict()
        histories[str(uid)]["starttime"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        histories[str(uid)]["history"] = []
    resp = make_response(success)
    resp.set_cookie('cookie', cookie)
    return resp

@app.route('/logout', methods=['POST'])
def logout():
    # deactivates cookie
    cookie = request.cookies.get('cookie')
    if not cookie:
        return error
    resp = make_response(success)
    uid = cookies.pop(cookie)
    # insert history into the database
    starttime = histories[str(uid)]["starttime"]
    history = histories[str(uid)]["history"]
    histories.pop(str(uid))
    value = [uid, starttime, json.dumps(history)]
    print(value)
    c, conn = connection()
    c.execute("INSERT INTO histories (uid, starttime, history) VALUES (%s, %s, %s)", value)
    conn.commit()
    c.close()
    conn.close()
    resp.set_cookie('cookie', '', expires=0)
    return resp

@app.route('/listconv', methods=['POST'])
def listconv():
    # gets cookie
    cookie = request.cookies.get('cookie')
    if not cookie:
        return error
    uid = cookies.get(cookie)
    # sends conversation
    c, conn = connection()
    x = c.execute("SELECT * FROM histories WHERE uid = (%s) order by starttime", (uid,))
    conversations = []
    for row in c:
        conversations.append(dict())
        conversations[-1]['id'] = row[0]
        conversations[-1]['start_date'] = row[2].strftime("%Y-%m-%d %H:%M:%S")
    current = histories.get(str(uid))
    if current:
        conversations.append(dict())
        conversations[-1]['id'] = 0
        conversations[-1]['start_date'] = current['starttime'] 
    print(conversations)
    return json.dumps({"status": "OK", "conversations": conversations})

@app.route('/getconv', methods=['POST'])
def getconv():
    cookie = request.cookies.get('cookie') 
    if not cookie:
        return error
    uid = cookies.get(cookie)
    request_json = request.get_json(force=True)
    id = request_json.get("id")
    c, conn =connection()
    if id == 0:
        history = histories.get(str(uid)).get('history')
    else:
        c.execute("SELECT * FROM histories WHERE hid = (%s);", (id,))
        row = c.fetchone()
        history = row[3]
    return_value = {"status": "OK", "conversation": history}
    return json.dumps(return_value)

if __name__ == '__main__':
    app.run(debug=True)
