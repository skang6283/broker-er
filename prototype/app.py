import yaml
import os
import constant

from flask import Flask, render_template, request, redirect, url_for
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from flask_mysqldb import MySQL

from db import Database
from recommendation import predict,insert_prediction
from utils import read_json

GRAPH_FOLDER = os.path.join('/static','graphs')



app = Flask(__name__)
app.config['SECRET_KEY'] = 'my key values'

# configure your yaml
db = yaml.load(open(os.path.join(constant.CREDENTIAL_DIR, 'db.yaml')), Loader=yaml.FullLoader)
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

app.config['UPLOAD_FOLDER'] = GRAPH_FOLDER

mysql = MySQL(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User login
# TODO: Move to individual file with blueprint registration
class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(user_id):
    db = Database()
    if user_id != db.get_user_id(user_id):
        return

    user = User()
    user.id = user_id
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    user_id = request.form['user_id']
    password = request.form['password']

    db = Database()
    if (user_id == db.get_user_id(user_id)) and (password == db.get_user_password(user_id)):
        user = User()
        user.id = user_id
        login_user(user)
        return redirect(url_for('home'))

    return render_template('login.html')

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """Logout the current user."""
    user = current_user
    user.authenticated = False
    logout_user()
    return redirect(url_for('home'))

#TODO:
@app.route("/register", methods=["GET"])
def register():
    pass

@app.route('/', methods=['GET', 'POST'])
def home():
    db = Database()
    if request.method == 'POST':
        # Fetch form data
        userDetails = request.form
        username = userDetails['username']
        email = userDetails['email']
        password = userDetails['password']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO Users(username, email, password) VALUES(%s,%s, %s)",(username,email, password))
        mysql.connection.commit()
        cur.close()
        return redirect('/users')

    stockInfo = db.select_stock_with_latest_info()



    return render_template('home.html', stockInfo=stockInfo)








@app.route('/stock/<ticker>', methods=['GET'])
def stock(ticker):
    db = Database()
    stockData = db.select_stock_with_daily_price(ticker)

    info = db.get_stock_data(ticker)
    cypher = f"MATCH (n:Company)-[r:IN]->(m)<-[d:IN]-(s:Company) WHERE n.ticker = '{ticker}' RETURN *"

    cache_path = os.path.join(constant.GRAPH_DIR, f"{ticker}.json")
    if not os.path.isfile(cache_path):
        insert_prediction(db,ticker,info)
        print(f"Prediction {ticker} is done.")

    graphJSON = read_json(cache_path)

    return render_template('stock.html', ticker=ticker, stockData=stockData, cypher=cypher, graphJSON=graphJSON)






@app.route('/users')
def users():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM Users")
    if resultValue > 0:
        userDetails = cur.fetchall()
        return render_template('users.html',userDetails=userDetails)


@app.route('/watchlist', methods=['GET','POST'])
@login_required
def watchlist():
    # Get current user id with "current_user.id"


    db = Database()
    companyData = db.watchlist_default(current_user.id)
    if request.method == 'POST':

        stockDetails = request.form
        ticker = stockDetails['ticker']

        #SEARCH
        if stockDetails['button'] == 'SEARCH':
            companyData = db.watchlist_search(current_user.id,ticker)

        #INSERT
        elif stockDetails['button'] == 'INSERT':
            db.watchlist_insert(current_user.id, ticker)
            companyData = db.watchlist_default(current_user.id)

        #UPDATE
        elif stockDetails['button'] == 'UPDATE':

            db.watchlist_update(current_user.id,ticker)
            companyData = db.watchlist_default(current_user.id)

        #DELETE
        elif stockDetails['button'] == 'DELETE':

            db.watchlist_delete(current_user.id,ticker)
            companyData = db.watchlist_default(current_user.id)

    famousStocks = db.watchlist_famous_stocks()


    return render_template('watchlist.html', famousStocks = famousStocks,
                                            companyData = companyData,
                                            username = current_user.id)


if __name__ == '__main__':
    app.run(debug=True)
