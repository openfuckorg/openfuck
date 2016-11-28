#Runs on Python 2.7
#On raspberry pi , install pip first from the python-dev apt package . http://raspberry.io/wiki/how-to-get-python-on-your-raspberrypi/
#Install Dependencies:
#sudo pip install python-socketio flask eventlet flask-cors flask-sslify flask-login pyserial future 

async_mode = 'eventlet'

import time, json, random, string, pickle
from flask import Flask, render_template
import socketio

sio = socketio.Server(logger=True, async_mode=async_mode)
app = Flask(__name__)
app.wsgi_app = socketio.Middleware(sio, app.wsgi_app)
app.config['SECRET_KEY'] = '3Eu7r{w4zBt>ktx?$LgXVgVs7m;*86yX,j2mz7M8>JMzi$2MC;'
file_thread = None
resetter_thread = None

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
    count = 0
    while True:
        count += 1
        sio.sleep(0.1)
        with open('/tmp/stream', 'w') as file:
            #read values and generate array a
            a = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            a[0] = int(values['on_off']) #on_off
            a[1] = 0 #v_zero #Unused
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
            #print(a)

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
    global file_thread,resetter_thread
    if file_thread is None:
        file_thread = sio.start_background_task(file_write_thread)

    if resetter_thread is None:
        resetter_thread = sio.start_background_task(button_resetter_thread)
    return render_template('index.html', **values)

@sio.on('connect', namespace='/fucking')
def test_connect(sid, environ):
    sio.emit('my response', {'data': 'Connected', 'count': 0}, room=sid, namespace='/fucking')
    sio.emit('update_radio', {'who': 'mode', 'data': values['mode']}, room=sid, namespace='/fucking') #to initialize on new connect - because radio buttons are special flowers
    print('Client connected')

@sio.on('disconnect', namespace='/fucking')
def test_disconnect(sid):
    print('Client disconnected')

@sio.on('event', namespace='/fucking')
def test_message(sid, message):
    sio.emit('event', {'data': message['data']}, room=sid,namespace='/fucking')

@sio.on('broadcast', namespace='/fucking')
def test_broadcast_message(sid, message):
    sio.emit('broadcast', {'data': message['data']}, namespace='/fucking')

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
        eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
    else:
        print('Unknown async_mode: ' + sio.async_mode)
