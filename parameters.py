import datetime

# path to csv file with the students (from fenix)
paths2csv = ["CP325179577_-_Alunos.csv",
             "EPro35179577_-_Alunos.csv",
            ]

# database
dbpath = "aval_db.sqlite3"

# nr of versions per shift
N = 2

# nonce for randomizing the distribution
randomizer = b"123abc"

# time delay after beginning of class to allow access
delay = datetime.timedelta(minutes=60)

# test durantion -- how long the access is allowed
test_duration = datetime.timedelta(minutes=30)

# comment shift to prevent access to their files
# map: shift -> [day (monday=2), time]
mapa_turnos = {
        "a_CP325179577PB04":  [6, datetime.time(15, 0)],
        "b_CP325179577PB04":  [6, datetime.time(15, 0)],
        "a1_CP325179577PB04": [3, datetime.time(14, 0)],
        "b1_CP325179577PB04": [3, datetime.time(14, 0)],
        "a1_CP325179577PB05": [3, datetime.time(16, 30)],
        "b1_CP325179577PB05": [3, datetime.time(16, 30)],
        "a_CP325179577PB07":  [4, datetime.time(13, 0)],
        "b_CP325179577PB07":  [4, datetime.time(13, 0)],
        "a_CP325179577PB08":  [4, datetime.time(17, 0)],
        "b_CP325179577PB08":  [4, datetime.time(17, 0)],
        "a_CP325179577PB09":  [5, datetime.time(16, 30)],
        "b_CP325179577PB09":  [5, datetime.time(16, 30)],
        "a_CP325179577PB10":  [6, datetime.time(16, 30)],
        "b_CP325179577PB10":  [6, datetime.time(16, 30)],
        "a1_EPro35179577PB02": [3, datetime.time(10, 30)],
        "b1_EPro35179577PB02": [3, datetime.time(10, 30)],
        "a1_EPro35179577PB03": [3, datetime.time(13, 0)],
        "b1_EPro35179577PB03": [3, datetime.time(13, 0)],
        "a_EPro35179577PB04":  [5, datetime.time(11, 0)],
        "b_EPro35179577PB04":  [5, datetime.time(11, 0)],
        "EPro35179577PB02": [2, datetime.time(15, 0)],
        "EPro35179577PB03": [2, datetime.time(15, 0)],
        }
