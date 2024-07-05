import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://miniprojectfacedetect-default-rtdb.firebaseio.com/"
})
ref = db.reference('Passengers') # root node/dir
# json formatted data
data = {
    "321654":{
        "name": "Murtaza",
        "flight": "NY5567",
        "class": "A",
        "departure": "NYC, 7:50 AM",
        "arrival": "LA, 2:30 PM"
    },
    "852741": {
        "name": "Emly Blunt",
        "flight": "UA1469L",
        "class": "L",
        "total_attendance": 4,
        "departure": "NYC, 7:50 AM",
        "arrival": "LA, 2:30 PM"
    },
    "963852": {
        "name": "Elon",
        "flight": "UA840",
        "class": "L",
        "departure": "NYC, 7:50 AM",
        "arrival": "LA, 2:30 PM"

    }
}
for key, value in data.items():
    ref.child(key).set(value)

