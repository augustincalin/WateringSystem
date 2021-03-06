from flask import Flask, flash, render_template, redirect, url_for, request, session, abort
import water_manager as mgr
import status
import os
import sys
import datetime



app = Flask(__name__)
path = sys.path[0]
app.secret_key = "a secret key"
status = status.Status()
log_filename = os.path.join(path, "log.txt")
history_filename = os.path.join(path, "history.txt")

def getModel(dateWatering='UNK', wasWet='UNK', isWetNow='UNK', statusMessage = "UNK"):
    status.load()
    viewModel = {
        'auto': "ON" if status.auto else "OFF",
        'dateWatering': status.last_watering.strftime("%x %X"),
        'wasWet': mgr.get_wet_dry(status.soil_was_wet_after),
        'isWet': mgr.get_wet_dry(mgr.checkIsWet()),
        'log': readLog(),
        'history': readHistory(),
        'events': [],
        'status': status.status,
        'title': 'WWWater @{0}'.format(datetime.datetime.now()),
        'day': (datetime.datetime.today()-datetime.timedelta(days=1)).day,
        'month':(datetime.datetime.today()-datetime.timedelta(days=1)).month,
        'year':(datetime.datetime.today()-datetime.timedelta(days=1)).year,
    }
    return viewModel


def readLog():
    result = '-'
    with open(log_filename) as f:
        line = f.readline()
        while line:
            result = '<p class='+getClass(line)+'>'+line.replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;')+'</p>' + result
            line = f.readline()
    return result

def readHistory():
    result = '-'
    with open(history_filename) as f:
        line = f.readline()
        while line:
            result = '<p>'+line+'</p>'+result
            line = f.readline()
    return result

def getClass(line):
    result = "text-dark"
    if "INFO" in line:
        result = "text-dark"
    if "WARN" in line:
        result = "text-warning"
    if "ERROR" in line:
        result = "text-danger"
    return result

def checkLogin():
    b = 'logged_in' in session
    print(b)
    if not 'logged_in' in session:
        return render_template('login.html')
    else:
        return True

@app.route("/")
def index():
    if not 'logged_in' in session:
        return redirect(url_for('login'))
    else:
        templateDate = getModel()
        return render_template('main.html', **templateDate)


@app.route("/action/clear_log")
def clearLog():
    if checkLogin():
        open('log.txt', 'w')
        return redirect(url_for('index'))

@app.route("/action/clear_history")
def clearHistory():
    if checkLogin():
        open('history.txt', 'w')
        return redirect(url_for('index'))

@app.route("/action/start")
def startAutoWatering():
    if checkLogin():
        status.auto = True
        status.save()
        return redirect(url_for('index'))

@app.route("/action/stop")
def stopAutoWatering():
    if checkLogin():
        status.auto = False
        status.save()
        return redirect(url_for('index'))

@app.route("/action/stopNow")
def stopNow():
    if checkLogin():
        mgr.autoIsOn = False
        mgr.stopWork()
        return redirect(url_for('index'))

@app.route("/action/feed")
def feed():
    if checkLogin():
        mgr.feed()
        return redirect(url_for('index'))

@app.route("/action/read")
def readSensor():
    if checkLogin():
        return redirect(url_for('index'))


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == 'DICflDmpmp_1' and request.form['username'] == 'admin':
            session['logged_in'] = True
            return redirect(url_for('index'))
    else:
        return render_template('login.html')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)