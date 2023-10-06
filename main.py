from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3 as sql

app = Flask (__name__)
app.secret_key = "CS499"

Sign_IN = False

@app.route('/')
def home():
    global Sign_IN
    Sign_IN = False

    return render_template("main.html")

if __name__ == "__main__":
     app.run(host="127.0.0.1", port=8080, debug=True)