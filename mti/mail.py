import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import pytesseract
from flask import Flask, render_template, request, redirect, url_for, session
from PIL import Image
from flask_mail import Mail

app = Flask(__name__)
app.secret_key = 'Shashi kutta hai'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'MTI SERVICE'
app.config['MAIL_PASSWORD'] = 'mti@0076'
app.config['MAIL_DEFAULT_SENDER'] = 'mti.service.email@gmail.com'

mail = Mail(app)


@app.route('/')
def index():
    return render_template('home.html')


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
            # User Information
            user_mail = user[0]
            user_password = user[1]
            recipient_mail = user[2]

            if len(user) >= 4:
                cc_mail = user[3]

            # Message Instance
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


if __name__ == '__main__':
    # Setup Tesseract executable path
    pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\\tesseract'
    app.run(debug=True)
