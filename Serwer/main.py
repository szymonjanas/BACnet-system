from flask import Flask, jsonify 


app = Flask(__name__)

timetableFile = open('timetable.json', 'r')
timetable = timetableFile.read()
timetableFile.close()

@app.route('/')
def mainRoute():
    return "Hello World!"

@app.route('/api/get/timetable')
def getTimetable():
    return timetable

if __name__ == "__main__":
    app.run(debug=True)
