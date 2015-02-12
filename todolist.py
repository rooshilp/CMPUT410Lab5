import os
import sqlite3
from flask import Flask, request, url_for, redirect, g, render_template, session, flash
import jinja2
DATABASE = 'todo.db'
USERNAME = 'admin'
PASSWORD = 'admin'
SECRET_KEY = 'super secret!'

app = Flask(__name__)
app.config.from_object(__name__)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        db = None
        
def query_db(query, args=(), one=False):
    cur = get_db().cursor()
    cur.execute(query, args)
    result = cur.fetchall()
    cur.close()
    return (result[0] if result else None) if one else result

def removetask(id):
    query_db("delete from todo where id = ?", id, one=True)
    get_db().commit()

@app.route('/')
def welcome():
    return '<h1>Welcome to the Jinja2 lab!</h1>'

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username.'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password.'        
        else:
            session['logged_in'] = True
            flash("You are logged in :-)")
            return redirect(url_for('task'))

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in')
    flash("You are now logged out.")
    return redirect(url_for('task'))

@app.route('/delete', methods=['POST'])
def delete():
    if not session.get('logged_in'):
        abort(401)
    removetask(request.form['id'][0][0])
    flash("Task was deleted successfully.")
    return redirect(url_for('task'))
    
@app.route('/task', methods = ['GET', 'POST'])
def task():
    #POST:
    if request.method == 'POST':
        if not session.get('logged_in'):
            abort(401)
        newID = query_db('select max(id) from todo')[0][0]
        try:
            newID = int(newID)
            newID += 1
        except:
            newID = 1

        query_db("insert into todo (category, priority, description, id) values (?, ?, ?, ?)", 
                 [request.form['category'], int(request.form['priority']), request.form['description'], newID])
        get_db().commit()
        return redirect(url_for('task'))        
    

    return render_template('show_entries.html', tasks=query_db('select * from todo'))  


if __name__ == '__main__':
    app.debug = True
    app.run()
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'