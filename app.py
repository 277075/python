from flask import Flask, send_from_directory, render_template, request, session, jsonify, flash, redirect, logging
from flask_pymongo import PyMongo
import pymongo
import bcrypt
from flask_cors import CORS, cross_origin
from flask import make_response, url_for, abort
import json
import random
from pymongo import MongoClient
from time import gmtime, strftime
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from werkzeug import secure_filename
import os


UPLOAD_FOLDER = './static/photo_uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
URI = 'mongodb://127.0.0.1:27017'
client = pymongo.MongoClient(URI)
DB = client['CCCv3']
photos = DB.photos
users = DB.users
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config.from_object(__name__)
app.secret_key = '<some secret key>'
CORS(app)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/loginview')
def loginview():
    return render_template('login.html')

@app.route('/registerview')
def registerview():
    return render_template('register.html')

@app.route('/uploadphotoview', methods=['GET'])
def uploadphotoview():
    return render_template('uploadphotos.html')

@app.route('/searchphotoview')
def searchphotoview():
    return render_template('searchphotos.html')

@app.route('/login', methods=['POST'])
def login():
    users = DB.users
    login_user = users.find_one({'username' : request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['username'] = request.form['username']
            return redirect(url_for('index'))

    return 'Invalid username/password combination'

@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm(request.form)
    users = DB.users
    # existing_user = users.find_one({'username' : request.form['username']})
    if request.method == 'POST' and form.validate():
        existing_user = users.find_one({'username' : request.form['username']})
        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'username' : request.form['username'], 'email' : request.form['email'], 'password' : hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('index'))

        return 'Username already exists'

    return render_template('register.html', form=form)

@app.route('/uploadview')
def uploadview():
    return render_template('uploadphotos.html')

@app.route('/viewallimages')
def viewall():
    image_names = DB.photos.find()
    return render_template('allimages.html', image_names=image_names)

@app.route('/useruploads')
def useruploads():
    user_uploads = DB.photos.find({"postedby" : session['username']})
    return render_template('useruploads.html', user_uploads=user_uploads)

@app.route('/photosearch', methods=['POST'])
def photosearch():
    DB.photos.create_index([('description', 'text'), ('postedby', 'text'), ('tag1' , 'text'), ('tag2' , 'text'), ('tag3' , 'text')])

    search_results = DB.photos.find({"$text": {"$search": request.form['searchbar']}})
    if search_results is None:
        return 'Your search did not return any results'
    return render_template('searchedphotos.html', search_results=search_results)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/create', methods=['GET', 'POST'])
def upload_file():
    photos=DB.photos
    if request.method == 'POST':
        file = request.files['uploaded_image']
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            photos.insert({'postedtime': strftime("%Y-%m-%dT%H:%M:%SZ", gmtime()), 'url': (url_for('uploaded_file', filename=filename)), 'postedby' : session['username'], 'description' : request.form['description'], 'tag1' : request.form['tag1'], 'tag2' : request.form['tag2'], 'tag3' : request.form['tag3'] })
            return redirect(url_for('viewuploadedimage', filename=filename))
    return render_template('uploadview', filename=filename)


@app.route('/uploadedimage/<filename>')
def viewuploadedimage(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/uploads/<filename>')
def send(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/clear')
def clearsession():
    # Clear the session
    session.clear()
    # Redirect the user to the main page
    return redirect(url_for('loginview'))

class RegisterForm(Form):
    username = StringField('Username', [validators.Length(min=1, max=30)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.DataRequired(), validators.EqualTo('confirm', message='Passwords do not match')])
    confirm = PasswordField('Confirm Password')

class UploadForm(Form):
    description = StringField('Description', [validators.Length(min=5, max=50)])
    tag1 = StringField('Tag 1', [validators.Length(min=2, max=50)])
    tag2 = StringField('Tag 2')
    tag3 = StringField('Tag 3')

if __name__=='__main__':
	app.run(debug=True)
