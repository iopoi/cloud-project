import time
import json
import ast
import random

def eliza_response(user_input):
    return '{"eliza": "My favorite number is ' + str(random.randint(-1, 20)) + ' "}'
#    return '{"eliza": "hello world"}'

from flask import Flask
from flask import request
from flask import render_template
from flask import send_from_directory

app = Flask(__name__, static_url_path="")

@app.route('/eliza/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/eliza/DOCTOR/', methods=['POST'])
def doctor():
    json_object = request.get_data().decode("utf-8") 
#    print(json_object)
    dict_json_object = json.loads(json_object)
    return eliza_response(dict_json_object["human"])

@app.route('/eliza/', methods=['GET', 'POST'])
def eliza_page():
    if request.method == 'POST':
        name=request.form['name']
        return render_template('eliza.html', name=name, date=time.strftime('%d/%m %H:%M'))
    return render_template('eliza.html')


if __name__ == '__main__':
    app.run()



