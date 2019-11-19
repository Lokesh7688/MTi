import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import pytesseract
from PIL import Image
from flask import Flask, render_template, redirect, url_for, session, request
from flask_sqlalchemy import SQLAlchemy
import razorpay
import json

from flask_migrate import Migrate
app = Flask(__name__, static_folder="static", static_url_path='')
razorpay_client = razorpay.Client(auth=("<rzp_test_zUzzVSWtNoygBS>", "<XOqJEYAk0IswZYGGpBHr6jgd>"))

app.secret_key = 'Shashi kutta hai'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///MtiDataBase.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120))
    password = db.Column(db.String(80))


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/reg", methods=["GET", "POST"])
def reg():
    return redirect(url_for("register"))


@app.route("/logi")
def logi():
    return redirect(url_for("login"))


@app.route("/price")
def price():
    return render_template("price.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["uname"]
        passw = request.form["passw"]

        login = user.query.filter_by(username=uname, password=passw).first()
        if login is not None:
            return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form['uname']
        mail = request.form['mail']
        passw = request.form['passw']

        register = user(username=uname, email=mail, password=passw)
        db.session.add(register)
        db.session.commit()

        return redirect(url_for("login"))
    return render_template("register.html")



@app.route('/', methods=['POST', 'GET'])
def mailForm():
    """ Fill the form of the request """
    if request.method == 'POST':
        userEmail = request.form['userEmail']
        userPassword = request.form['userPassword']
        recipientEmail = request.form['recipientEmail']
        ccEmail = request.form['CCEmail']

        userInformation = (userEmail, userPassword, recipientEmail, ccEmail)

        mailSubject = request.form['msgSubject']
        mailMessage = request.form['msgMessage']

        msgBody = (mailSubject, mailMessage)

        def serverAndPort(user, req):
            """ Return the server and port by user and req """

            mailClient = user.split('@')[1].split('.')[0]

            smtpserverlist = {
                'yahoo': ['smtp.mail.yahoo.com', 587],
                'gmail': ['smtp.gmail.com', 587],
                'yandex': ['smtp.yandex.com', 465]
            }

            if req == 'server':
                return smtpserverlist[mailClient][0]
            elif req == 'port':
                return smtpserverlist[mailClient][1]
            else:
                return None

        def sendMessage(user, msg):
            """ Sending the Message via SMTP """
            user_mail = user[0]
            user_password = user[1]
            recipient_mail = user[2]

            if len(user) >= 4:
                cc_mail = user[3]

            message = MIMEMultipart()
            message['From'] = user_mail
            message['To'] = recipient_mail
            message['Subject'] = msg[0]
            body = msg[1]
            message.attach(MIMEText(body, _subtype='plain'))
            text = message.as_string()

            # Server Setup
            try:
                server = smtplib.SMTP(serverAndPort(user_mail, 'server'), serverAndPort(user_mail, 'port'))
                server.ehlo()
                server.starttls()
                server.login(user_mail, user_password)
                server.sendmail(user_mail, recipient_mail, text)
            except:
                return render_template('error.html')

            server.close()
            return render_template('finish.html')

        return sendMessage(userInformation, msgBody)

    return render_template('home.html')


@app.route('/scanner', methods=['GET', 'POST'])
def scan_file():
    if request.method == 'POST':
        start_time = datetime.datetime.now()
        image_data = request.files['file'].read()

        scanned_text = pytesseract.image_to_string(Image.open(io.BytesIO(image_data)))

        print("Found data:", scanned_text)

        session['data'] = {
            "text": scanned_text,
            "time": str((datetime.datetime.now() - start_time).total_seconds())
        }

        return redirect(url_for('result'))


@app.route('/result')
def result():
    if "data" in session:
        data = session['data']
        return render_template(
            "home.html",
            title="Result",
            time=data["time"],
            text=data["text"],
            words=len(data["text"].split(" "))
        )
    else:
        return "Wrong request method."


@app.route('/pay')
def pay():
    return render_template('pay.html')


@app.route('/charge', methods=['POST'])
def app_charge():
    amount = 5100
    payment_id = request.form['razorpay_payment_id']
    razorpay_client.payment.capture(payment_id, amount)
    return json.dumps(razorpay_client.payment.fetch(payment_id))


if __name__ == '__main__':
    db.create_all()
    # Setup Tesseract executable path
    pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\\tesseract'
    app.run(debug=True)
