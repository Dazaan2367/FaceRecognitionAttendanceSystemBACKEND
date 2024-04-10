from flask import Flask, jsonify,render_template, request, session,redirect, Response
import requests
import os
from camera import VideoCamera

app = Flask(__name__)
app.secret_key  = 'secret'

@app.route("/")
def home():
    return render_template("index.html")

def gen(cam):
    while True:
        frame = cam.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n'+frame
               + b'\r\n\r\n')

@app.route("/video")
def video():
    return Response(gen(VideoCamera),
    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)