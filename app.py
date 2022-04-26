from http import client
from flask import Flask, redirect, url_for, request, render_template, session, flash
import datetime
import pymongo
from twilio.rest import Client
from decouple import config






# FlASK
#############################################################
app = Flask(__name__)
app.permanent_session_lifetime = datetime.timedelta(days=365)
app.secret_key = "super secret key"
#############################################################

# MONGODB
#############################################################
mongodb_key = config('mongodb_key')
client = pymongo.MongoClient(
    mongodb_key, tls=True, tlsAllowInvalidCertificates=True)
db = client.Pagina
cuentas = db.Cliente
#############################################################

# Twilio
#############################################################
account_sid = config('account_sid')
auth_token = config('auth_token')
TwilioClient = Client(account_sid, auth_token)
#############################################################

#cursor = cuentas.find()
#for doc in cursor:
#    print(doc)



@app.route('/')
def home():
    email = None
    if "email" in session:
        email = session["email"]
        return render_template('index.html', data=email)
    else:
        return render_template('login.html', data=email)


@app.route('/signup', methods=["GET", "POST"])
def signup():
    email = ""
    if 'email' in session:
        return render_template('index.html', data=email)
    else:
        
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']

        if(name != "" and email != "" and password != "" and phone != ""):
            if(len(str(phone)) != 10 or (str.isdigit(phone) != True)):
                flash('El número telefónico debe ser de 10 dígitos y un número entero')
                return render_template("login.html")
                
            elif(cuentas.find_one({"correo": (email)}) != None):
                flash('El correo electronico ya está registrado')
                return render_template("login.html")
            else:
                session['email'] = email
                session['password'] = password
                session['name'] = name
                session['phone']= phone
                phone = "+521" +phone
                print("hola1")

                user = {
                    "matricula": "a",
                    "nombre": name,
                    "correo": email,
                    "contrasena": password,
                    "telefono": phone,
                }
                print("hola 1.5")
                comogusten = TwilioClient.messages.create(
                    from_="whatsapp:+14155238886",
                    body="Hola, %s, desde aquí recibirás todas las ofertas especiales que existan en nuestra pagina prueba finare" % (
                        name),
                    to="whatsapp:"+phone
                )
                try:
                    print("hola2")
                    cuentas.insert_one(user)
                    return render_template('index.html', data=email)
                except Exception as e:
                    return "<p>El servicio no esta disponible =>: %s %s" % type(e), e
                


            
        else:
            flash('Introduce todos los datos')
            return render_template("login.html")



    


@app.route("/login", methods=["GET", "POST"])
def login():
    email = None
    if "email" in session:
        return render_template('index.html', data=session["email"])
    else:
        if (request.method == "GET"):
            return render_template("login.html", data="email")
        else:
            email = request.form["email"]
            password = request.form["password"]
            if(email != "" and password != ""):
                try:
                    user = cuentas.find_one({"correo": (email)})
                    if (user != None):
                        if(user["contrasena"]==password):
                            session["email"] = email
                            return render_template("index.html", data=user["nombre"])
                        else:
                            flash('La contraseña es incorrecta')
                            return render_template("login.html")
                    else:
                        flash('El correo no existe')
                        return render_template("login.html")
                        
                except Exception as e:
                    return "%s" % e
            else:
                flash('Introduce todos los datos')
                return render_template("login.html")

    


    




@app.route('/estructuradedatos')
def prueba():
    nombres = []
    nombres.append({"nombre": "ruben",

                    "Semetre01": [{
                        "matematicas": "8",
                        "español": "7"
                    }],
                    "Semetre02": [{
                        "programacion": "5",
                        "basededatos": "9"
                    }]
                    })

    return render_template("home.html", data=nombres)

@app.route('/logout')
def logout():
    if "email" in session:
        session.clear()
        return redirect(url_for("home"))

@app.route("/usuarios")
def usuarios():
    cursor = cuentas.find({})
    users = []
    for doc in cursor:
        users.append(doc)
    return render_template("/usuarios.html", data=users)


@app.route("/insert", methods=["POST"])
def insertUsers():
    user = {
        "matricula": request.form["matricula"],
        "nombre": request.form["nombre"],
        "correo": request.form["correo"],
        "contrasena": request.form["contrasena"],
    }
    try:
        cuentas.insert_one(user)
        comogusten = TwilioClient.messages.create(
            from_="whatsapp:+14155238886",
            body="El usuario %s se agregó a tu pagina web" % (
                request.form["nombre"]),
            to="whatsapp:+5215559435595"
        )
        return redirect(url_for("usuarios"))
    except Exception as e:
        return "<p>El servicio no esta disponible =>: %s %s" % type(e), e


@app.route("/find_one/<matricula>")
def find_one(matricula):
    try:
        user = cuentas.find_one({"matricula": (matricula)})
        if user == None:
            return "<p>La matricula %s nó existe</p>" % (matricula)
        else:
            return "<p>Encontramos: %s </p>" % (user)
    except Exception as e:
        return "%s" % e


@app.route("/delete/<matricula>")
def delete_one(matricula):
    try:
        user = cuentas.delete_one({"matricula": (matricula)})
        if user.deleted_count == None:
            return "<p>La matricula %s nó existe</p>" % (matricula)
        else:
            return redirect(url_for("usuarios"))
    except Exception as e:
        return "%s" % e


@app.route("/update", methods=["POST"])
def update():
    try:
        filter = {"matricula": request.form["matricula"]}
        user = {"$set": {
            "nombre": request.form["nombre"]
        }}
        cuentas.update_one(filter, user)
        return redirect(url_for("usuarios"))

    except Exception as e:
        return "error %s" % (e)


@app.route('/create')
def create():
    return render_template("Create.html")