from flask import Flask, render_template, url_for, request, session, redirect
from flask_pymongo import PyMongo
from pymongo import MongoClient


app = Flask(__name__)
app.secret_key = 'mysecret'
app.config['MONGO_DBNAME'] = 'mongologin'
app.config['MONGO_URI'] = 'mongodb+srv://vardhan688:12345@cluster0-ais0n.mongodb.net/test?retryWrites=true&w=majority'
#client = MongoClient("mongodb+srv://vardhan688:Wantmylife11@cluster0-ais0n.mongodb.net/test?retryWrites=true&w=majority")
#db = client["mongologin"]
mongo = PyMongo(app)
allCurrentUsers=[]

@app.route('/')
def index():
    if 'username' in session:
        return 'You are logged in as ' + session['username']

    return render_template('index.html')

@app.route('/companyDetail/<username>')
def companyDetail(username):
    print(url_for('companyDetail', username= username))
    companies = mongo.db.companies
    users = mongo.db.users
    session['username'] = username
    login_user = users.find_one({'name' : username})
    company = companies.find_one({'companyName' : login_user['companyName']})
    if company is None:
        return 'Company does not exits'
    
    if session['username'] not in allCurrentUsers:
        allCurrentUsers.append(session['username'])
    for user in allCurrentUsers:
        temp_user = users.find_one({'name' : user})
        if temp_user['companyName'] == company['companyName']:
            company['activeUsers'] = company['activeUsers'] + 1
    
    company['totalViews'] = company['totalViews'] + 1
    companies.update_one({"_id": company['_id']},{"$set":{"totalViews": company['totalViews']}})
    return render_template('companyDetail.html', company = company)

@app.route('/file/<filename>')
def file(filename):
    return mongo.send_file(filename)

@app.route('/userdetail/<username>')
def userDetail(username):
    users = mongo.db.users
    login_user = users.find_one({'name' : username})
    return render_template('user.html', login_user = login_user)

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name' : request.form['username']})
    if login_user:
        if request.form['pass'] == login_user['password']:
            login_user['username'] = request.form['username']
            return render_template('user.html', login_user = login_user)

    return 'Invalid username/password combination'

@app.route('/register_user', methods=['POST', 'GET'])
def register_user():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})
        print(existing_user)
        if existing_user is None:
            profile_img = request.files['profile_img']
            mongo.save_file(profile_img.filename, profile_img)
            users.insert({'name' : request.form['username'], 'password' : request.form['pass'], 'jobRole': request.form['role'], 'companyName': request.form['cname'], 'profileimgName': profile_img.filename})
            return render_template('index.html')
        
        return 'That username already exists!'

    return render_template('register_user.html')

@app.route('/register_company', methods=['POST', 'GET'])
def register_company():
    if request.method == 'POST':
        companies = mongo.db.companies
        existing_company = companies.find_one({'companyName' : request.form['companyName']})
        print(existing_company)
        if existing_company is None:
            logo_img = request.files['logoimg']
            mongo.save_file(logo_img.filename, logo_img)
            companies.insert({'companyName' : request.form['companyName'], 'address' : request.form['address'], 'activeUsers': 0, 'totalViews': 0, 'logoImgName': logo_img.filename})
            return render_template('index.html')
        
        return 'Company already exists!'

    return render_template('register_company.html')

if __name__ == '__main__':
    app.run(debug=True)
