from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!!!</p>"
def testing_outputs():
    return "<h1>This is a test output for the function.</h1>"

if __name__ == "__main__":
    app.run(debug=True)
