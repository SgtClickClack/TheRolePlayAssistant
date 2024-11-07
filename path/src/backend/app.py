from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='assets')

@app.route('/assets/<path:filename>')
def custom_static(filename):
    return send_from_directory(app.static_folder, filename) 