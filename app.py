from flask import Flask,render_template, request, url_for,session, redirect
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session,sessionmaker
from flask_mysqldb import MySQL
import os
# import validators

app = Flask(__name__)
app.secret_key = "super secret key"
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='url_shortner'

mysql=MySQL(app)

@app.route("/register",methods=["POST","GET"])
def register():
    if request.method=="POST":
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        if username is "" or email is "" or password is "":
            error_msg="Please Enter Complete Details"
            return render_template('register.html',msg=error_msg)
        curr=mysql.connection.cursor()
        curr.execute("select * from users where email= '"+email+"'")
        data=curr.fetchone()
        curr.close()
        if data is None:
            curr=mysql.connection.cursor()
            curr.execute("INSERT INTO `users` (`Username`, `Email`, `Password`) VALUES('"+username+"','"+email+"','"+password+"')")
            mysql.connection.commit()
            curr.close()
            session["email"]=email
            return redirect(url_for("home"))
        else:
            msg="Email already exists."
            return render_template('register.html',msg=msg)
    return render_template('register.html')

@app.route("/Logout")
def logout():
    session.pop('email')
    return redirect(url_for("login"))


@app.route("/",methods=["POST","GET"])
def login():
    if "email" in session:
        return redirect(url_for("home"))
    if request.method=="POST":
        email=request.form.get('email')
        password=request.form.get('password')
        curr=mysql.connection.cursor()
        curr.execute("select * from users where email= '"+email+"'")
        data=curr.fetchone()
        curr.close()
        if data is not None:
            session["email"]=data[2]
            return redirect(url_for("home"))
        else:
            msg="Invalid Credentials"
            return render_template('login.html',msg=msg)
    return render_template('login.html')

@app.route("/home",methods=["POST","GET"])
def home():
    if "email" in session:
        curr=mysql.connection.cursor()
        curr.execute("select * from users where Email= '"+str(session["email"])+"'")
        data=curr.fetchone()
        username=data[1]
        curr.close()
        curr=mysql.connection.cursor()
        curr.execute("select * from url_tracker where email= '"+str(session["email"])+"'")
        allrows=curr.fetchall()
        curr.close()
        if request.method=="POST":
            url=request.form.get("url")
            # if validators.url(url) is False:
            #     error_msg="Please enter a valid url."
            #     return render_template('home.html',data=username,error_msg=error_msg)
            short_name=request.form.get("short_name")
            curr=mysql.connection.cursor()
            curr.execute("select * from url_tracker where Short_name= '"+short_name+"'")
            data=curr.fetchone()
            curr.close()
            if data is None:
                curr=mysql.connection.cursor()
                curr.execute("INSERT INTO `url_tracker` (`Email`, `Short_name`, `Primary_Url`) VALUES('"+session["email"]+"','"+short_name+"','"+url+"')")
                mysql.connection.commit()
                curr.close()
                msg="Link Created Successfully at http://127.0.0.1:5000/"+short_name+". This will be valid for 48 hours."
                curr=mysql.connection.cursor()
                curr.execute("select * from url_tracker where email= '"+str(session["email"])+"'")
                allrows=curr.fetchall()
                curr.close()
                return render_template('home.html',data=username,allrows=allrows,msg=msg)
            error_msg="Short name not available. Try another one."
            return render_template('home.html',data=username,allrows=allrows,error_msg=error_msg)    
        return render_template('home.html',data=username,allrows=allrows) 

    return redirect(url_for("login"))    

@app.route("/<path:path_name>")
def redirect_url(path_name):
    if "email" in session:
        curr=mysql.connection.cursor()
        curr.execute("select * from url_tracker where Short_name= '"+path_name+"' and Email='"+session["email"]+"' ")
        data=curr.fetchone()
        curr.close()
        if data is None:
            return "<h2>Invalid URL</h2>"
        else:
            return redirect(data[3])
    return redirect(url_for("login"))    

if __name__=="__main__":
    app.run(debug=True)    