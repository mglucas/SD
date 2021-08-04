'''
Se quiser criar um virtual environment:
python -m venv .venv
.venv/Scripts/activate

$env:FLASK_APP = "NOMEDOARQUIVOPYTHON.py"
$env:FLASK_ENV = "development"
'''


from flask import Flask

app = Flask(__name__)
print("i got here")

@app.route('/')
def index():
    return 'Hello'