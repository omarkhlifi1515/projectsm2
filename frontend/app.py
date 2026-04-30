from flask import Flask, render_template, redirect, url_for
import os

app = Flask(__name__)

@app.route('/')
def index():
    api_base_url = os.environ.get("BACKEND_URL", "").strip()
    return render_template('index.html', api_base_url=api_base_url)

@app.route('/admin')
def admin():
    api_base_url = os.environ.get("BACKEND_URL", "").strip()
    return render_template('admin.html', api_base_url=api_base_url)

@app.route('/dashboard')
def dashboard():
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8501, debug=True)
