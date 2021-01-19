import os
import datetime
import logging
import hashlib
from flask import Flask, render_template, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy

from parameters import mapa_turnos, dbpath, delay, test_duration, N, randomizer

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"+dbpath
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
logging.basicConfig(filename="log_formaval.log", level=logging.DEBUG)
db = SQLAlchemy(app)

# database tables
class students(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    istid = db.Column(db.String(10))
    course = db.Column(db.String(20))
    version = db.Column(db.String(30))
    shift = db.Column(db.String(20))
    timelogged1st = db.Column(db.DateTime)
    iplogged1st = db.Column(db.String(15))

class logs(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    req = db.Column(db.String(100))
    status = db.Column(db.String(100))
    ip = db.Column(db.String(15))
    repeatedQ = db.Column(db.Boolean)

    def __init__(self, time, req, status, ip, repeatedQ):
        self.time = time
        self.req = req
        self.status = status
        self.ip = ip
        self.repeatedQ = repeatedQ

def time_add(time, delta):
    return (datetime.datetime.combine(datetime.date(1,1,1),time) + delta).time()

def timewindowQ(shift):
    # check if shift is disabled
    if shift not in mapa_turnos.keys():
        return False
    # parse shift's turn
    shiftdow = mapa_turnos[shift][0]
    shifttime = mapa_turnos[shift][1]
    # compute current info
    datenow = datetime.datetime.now()
    dayofweek = datenow.isoweekday()+1
    timenow = datenow.time()
    # check if allowed
    if (dayofweek == shiftdow) and \
            (time_add(shifttime, delay) < timenow < time_add(shifttime, delay+test_duration)):
        return True
    return False

def getcurrshift(course): # required when student does not have a shift...
    datenow = datetime.datetime.now()
    dayofweek = datenow.isoweekday()+1
    timenow = datenow.time()
    for shift in mapa_turnos:
        shiftdow = mapa_turnos[shift][0]
        shifttime = mapa_turnos[shift][1]
        # skip shifts for different courses:
        if course not in shift:
            continue
        # check what shift for current date and time (it will be shift a_ instead of b_):
        if (shiftdow == dayofweek) and \
                (time_add(shifttime,delay) < timenow < time_add(shifttime,delay+test_duration)):
            return shift
    return None

def hash(s: bytes, m: int):
    '''hashes bytestring s to int from 1...m'''
    return 1 + (int(hashlib.md5(s + randomizer).hexdigest(), 16) % m)

def log(time, req, status, ip, repeatedQ):
    newlog = logs(time, req, status, ip, repeatedQ)
    db.session.add(newlog)
    db.session.commit()

@app.route("/", methods=["GET", "POST"])
def logon():
    # accessing the home (logon) page (GET)
    if request.method == "GET":
        return render_template("logon.html")

    # submitting ist id, requesting version (POST)
    elif request.method == "POST":
        temp_shift = None
        #curr_ip = request.remote_addr
        curr_ip = request.headers.getlist("X-Forwarded-For")[0] if \
                request.headers.getlist("X-Forwarded-For") else \
                request.remote_addr
        curr_time = datetime.datetime.now().replace(microsecond=0)
        input_istid = request.form["istid"]
        app.logger.debug(f"[POSTPOST] {curr_ip}, {request.form}")

        # check if IP has made a request before
        repeatedipQ = (logs.query.filter_by(ip=curr_ip).first() != None)

        # check if istid is valid
        if not (8 <= len(input_istid) <= 10) or \
                not input_istid.startswith("ist") or \
                not input_istid[3:].isdigit():
            log(curr_time, input_istid, "BAD - ISTID", curr_ip, repeatedipQ)
            return "Isto não é um IST ID >=|", 400

        # get info on current student from the database (if exists)
        curr_student = students.query.filter_by(istid=input_istid).first()
        if not curr_student:
            log(curr_time, input_istid, "BAD - signup", curr_ip, repeatedipQ)
            return "O IST ID não está inscrito à disciplina de CP ou EP", 400

        # check if this is the students shift. if it has no shift, it is accepted (if a valid shift is enabled)
        if not curr_student.shift: # student has no shift -- get current shift
            temp_shift = getcurrshift(curr_student.course)
            if not temp_shift:
                log(curr_time, input_istid, "BAD - shift", curr_ip, repeatedipQ)
                return "O IST ID não está inscrito no turno actual", 400
        elif not timewindowQ(curr_student.shift):
            log(curr_time, input_istid, "BAD - shift", curr_ip, repeatedipQ)
            return "O IST ID não está inscrito no turno actual", 400

        # give version
        version = hash(input_istid.encode(), N)
        if not curr_student.timelogged1st: # no request has been made for this istid yet
            if temp_shift: # this student is not signed up for any shift...
                log(curr_time, input_istid, f"OK (not signed up) - {temp_shift} V {str(version)}", curr_ip, repeatedipQ)
                curr_student.version = temp_shift + " - V. " + str(version)
            else:
                log(curr_time, input_istid, f"OK - {curr_student.shift} V {str(version)}", curr_ip, repeatedipQ)
                curr_student.version = curr_student.shift + " - V. " + str(version)
            curr_student.timelogged1st = curr_time
            curr_student.iplogged1st = curr_ip
            db.session.commit()
        elif curr_student.iplogged1st == curr_ip: # repeated istid from same ip
            log(curr_time, input_istid, f"OK - {temp_shift if temp_shift else curr_student.shift} V {str(version)} (same IP)", curr_ip, repeatedipQ)
        else: # another ip is requesting istid that was already asked before
            log(curr_time, input_istid, f"CHECK - repeated istid ({temp_shift if temp_shift else curr_student.shift} V {str(version)})", curr_ip, repeatedipQ)

        # check if that version exist and log HORRIBLE otherwise. if OK send the pdf
        testpath = f"./testes/{temp_shift if temp_shift else curr_student.shift}/"
        if not os.path.isfile(testpath + f"{version}.pdf"):
            log(curr_time, input_istid, f"HORRIBLE - version from query below does not exist!", curr_ip, repeatedipQ)
            return "ERRO - por favor contactar o docente", 400
        return send_from_directory(directory=testpath, filename=f"{version}.pdf", mimetype='application/pdf')

    else:
        return "FAILED REQUEST", 400

@app.route("/viewdb")
def viewdb():
    return render_template("viewdb.html", students=students.query.all(), logs=logs.query.all(), mapa=mapa_turnos)

if __name__ == "__main__":
    assert os.path.isfile(dbpath), "database does not exist"
    app.run(host="0.0.0.0")
