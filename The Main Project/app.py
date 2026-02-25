from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:\\\The Main Project\\the_til.db'
#* This tells Flask to create a file named 'the_til.db' in your project folder
db = SQLAlchemy(app)

class TILPost(db.Model):
    # Every post needs a unique ID (1, 2, 3...)
    id = db.Column(db.Integer, primary_key=True)
    
    # The actual thing you learned (limit 200 characters)
    content = db.Column(db.String(200), nullable=False)
    
    # Optional: A simple way to show the post in your terminal
    def __repr__(self):
        return f'<Post {self.id}>'

@app.route("/")
def hello_world():
    return "<h1>Hello, World!!!</h1>"



if __name__ == "__main__":
    app.run(debug=True)
