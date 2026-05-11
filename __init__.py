from flask import Flask, request, render_template

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/play")
def play():
    return render_template("chessboard.html")

if __name__ == '__main__':
    app.run()