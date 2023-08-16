
import numpy as np
import pandas as pd
from flask import Flask, request, render_template,session
import pickle
from flask_mysqldb import MySQL
import MySQLdb.cursors
import matplotlib.pyplot as plt
import matplotlib.axes._axes as axes

import threading



def predict_churn(tenure,logindevice,  citytier,warehouse, gender, numdevice, score, maritalstatus,numaddress,complain,lastorder, cashback, avg, paymentmode, ordercat ):    
  

    prediction = {
        'Tenure': tenure,
        'PreferredLoginDevice': logindevice,
        'CityTier': citytier,
        'WarehouseToHome': warehouse,
        'Gender': gender,
        'NumberOfDeviceRegistered': numdevice,
        'SatisfactionScore': score,
        'MaritalStatus': maritalstatus,
        'NumberOfAddress': numaddress,
        'Complain': complain,
        'DaySinceLastOrder': lastorder,
        'CashbackAmount': cashback,
        'avg_cashbk_per_order': avg,
        'PreferredPaymentMode_CC': 1 if paymentmode == 'CC' else 0,
        'PreferredPaymentMode_COD': 1 if paymentmode == 'COD' else 0,
        
        
        'PreferredPaymentMode_DC': 1 if paymentmode == 'DC' else 0,
        'PreferredPaymentMode_E wallet': 1 if paymentmode == 'E wallet' else 0,
        'PreferredPaymentMode_UPI': 1 if paymentmode == 'UPI' else 0,
        'PreferedOrderCat_Fashion': 1 if ordercat == 'Fashion' else 0,
        'PreferedOrderCat_Grocery': 1 if ordercat == 'Grocery' else 0,
        'PreferedOrderCat_Laptop': 1 if ordercat == 'Laptop' else 0,
        'PreferedOrderCat_Mobile': 1 if ordercat == 'Mobile' else 0,
        'PreferedOrderCat_Others': 1 if ordercat == 'Others' else 0,
    }
    print(prediction)
    df = pd.DataFrame(prediction,index=[0])
    print(df)
    
    

    pred=model.predict(df)
    
    
    return pred
    
 # making prediction

app = Flask(__name__)
app.secret_key = 'asdsdfsdfs13sdf_df%&'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ecommerce'
mysql = MySQL(app)

model = pickle.load(open('rfmodel.pkl', 'rb'))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/predict',methods=['POST'])
def predict():
    '''
    For rendering results on HTML GUI
    '''
    if request.method == 'POST':
        tenure = int(request.form['tenure'])
        warehouse = int(request.form['warehousetohome'])
        numdevice = int(request.form['numdevices'])
        numaddress = int(request.form['numaddress'])
        lastorder = int(request.form['lastorder'])
        cashback = int(request.form['cashbackamount'])
        ordercount=int(request.form['ordercount'])
        logindevice = request.form['logindevice']
        citytier = int(request.form['citytier'])
        paymentmode = request.form['paymentmode']
        ordercat = request.form['ordercat']
        score = int(request.form['satisfactionscore'])
        maritalstatus =request.form['maritalstatus']
        gender = request.form['gender']
        complain = int(request.form['complain'])
        avg=cashback/ordercount
        

    
       
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    prediction = predict_churn(tenure,logindevice,  citytier,warehouse, gender, numdevice, score, maritalstatus,numaddress,complain,lastorder, cashback, avg, paymentmode, ordercat)    
    if(prediction==1):
          pred='Will Churn'
    else:
          pred='Will Not Churn'
    cursor.execute('INSERT INTO prediction VALUES (NULL, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s,%s,%s,%s,%s)', (tenure,logindevice,citytier,warehouse,gender,numdevice,score,maritalstatus,numaddress,complain,lastorder,cashback,avg,paymentmode,ordercat,pred))
    mysql.connection.commit()
    return render_template('churnpred.html', prediction=prediction,display="none",display_a="block")
@app.route('/login',methods=['POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
                
                username= request.form['username']
                password= request.form['password']
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM admin WHERE username = % s AND password = % s', (username, password, ))
                account = cursor.fetchone()
                
                
 



                
                query = """SELECT * FROM prediction"""
                cursor.execute(query)
                rows = cursor.fetchall()
                if rows==[]:
                      no=0
                      churn=0
                      not_churn=0
                else:
                      df = pd.DataFrame(rows)
                      churn_percentage = df['Churn'].value_counts()['Will Churn'] / df['Churn'].value_counts().sum() * 100
                      churn=df['Churn'].value_counts()['Will Churn']
                      not_churn=df['Churn'].value_counts()['Will Not Churn']
                      no=df.Id.nunique()
                
                # Create a thread to create the Matplotlib GUI
                      def create_plot():
                            churn_pie = df['Churn'].value_counts().plot.pie(labels=['Will Not Churn','Will Churn'], figsize=(5,5), autopct=lambda p: '{:.1f}%'.format(p))
                            churn_pie.plot()
                            plt.savefig('./static/images/churn_pie.png')
                thread = threading.Thread(target=create_plot)
                thread.start()
                
               
               
                

                if account:
                      session['loggedin'] = True
                      #session['id'] = account['id']
                      session['username'] = account['username']
                      msg = 'Logged in successfully !'

                      return render_template('dashboard.html', msg = msg,no=no,churn=churn,not_churn=not_churn,churn_pie='./static/images/churn_pie.png',churn_percentage=churn_percentage)
                else:
                     msg = 'Incorrect username / password !'
                     return render_template('login.html', msg = msg)
@app.route('/signup',methods=['POST'])
def  signup():
    
    if request.method == 'POST' and 'username' in request.form and   'email' in request.form and 'password' in request.form:
                
                username= request.form['username']
                password= request.form['password']
                email=request.form['email']
                 
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('INSERT INTO admin VALUES ( % s, % s, % s)', (username,email,password))
                mysql.connection.commit()
                return render_template('login.html')
@app.route("/logout")
@app.route("/logout")
def logout():
	session['loggedin']=False
	return render_template("home.html")  
@app.route("/view")
def view():
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM prediction')
        data = cursor.fetchall()
        print(data)
        mysql.connection.commit()
        
        return render_template("view.html",data=data) 
@app.route("/loginpage")
def loginpage():
	#session['loggedin,methods=['POST']False
	return render_template("login.html")   
@app.route("/churnpred")
def churnpred():
	#session['loggedin,methods=['POST']False
	return render_template("churnpred.html")  
@app.route('/dashboard')
def dashboard():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    query = """SELECT * FROM prediction"""
    cursor.execute(query)
    rows = cursor.fetchall()
    df = pd.DataFrame(rows)
    churn_percentage = df['Churn'].value_counts()['Will Churn'] / df['Churn'].value_counts().sum() * 100
    churn=df['Churn'].value_counts()['Will Churn']
    not_churn=df['Churn'].value_counts()['Will Not Churn']
    no=df.Id.nunique()
    
    # Create a thread to create the Matplotlib GUI
    def create_plot():
            
            churn_pie = df['Churn'].value_counts().plot.pie(labels=['Will Not Churn','Will Churn'], figsize=(5,5), autopct=lambda p: '{:.1f}%'.format(p))
            churn_pie.plot()
            plt.savefig('./static/images/churn_pie.png')

    thread = threading.Thread(target=create_plot)
    thread.start()
    # Create the pie chart in the main thread
    # churn_pie = df['Churn'].value_counts().plot.pie(labels=['Will Not Churn','Will Churn'], figsize=(5,5))
    # churn_pie.plot()
    # plt.savefig('./static/images/churn_pie.png')
    
    return render_template('dashboard.html',no=no,churn=churn,not_churn=not_churn,churn_pie='./static/images/churn_pie.png',churn_percentage=churn_percentage)
@app.route("/search",methods=['POST'])
def search():
        if request.method == 'POST' and 'custid' in request.form:
              cust_id= request.form['custid']
              cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
              cursor.execute('SELECT * FROM prediction where Id={}'.format(cust_id))
              data = cursor.fetchall()
              print(data)
              mysql.connection.commit()
              return render_template("custpred.html",data=data) 
@app.route("/view1")
def view1():
	
	return render_template("customerno.html")   
if __name__ == "__main__":
    app.run(debug=True)