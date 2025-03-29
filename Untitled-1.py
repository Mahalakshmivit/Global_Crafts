# prompt: how to create a website for trading like amozon etc...

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Your frontend HTML

if __name__ == '__main__':
    app.run(debug=True)
