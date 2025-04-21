from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify, flash, session
import os
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from premailer import transform
import base64
from email.mime.image import MIMEImage
from ccavutil import encrypt, decrypt
import json
import random
from datetime import datetime, timedelta
from string import Template
import threading





app = Flask(__name__)
app.secret_key = '#register_with_hashtag0909'



# Google Sheets API credentials
scopes = ['https://www.googleapis.com/auth/spreadsheets']

# Load the credentials from the JSON key file
credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scopes)
client = gspread.authorize(credentials)

os.environ['SHEET_KEY'] = '1cJdiWjKzOMK6kVkPWBfhBVGTy_bsxDBwDbwlagkQfY4'
os.environ['SHEET_NAME'] = 'Registrations'
os.environ['WORKING_KEY'] = "868E43E034DB2953A9E18EC401CA3268"
os.environ['ACCESS_CODE'] = "AVKR14KI19BL44RKLB"
os.environ['THREE_MONTHS_VALIDITY'] = "false"
os.environ['GRID_VALIDITY'] = "true"

# Environment variables with values in the desired format
os.environ['PRIYANSHI_PASSWORD'] = "priyanshi_password"
os.environ['KAJAL_PASSWORD'] = "kajal_password"
os.environ['JHILMIL_PASSWORD'] = "jhilmil_password"
os.environ['RUBANI_PASSWORD'] = "rubani_password"
os.environ['JAHNVI_PASSWORD'] = "jahnvi_password"
os.environ['MUSKAN_PASSWORD'] = "muskan_password"
os.environ['TARUN_PASSWORD'] = "tarun_password"

# Google Sheet details
sheet_key = os.environ.get('SHEET_KEY')
sheet_name = os.environ.get('SHEET_NAME')


# PROMO CODE HANDLER


def generate_random_promo_code(length=8 ):
    characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"
    return f"Hashtag{''.join(random.choice(characters) for _ in range(length))}"


def load_promo_data(filename):
    try:
        if not os.path.exists(filename):
            return []  # Return an empty list if the file doesn't exist

        with open(filename, 'r') as json_file:
            promo_data = json.load(json_file)

        # Ensure that promo_data is a list, or initialize an empty list
        if not isinstance(promo_data, list):
            promo_data = []

        return promo_data

    except (FileNotFoundError, json.JSONDecodeError):
        return []
def get_studio_wingperson(studio):
    if studio == "NDA":
        wingperson = "Priyanshi"
        return wingperson
    if studio == "RG":
        wingperson = "Kajal"
        return wingperson

    if studio == "PP":
        wingperson = "Rubani"
        return wingperson

    if studio == "SD":
        wingperson = "Jhilmil"
        return wingperson

    if studio == "ED":
        wingperson = "Muskan"
        return wingperson

    if studio == "GGN":
        wingperson = "Jahnvi"
        return wingperson

    if studio == "IPM":
        wingperson = "Tarun"
        return wingperson


def return_studio_fullform(studio):
    studio_dic = {
        "ED": "East Delhi",
        "NDA": "Noida",
        "RG": "Rajouri Garden",
        "SD": "South Delhi",
        "GGN": "Gurgaon",
        "PP": "Pitampura",
        "IPM": "Indirapuram"
    }
    return studio_dic[studio]


def get_studio_location(studio):
    if studio == "Noida":
        location = "https://maps.app.goo.gl/EA75L86kCKT72H6N8"
        return location
    if studio == "Rajouri Garden":
        location = "https://maps.app.goo.gl/RqP29GsxekCRALrU9"
        return location
    if studio == "Pitampura":
        location = "https://maps.app.goo.gl/NMtbTXxBnV5rbBjB9"
        return location

    if studio == "South Delhi":
        location = "https://maps.app.goo.gl/FmzSXf8M12qKtN4r9"
        return location

    if studio == "East Delhi":
        location = "https://maps.app.goo.gl/6qcLECimcCqzSHEa7"
        return location

    if studio == "Gurgaon":
        location = "https://maps.app.goo.gl/p7G3kMkHaxGgP4Z98"
        return location

    if studio == "Indirapuram":
        location = "https://maps.app.goo.gl/xechLGU3XpZ1QX3J7"
        return location



def check_promo_validity(expiry_date):
    try:
        return expiry_date >= datetime.now()
    except ValueError:
        return False  # Handle invalid date format


def create_promo_json(name, email, phone, amount, dropin_date, filename):
    promo_code = generate_random_promo_code()
    today = datetime.strptime(dropin_date, "%Y-%m-%d")
    expiry = today + timedelta(hours=23, minutes=59, seconds=59)

    promo_entry = ({
        "promo_code": promo_code,
        "expiry": expiry.strftime("%Y-%m-%d %H:%M:%S"),
        "name": name,
        "email": email,
        "phone": phone,
        "amount": amount
    })

    promo_data = load_promo_data(filename)
    promo_data.append(promo_entry)

    with open(filename, 'w') as json_file:
        json.dump(promo_data, json_file, indent=4)

    return promo_code  # Return the generated promo code


def apply_promo_code(name, email, phone, promo_code, filename):
    try:
        promo_data = load_promo_data(filename)
        amount = 0

        for promo_entry in promo_data:
            if (
                    promo_entry.get("name") == name
                    and promo_entry.get("email") == email
                    and promo_entry.get("phone") == phone
                    and promo_entry.get("promo_code") == promo_code
                    and check_promo_validity(datetime.strptime(promo_entry["expiry"], "%Y-%m-%d %H:%M:%S"))
            ):
                print("applied")
                amount = promo_entry.get('amount')
                break
        return amount
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return False  # Handle exceptions gracefully


    return 0  # No matching or valid promo code found



def remove_promo_code(name, email, phone, promo_code, filename):
    promo_data = load_promo_data(filename)

    for promo_entry in promo_data:
        if (
                promo_entry.get("name") == name
                and promo_entry.get("email") == email
                and promo_entry.get("phone") == phone
                and promo_entry.get("promo_code") == promo_code
                and check_promo_validity(datetime.strptime(promo_entry["expiry"], "%Y-%m-%d %H:%M:%S"))
        ):
            promo_data.remove(promo_entry)

            with open(filename, 'w') as json_file:
                json.dump(promo_data, json_file, indent=4)

# Your Cc avenue API credentials


workingKey = "868E43E034DB2953A9E18EC401CA3268"
accessCode = "AVKR14KI19BL44RKLB"


# Receipt Number Generation

def get_current_receipt_number():
    # Code to retrieve the current receipt number from storage (file or database)
    # Return the current receipt number as an integer
    # Example: read from a file
    with open("receipt_number.txt", "r") as file:
        current_receipt_number = int(file.read())
    return str(current_receipt_number)


# Increment Receipt number

def increment_receipt_number():
    # Get the current receipt number
    current_receipt_number = int(get_current_receipt_number())

    # Increment the receipt number by one
    new_receipt_number = current_receipt_number + 1

    # Update the storage with the new receipt number
    # Example: write to a file
    with open("receipt_number.txt", "w") as file:
        file.write(str(new_receipt_number))

    # Return the new receipt number
    return str(new_receipt_number)


def increment_receipt_number():
    # Get the current receipt number
    current_receipt_number = int(get_current_receipt_number())

    # Increment the receipt number by one
    new_receipt_number = current_receipt_number + 1

    # Update the storage with the new receipt number
    # Example: write to a file
    with open("receipt_number.txt", "w") as file:
        file.write(str(new_receipt_number))

    # Return the new receipt number
    return str(new_receipt_number)


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



def send_receipt(receiver_mail, rendered_html):
    my_email = "singhalshivek24@gmail.com"
    password = 'yhczvwbgkmdbkdgm'
    smtp_server = "smtp.gmail.com"
    email_subject = "Registration Receipt Feb'24"
    smtp_port = 587

    inlined_html = transform(rendered_html)
    print("done")
    print("done1")

    msg = MIMEMultipart()
    msg["From"] = my_email
    msg["To"] = receiver_mail
    msg["Subject"] = email_subject

    body = MIMEText(inlined_html, "html")
    msg.attach(body)
    print("done2")
    with open('./static/images/hashtag_logofinal.webp', 'rb') as image_file:
        image = MIMEImage(image_file.read())
        image.add_header('Content-ID', '<logo_image>')
        msg.attach(image)
    with open('./static/images/phone.png', 'rb') as image_file:
        image_phone = MIMEImage(image_file.read())
        image_phone.add_header('Content-ID', '<phone>')
        msg.attach(image_phone)
    with open('./static/images/whatsapp.png', 'rb') as image_file:
        image_whatsapp = MIMEImage(image_file.read())
        image_whatsapp.add_header('Content-ID', '<whatsapp>')
        msg.attach(image_whatsapp)
    with open('./static/images/instagram.png', 'rb') as image_file:
        image_instagram = MIMEImage(image_file.read())
        image_instagram.add_header('Content-ID', '<instagram>')
        msg.attach(image_instagram)

    with open('./static/images/email.png', 'rb') as image_file:
        image_email = MIMEImage(image_file.read())
        image_email.add_header('Content-ID', '<email>')
        msg.attach(image_email)

    with open('./static/images/pink.png', 'rb') as image_file:
        image_watermark = MIMEImage(image_file.read())
        image_watermark.add_header('Content-ID', '<watermark>')
        msg.attach(image_watermark)

    print("images rendered")

    with smtplib.SMTP(smtp_server, smtp_port) as connection:
        connection.starttls()
        connection.login(my_email, password)
        connection.send_message(msg)
    print("email sent")


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
        return encoded_image


# Dictionary of name-password pairs

name_password_pairs = dict(Priyanshi=os.environ.get("PRIYANSHI_PASSWORD"), Kajal=os.environ.get("KAJAL_PASSWORD"),
                           Jhilmil=os.environ.get("JHILMIL_PASSWORD"),
                           Rubani=os.environ.get("RUBANI_PASSWORD"), Jahnvi=os.environ.get("JAHNVI_PASSWORD"),
                           Muskan=os.environ.get("MUSKAN_PASSWORD"),
                           Tarun=os.environ.get("TARUN_PASSWORD"))


@app.route('/static/<path:filename>')
def serve_static(filename):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(os.path.join(root_dir, 'static'), filename)


# Drop In
@app.route('/dropin', methods=['GET', 'POST'])
def registration_form_dropin():
    return render_template('dropin.html')

@app.route('/dropintest')
def test_dropin():
    return render_template("dropin_test.html")



@app.route('/dropinbatch', methods=['GET', 'POST'])
def select_dropin():
    three_months_validty = os.environ.get('THREE_MONTHS_VALIDITY')
    grid_validity = os.environ.get('GRID_VALIDITY')
    session['name'] = request.form['name']
    session['phone'] = request.form['phone']
    session['email'] = request.form['email']
    session['studio'] = request.form['Studio']

    today_date = datetime.today().strftime('%d-%b-%Y %H:%M:%S')
    dropin_studio = session.get('studio')
    sheet = client.open_by_key(sheet_key).worksheet("Payment_Incomplete(DropIn)")
    dropin_data = [today_date, session.get('name'), session.get('phone'), session.get('email'), session.get('studio')]

    sheet.append_row(dropin_data)

    print(dropin_studio)

    # elif studio in ["Gurgaon", "South Delhi", "Indirapuram"]:
    #     batch_scenario = "heels_once"
    #
    # else:
    #     batch_scenario = "once"


    return render_template('selectdropin.html', dropin_studio=dropin_studio,
                           three_months_validty="true", grid_validity="true")


# Registration Form


@app.route('/', methods=['GET', 'POST'])
def registration_form():

    return render_template('index.html')

@app.route('/batch', methods=['GET', 'POST'])
def select_batch():
    global name, phone, email, studio, promo_code_applied, batch_scenario

    session['name'] = request.form['name']
    session['phone'] = request.form['phone']
    session['email'] = request.form['email']
    session['studio'] = request.form['Studio']
    session['promo_code_applied'] = request.form['promo']

    name = session.get('name')
    phone = session.get('phone')
    email = session.get('email')

    today_date = datetime.today().strftime('%d-%b-%Y %H:%M:%S')
    sheet = client.open_by_key(sheet_key).worksheet("Payment_Incomplete")
    registration_data = [today_date, session.get('name'), session.get('phone'), session.get('email'), session.get('studio')]

    sheet.append_row(registration_data)

    promo_code_applied = session.get('promo_code_applied')
    batch_scenario = ""
    if session.get('studio') in ["Noida", "Rajouri Garden", "Pitampura", "Gurgaon", "South Delhi"]:
        batch_scenario = "twice"


    elif session.get('studio') in ["Indirapuram"]:
        batch_scenario = "no_modern"

    else:
        batch_scenario = "once"

    promo_data = load_promo_data("promo_data.json")
    if promo_data is not None:
        discount = int(apply_promo_code(name, email, phone, promo_code_applied, filename="promo_code.json"))
        if promo_code_applied == "":
            discount = 0
            return render_template('selectbatch.html', batch_scenario=batch_scenario, discount=discount)

        if discount > 0:
            print(discount)

            return render_template('selectbatch.html', batch_scenario=batch_scenario, discount=discount,
                                   promo_message=f"Promo Code worth {discount} applied successfully")
        if discount == 0:
            return render_template('selectbatch.html', batch_scenario=batch_scenario, discount=discount,
                                   promo_message=f"Promo Code expired or invalid user details")


@app.route('/payment-method', methods=['GET', 'POST'])
def make_payment():




      # Replace with your own logic to generate a unique order receipt ID



    if request.form['fee'] == "":
        flash(category=str, message="Please select atleast 1 batch")
        return redirect("/")
    else:
        session['order_receipt'] = get_current_receipt_number()
        session['batches'] = request.form.getlist('batch[]')
        session['fee_without_gst'] = request.form['fee']
        session['fee'] = str(round(float(session.get('fee_without_gst')) * 1.18))
        paid_to = "Pink Grid"
        session['validity'] = request.form['validity']
        validity = session.get('validity')
        if validity == "two_months_grid":
            session['validity'] = "Grid, December, January"
        if validity == "three_months":
            validity = "August, September, December"
        if validity == "grid":
            validity = "Grid 2.0"
        if validity == "Drop In":
            session['dropin_date'] = request.form['dropin_date']
            session['batch'] = request.form['batch']

        return render_template('pay.html')


workingKey = "868E43E034DB2953A9E18EC401CA3268"
accessCode = "AVKR14KI19BL44RKLB"

@app.route('/payment', methods=['GET', 'POST'])
def ccavenue_login():
    p_merchant_id = "2538003"
    p_order_id = f"order_{session.get('order_receipt')}"
    p_currency = 'INR'
    p_amount = session.get('fee')
    p_redirect_url = "https://register.hashtag.dance/success"
    p_cancel_url = "https://register.hashtag.dance/failed"
    p_billing_name = session.get('name')
    p_phone = session.get('phone')
    p_email = session.get('email')





    merchant_data = 'merchant_id=' + p_merchant_id + '&' + 'order_id=' + p_order_id + '&' + "currency=" + p_currency + '&' + 'amount=' + p_amount + '&' + 'redirect_url=' + p_redirect_url + '&' + 'cancel_url=' + p_cancel_url + '&' + 'billing_name=' + p_billing_name + '&' + 'billing_tel=' + p_phone + '&' + 'billing_email=' + p_email + '&'

    encryption = encrypt(merchant_data, workingKey)
    mid= p_merchant_id
    xscode = accessCode
    enReq = encryption

    html = '''\
    <html>
    <head>
    	<title>Sub-merchant checkout page</title>
    	<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
    </head>
    <body>
    <form id="nonseamless" method="post" name="redirect" action="https://secure.ccavenue.com/transaction/transaction.do?command=initiateTransaction" > 
    		<input type="hidden" id="encRequest" name="encRequest" value=$encReq>
    		<input type="hidden" name="access_code" id="access_code" value=$xscode>
    		<script language='javascript'>document.redirect.submit();</script>
    </form>
    <div id="gstBreakup">
        <h2>GST Breakup</h2>
        <p>GST Percentage: <span id="gstPercentage">{{p_amount/118%}}</span></p>
        <p>GST Amount: <span id="gstAmount">{{p_amount/118%*18%}}</span></p>
        <p>Total Amount (Including GST): <span id="totalAmount">{{p_amount}}</span></p>
    </div>    
    </body>
    </html>
    '''
    fin = Template(html).safe_substitute(encReq=encryption, xscode=accessCode)

    return fin


@app.route('/cash_payment', methods=['GET', 'POST'])
def cash_payment():
    studio = session.get('studio')

    session['wingperson'] = get_studio_wingperson(studio)
    fee = session.get('fee')

    return render_template('cash.html',studio=studio, full_studio=return_studio_fullform(studio), fee=fee, wingperson=session.get('wingperson'), location=get_studio_location(studio=studio))





@app.route('/process_cash', methods=['GET', 'POST'])
def process_cash():
    if request.method == "POST":
        global wingperson_name
        # wingperson_name = request.form.get('wingperson_name')
        wingperson_name = session.get('wingperson')
        password = request.form.get('password')
        mode_of_payment = "Cash"

        if wingperson_name in name_password_pairs and password == name_password_pairs[wingperson_name]:
            # Password verification succeeded
            return redirect(url_for('payment_successful', source=mode_of_payment))
        else:
            # Password verification failed
            return redirect(url_for('payment_failed'))

    else:
        return render_template("cash.html")


@app.route('/success', methods=['GET', 'POST'])
def payment_successful():
    request.form.get('')
    sheet = client.open_by_key(sheet_key).worksheet(sheet_name)
    batch_str = ', '.join(session.get('batches'))  # Join the batches list with a comma separator
    today_date = datetime.today().strftime('%d-%b-%Y')
    name = session.get('name')
    phone = session.get('phone')
    email = session.get('email')
    order_receipt = session.get('order_receipt')
    fee_without_gst = session.get('fee_without_gst')
    validity = session.get('validity')
    fee = session.get('fee')
    studio = session.get('studio')
    mode_of_payment = session.get('mode_of_payment')
    promo_code_applied = session.get('promo_code_applied')
    source = request.args.get('source')
    if source == "Cash":
        mode_of_payment = "Cash"
        paid_to = wingperson_name

    else:
        mode_of_payment = "Bank Transfer"
        paid_to = "Pink Grid"


    if validity == 'grid':
        validity = "Grid 2.0"


        # if promo_data is not None:


    elif validity == "Drop In":
        batch_str = session.get('batch')
        promo_code_created = create_promo_json(name, email, phone, fee_without_gst, session.get('dropin_date'),
                                       "promo_code.json")

    if promo_code_applied:
        remove_promo_code(name, email, phone, promo_code_applied, filename="promo_code.json")

    print(batch_str)
    print(source)
    if validity == "Drop In":
        row = [today_date, name, phone, email, "#" + order_receipt, validity, batch_str, fee, studio,
               mode_of_payment, paid_to, promo_code_created]
    else:
        promo_code_created = ""

        row = [today_date, name, phone, email, "#" + order_receipt, validity, batch_str, fee, studio,
               mode_of_payment, paid_to, promo_code_applied]

    gross_amount = round(float(fee) / 1.18, 2)
    gst = round(gross_amount * 0.18, 2)

    hashtag_logo = image_to_base64('./static/images/Hashtag_logo.png')
    hashtag_watermark = image_to_base64('./static/images/pink.png')
    increment_receipt_number()

    sheet.append_row(row)
    print("Succesfully added to sheets")


    def send_receipt_background():
        rendered_receipt = render_template("receipt2.html", date=today_date, name=name, batch=batch_str, phone=phone,
                                           validity='September, October, Grid', email=email, studio=studio, gross_amount=gross_amount,
                                           gst=gst, fee=fee, order_receipt=f"#{str(order_receipt)}",
                                           mode_of_payment="Bank Transfer", paid_to="Pink Grid", hashtag_logo=hashtag_logo,
                                           watermark=hashtag_watermark, promo_code=promo_code_created)

        print("reciptrendered")

        send_receipt(receiver_mail=email, rendered_html=rendered_receipt)

    # thread = threading.Thread(target=send_receipt_background)
    # thread.start()
    send_receipt_background()
    print("receipt sent")



    return render_template("success.html")

# def render_recipt(date):
#     return render_template("receipt2.html", date=today_date, name=name, batch=batch_str, phone=phone,
#                                        validity=validity, email=email, studio=studio, gross_amount=gross_amount,
#                                        gst=gst, fee=fee, order_receipt=f"#{str(order_receipt)}",
#                                        mode_of_payment=mode_of_payment, paid_to=paid_to, hashtag_logo=hashtag_logo,
#                                        watermark=hashtag_watermark, promo_code=promo_code)


@app.route('/terms')
def terms_and_conditions():
    return render_template("terms.html")

@app.route('/privacypolicy')
def privacypolicy():
    return render_template("privacypolicy.html")

@app.route('/failed', methods=['GET', 'POST'])
def payment_failed():
    return render_template('failed.html')


if __name__ == '__main__':
    app.run(debug=True, port=4915)

