from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/dashboard')
def dashboard():
    return render_template('newtemp.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8501, debug=True)
