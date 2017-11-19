from flask import Flask, Blueprint, Response, request, json, jsonify, render_template
from nanpy import (ArduinoApi, SerialManager)
from nanpy.serialmanager import SerialManagerError
from time import sleep
import time
import os
import json as json_song

mod = Blueprint('', __name__)

l_drumstick = 4
r_drumstick = 5
l_tamborine = 6
r_tamborine = 7

connection = SerialManager()
a = ArduinoApi(connection=connection)
a.pinMode(l_drumstick, a.OUTPUT)
a.pinMode(r_drumstick, a.OUTPUT)
a.pinMode(l_tamborine, a.OUTPUT)
a.pinMode(r_tamborine, a.OUTPUT)


@mod.route('/')
def index():
    reset_pins()
    return render_template('index.html')


@mod.route('/one_beat')
def one_beat():
    instruments = {
        0: ['no instrument'],
        1: ['left drum', l_drumstick],
        2: ['right drum', r_drumstick],
        3: ['left tamborine', l_tamborine],
        4: ['right tamborine', r_tamborine]
    }
    instrument = instruments[request.args.get('a', 0, type=int)]

    a.digitalWrite(instrument[1], a.HIGH)
    sleep(.1)
    a.digitalWrite(instrument[1], a.LOW)
    sleep(.1)

    return jsonify(result=instrument[0])


@mod.route('/rhythm')
def play_rhythm():
    reset_pins()
    rhythm = {}
    name = request.args.get('name', 'verse', type=str)
    rhythm[name] = []
    rhythm[name].append({
        'strike': request.args.get('strike', 6, type=int)/60,
        'tempo': request.args.get('tempo', 120, type=int),
        'loop': request.args.get('loop', 1, type=int),
        'measure': [],
        })
    
    for i in range(8):
        beat_list = request.args.get(str(i), '0,0,0,0').split(",")
        beat_list = [int(beat) for beat in beat_list]
        rhythm[name][0]['measure'].append(beat_list)
    
    # if name:
    #     saved_name = name + '.csv'
    #     print(saved_name)
    #     with open('/home/pi/nanpyapi/arduino/songs/' + saved_name, 'w', newline='') as c:
    #         writer=csv.writer(c)
    #         for i in rhythm:
    #             writer.writerow(rhythm[i])

    #     with open('/home/pi/nanpyapi/arduino/songs/list_beats.csv', 'a', newline='') as l:
    #         writer=csv.writer(l)
    #         writer.writerow([name,saved_name])

    for i in range(rhythm[name][0]['loop']):
        try:
            play_measure(rhythm[name][0]['measure'], rhythm[name][0]['tempo'])
        except SerialManagerError:
            print("SerialManagerError: Resetting pins")
            reset_pins()

    return jsonify(result=rhythm)


@mod.route('/list_beats')
def list_beats():
    reset_pins()
    beats = []
    with open('/home/bedubs/Drumbot/drumbot/nanpyapi/arduino/songs/list_beats.csv', newline='') as c:
        beat_list = csv.reader(c)
        for row in beat_list:
            beats.append({'title': row[0], 'file': row[1]})

    templateData = {'beats': beats}
    return render_template('list.html', **templateData)


@mod.route('/play_song')
def play_song():
    reset_pins()
    filename = request.args.get('filename', 'sample_beat_1.json', type=str)
    filepath = os.path.join('/home/bedubs/Drumbot/drumbot/nanpyapi/arduino/songs/', filename)

    song = song_dict(filepath)

    # with open(filepath, newline='') as c:
    #     song = csv.reader(c)
    #     counter = 0
    #     for row in song:
    #         beats[counter] = row
    #         counter += 1

    # read_beats(beats)
    print(song)

    return jsonify(result=song)


def millis():
    return int(round(time.time() * 1000))


def play_measure(beat, tempo):
    bps = tempo/60
    beat_time = 1000/bps
    measure_time = beat_time * 4    
    length = len(beat)
    beat_stream = (x for x in beat)

    previous_ms = 0
    current_ms = millis()
    try:
        next_beat = next(beat_stream)
        previous_ms = current_ms
        while True:
            current_ms = millis()
            beat_set = []
            if (current_ms - previous_ms) >= measure_time/length:
                print(current_ms - previous_ms)
                previous_ms = current_ms
                beat_set.append("Doomp" if next_beat[0] else "")
                beat_set.append("tssss" if next_beat[1] else "")
                beat_set.append("SLAP" if next_beat[2] else "")
                print(beat_set)
                set_pins(next_beat)
                next_beat = next(beat_stream)         
    except StopIteration:
        return


def read_beats(beats):
    for i in range(len(beats)):
        a.digitalWrite(l_drumstick, int(beats[i][0]))
        a.digitalWrite(r_drumstick,int(beats[i][1]))
        a.digitalWrite(l_tamborine,int(beats[i][2]))
        a.digitalWrite(r_tamborine,int(beats[i][3]))
        sleep(.1)
        #reset_pins((60/int(beats[i][4]) - float(beats[i][3])))
        reset_pins(.1)


def set_pins(beat):
    a.digitalWrite(l_drumstick, int(beat[0]))
    a.digitalWrite(r_drumstick,int(beat[1]))
    a.digitalWrite(l_tamborine,int(beat[2]))
    a.digitalWrite(r_tamborine,int(beat[3]))
    sleep(.1)
    #reset_pins((60/int(beats[i][4]) - float(beats[i][3])))
    reset_pins(.1)


def reset_pins(delay=.2):
    a.digitalWrite(l_drumstick, 0)
    a.digitalWrite(r_drumstick, 0)
    a.digitalWrite(l_tamborine, 0)
    a.digitalWrite(r_tamborine, 0)
    sleep(delay)


def song_dict(json_file):
    with open(json_file) as song_file:
        song = json_song.load(song_file)
    return song
