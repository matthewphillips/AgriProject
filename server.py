from flask import Flask, render_template
from flaskext.mysql import MySQL
app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'AgriProject'
app.config['MYSQL_DATABASE_DB'] = 'test'
mysql.init_app(app)

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/showDatabase/")
def showDatabase():
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT * from test_table")
    data = cursor.fetchall()
    return render_template('showDatabase.html', data=data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
