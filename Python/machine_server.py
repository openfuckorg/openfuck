#Require the following modules (and their dependencies) : python-socketio,flask,eventlet,flask_cors,Flask-SSLify,flask_login,pyserial

#Generate a file and place a secret key string for the flask app in it. Insert the path to the file in the line labeled "INSERT_SECRET_KEY"

#Generate / Acquire an SSL CERT - Insert the paths to the SSL Certificate .crt and .key files where instructed (see __main__ at the end of this file)


async_mode = 'eventlet'

import pickle
from flask import Flask, render_template, request,url_for,redirect
import socketio
import hashlib
from flask_cors import CORS, cross_origin
from flask_sslify import SSLify
import io

#Load Secret Key
f1 = io.open('INSERT_SECRET_KEY','r')
secret_key = f1.read()
f1.close()

sio = socketio.Server(logger=True, async_mode=async_mode)
app = Flask(__name__)
CORS(app)  #allow cross origin because google is fussy
sslify = SSLify(app)  #redirect everything to HTTPS because google is fussy (also its a good idea)
app.wsgi_app = socketio.Middleware(sio, app.wsgi_app)
app.config['SECRET_KEY'] = secret_key  #Apply loaded secret key
file_thread = None
resetter_thread = None

#Define initial control values
values = {
    'max_depth':135,
    'stroke_length':15,
    'min_delay':0.5,
    'max_delay':0.5,
    'max_speed':8,
    'min_speed':8,
    'speed_step':5,
    'on_off':0,
    'go_zero':0,
    'go_min':0,
    'go_max':0,
    'mode':0,
    'reset':0,
    'padding' : ''
}

def file_write_thread():
    while True:
        sio.sleep(0.1)
        with io.open('/tmp/stream', 'wb') as file:
            #read values and generate array a
            a = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            a[0] = 255 #v_zero #Unused
            a[1] = int(values['on_off']) #on_off
            a[2] = int(values['stroke_length']) #stroke_slider
            a[3] = int(values['max_depth']) #max_slider
            a[4] = float(values['min_delay']) #inner_slider
            a[5] = float(values['max_delay']) #outer_slider
            a[6] = int(values['max_speed']) #max_speed
            a[7] = int(values['go_max']) #go_max
            a[8] = int(values['go_min']) #go_min
            a[9] = int(values['go_zero']) #go_zero
            a[10] = int(values['speed_step']) #step_adjust
            a[11] = int(values['min_speed']) #min_speed
            a[12] = int(values['mode']) #mode
            a[13] = int(values['reset']) #reset
            pickle.dump(a, file)

def button_resetter_thread():
    count = 0
    while True:
        count += 1
        sio.sleep(0.75)
        values['go_zero'] = 0
        values['go_min'] = 0
        values['go_max'] = 0
        values['reset'] = 0

@app.route('/')
def index():
    return redirect(url_for('controller'))

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'

@app.route('/controller')
def controller():
    global file_thread,resetter_thread
    if file_thread is None:
        file_thread = sio.start_background_task(file_write_thread)

    if resetter_thread is None:
        resetter_thread = sio.start_background_task(button_resetter_thread)

    return render_template('controller_htmlinput.html', **values)

@sio.on('connect', namespace='/fucking')
def test_connect(sid, environ):
    sio.emit('update_radio', {'who': 'mode', 'data': values['mode']}, room=sid, namespace='/fucking') #to initialize on new connect - because radio buttons are special flowers
    print('Client connected')

@sio.on('disconnect', namespace='/fucking')
def test_disconnect(sid):
    print('Client disconnected')

@sio.on('ui_change', namespace='/fucking')
def interface_update(sid,message):
    values[message['who']] = message['data']
    values['reset'] = 1
    sio.emit('update_value', message, namespace='/fucking')
    #print(message)

@sio.on('radio_change', namespace='/fucking')#because radio buttons are special flowers
def interface_update(sid,message):
    values[message['who']] = message['data']
    values['reset'] = 1
    sio.emit('update_radio', message, namespace='/fucking')
    print(message)

@sio.on('button_click', namespace='/fucking')
def interface_update(sid,message):
    values[message['who']] = message['data']
    #print(message)

if __name__ == '__main__':
    if sio.async_mode == 'eventlet':
        #check and deploy with eventlet
        import eventlet
        import eventlet.wsgi

        eventlet.wsgi.server(eventlet.wrap_ssl(eventlet.listen(('', 5000)),
                                               certfile='INSERT_SSL_CERT',
                                               keyfile='INSERT_SSL_KEY',
                                               server_side=True), app)
    else:
        print('Unknown async_mode: ' + sio.async_mode)
