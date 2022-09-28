#!flask/bin/python
import datetime
import json
import os

import pronotepy
from flask import Flask, abort, render_template
from pronotepy import ent

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('home.html', child=child)


@app.route('/lessons')
def lessons():
    if client.logged_in:
        start = datetime.date.today()
        end = start + datetime.timedelta(days=config['lessons']['days'])
        return __serialize(client.lessons(start, end))
    else:
        abort(500)


@app.route('/discussions')
def discussions():
    if client.logged_in:
        return __serialize(client.discussions())
    else:
        abort(500)


@app.route('/homework')
def homework():
    if client.logged_in:
        start = datetime.date.today()
        end = start + datetime.timedelta(days=config['homework']['days'])
        return __serialize(client.homework(start, end))
    else:
        abort(500)


@app.route('/absences')
def absences():
    if client.logged_in:
        return __serialize(client.current_period.absences)
    else:
        abort(500)


@app.route('/overall_average')
def overall_average():
    if client.logged_in:
        return __serialize(client.current_period.overall_average)
    else:
        abort(500)


@app.route('/punishments')
def punishments():
    if client.logged_in:
        print (client.current_period.punishments)
        return __serialize(client.current_period.punishments)
    else:
        abort(500)


@app.route('/grades')
def grades():
    if client.logged_in:
        return __serialize(client.current_period.grades)
    else:
        abort(500)


@app.route('/averages')
def averages():
    if client.logged_in:
        return __serialize(client.current_period.averages)
    else:
        abort(500)


@app.route('/evaluations')
def evaluations():
    if client.logged_in:
        return __serialize(client.current_period.evaluations)
    else:
        abort(500)


@app.route('/period')
def period():
    if client.logged_in:
        out = __serialize(client.current_period)
        out['overall_average'] = overall_average()
        return out
    else:
        abort(500)


def __serialize(data):
    if hasattr(data, '__slots__'):
        out = {}
        for attr in data.__slots__:
            if hasattr(data, attr):
                if attr != '_client' and attr != '_content' and attr != '_files':
                    out[attr] = __serialize(getattr(data, attr))
        return out
    else:
        if isinstance(data, str):
            return data
        else:
            try:
                out = []
                for item in iter(data):
                    out.append(__serialize(item))
                return out
            except TypeError as te:
                if isinstance(data, datetime.datetime) or isinstance(data, datetime.date):
                    return data.isoformat()
                elif isinstance(data, datetime.timedelta):
                    return data.total_seconds()
                else:
                    return data


if __name__ == '__main__':
    defaultConfig = {
        'lessons': {'days': 7},
        'homework': {'days': 7},
        'parent': True
    }
    with open('config/config.json') as f:
        config = json.load(f)

    config = defaultConfig | config
    _ent = ''
    if 'cas' in config:
        cas = config['cas']
        if cas is not None:
            _ent = getattr(ent, cas)
    mode = 'eleve'
    if 'parent' in config:
        if config['parent']:
            mode = 'parent'

    url = 'https://' + config['prefix'] + '.index-education.net/pronote/' + mode + '.html'

    if mode == 'parent':
        client = pronotepy.ParentClient(url,
                                        username=config['username'],
                                        password=config['password'],
                                        ent=_ent)
        if 'child' in config and config['child'] != '':
            client.set_child(config['child'])
            child = config['child']
        else:
            child = client.children[0].name
    else:
        client = pronotepy.Client(url,
                                  username=config['username'],
                                  password=config['password'],
                                  ent=_ent)

    debug = os.getenv('DEBUG') == 'true'
    port = os.getenv('PORT')
    app.run(host='0.0.0.0', port=port, debug=debug)
