from flask import Flask, render_template
from helper import Helper

app = Flask(__name__)


with app.app_context():
    helper = Helper()


@app.route('/')
def home():
    return render_template('home.html', title='Home')


if __name__ == "__main__":
    app.run(debug=True)
