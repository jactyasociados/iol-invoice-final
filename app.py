from flask import Flask, request, redirect, url_for, render_template, jsonify, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_modus import Modus
from flask_mail import Mail
from flask_moment import Moment
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
import os
import re
from werkzeug.utils import secure_filename
import PIL
from PIL import Image
from datetime import date
from mega import Mega




app = Flask(__name__,
            static_url_path='', 
            static_folder='static')


app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
modus = Modus(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)
#bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
bcrypt = Bcrypt(app)
mega = Mega()


app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

path = os.getcwd()
# file Upload
UPLOAD_FOLDER = os.path.join(path, 'uploads')

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
from models import User, InvoiceData, InvoiceItems, ImageData, InvoiceValues, ProfileData

class InvoiceDataSchema(ma.SQLAlchemyAutoSchema):
        class Meta:
        	model = InvoiceData
        	load_instance = True

# setup the login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
           
####  setup routes  ####
@app.route('/')
@login_required
def index():
    return render_template('index.html', user=current_user)
    
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    user_id = current_user.user_id_hash
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            extension=filename.split(".")
            extension=str(extension[1])
            name=current_user.user_id_hash
            name=name.replace("/","$$$")
            destination=name+"orig"+"."+extension
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], destination))
            
            image = PIL.Image.open(os.path.join(app.config['UPLOAD_FOLDER'], destination))
            
            width, height = image.size
            
            #print(width, height)
            finalimagename=name+"."+extension 
            basewidth = 200
            img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], destination))
            wpercent = (basewidth / float(img.size[0]))
            hsize = int((float(img.size[1]) * float(wpercent)))
            img = img.resize((basewidth, hsize), Image.ANTIALIAS)
            img.save(os.path.join(app.config['UPLOAD_FOLDER'], finalimagename))
            new__image = PIL.Image.open(os.path.join(app.config['UPLOAD_FOLDER'], finalimagename))
            width, height = new__image.size
            email = 'jctyasociados@gmail.com'
            password = '1to1anyherzT&'
            m = mega.login(email, password)
            os.chdir(r"uploads")
            os.remove(destination)
            file = m.upload(finalimagename)
            url_link = m.get_upload_link(file)
            #print(url_link)
            os.chdir(r"..")
            
            
            user_hashed=current_user.user_id_hash
            new_image = ImageData(user_hashed, finalimagename, url_link, width, height)
            db.session.add(new_image)
            db.session.commit()
            
            
            flash('File successfully uploaded')
            return redirect('/upload')
        else:
            flash('Allowed file types are png, jpg, jpeg, gif')
            return redirect(request.url)
    return render_template('upload.html', user=current_user)



@app.route("/login", methods=["GET", "POST"])
def login():

    # clear the inital flash message
    session.clear()
    if request.method == 'GET':
        return render_template('login.html')

    # get the form data
    username = request.form['username']
    password = request.form['password']

    remember_me = False
    if 'remember_me' in request.form:
        remember_me = True

    # query the user
    registered_user = User.query.filter_by(username=username).first()

    # check the passwords
    if registered_user is None:
        flash('Invalid Username')
        return render_template('login.html')
        
    if registered_user.username == username and bcrypt.check_password_hash(registered_user.password, password) == False:
    	flash('Invalid Password')
    	return render_template('login.html')

    # login the user
    #else:
    if registered_user.username == username and bcrypt.check_password_hash(registered_user.password, password) == True:
    		login_user(registered_user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/registration', methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        session.clear()
        return render_template('register.html')

    # get the data from our form
    password = request.form['password']
    conf_password = request.form['confirm-password']
    username = request.form['username']
    email = request.form['email']

    # make sure the password match
    if conf_password != password:
        flash("Passwords do not match")
        return render_template('register.html')

    # check if it meets the right complexity
    check_password = password_check(password)

    # generate error messages if it doesnt pass
    if True in check_password.values():
        for k,v in check_password.items():
            if str(v) == "True":
                flash(k)

        return render_template('register.html')

    # hash the password for storage
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    user_id_hashed = bcrypt.generate_password_hash(username).decode('utf-8')

    # create a user, and check if its unique
    user = User(username, user_id_hashed, pw_hash, email)
    u_unique = user.unique()

    # add the user
    if u_unique == 0:
        db.session.add(user)
        db.session.commit()
        flash("Account Created")
        return redirect(url_for('login'))

    # else error check what the problem is
    elif u_unique == -1:
        flash("Email address already in use.")
        return render_template('register.html')

    elif u_unique == -2:
        flash("Username already in use.")
        return render_template('register.html')

    else:
        flash("Username and Email already in use.")
        return render_template('register.html')
    



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = current_user.user_id_hash
    if request.method == 'POST':
        new_profile = ProfileData(user_id, request.form['businessname'], request.form['email'], request.form['ein'], request.form['address1'], request.form['address2'], request.form['city'], request.form['state'], request.form['zip'])
        db.session.add(new_profile)
        db.session.commit()
        flash("Profile Adeed to Database")    
    return render_template('profile.html', user=current_user)


@app.route('/invoice', methods=['GET', 'POST'])
@login_required
def invoice():
    
    user_hashed=current_user.user_id_hash
    
    try:
        if request.method == 'POST':
            invoice_date=request.form['invoice_date']
            #print(invoice_date)
            date_inv=invoice_date.replace("-",",")
            y, m, d = date_inv.split(',')
            date_inv = date(int(y), int(m), int(d))
            
            #print(date_inv)
            new_invoice_data = InvoiceData(user_hashed, request.form['invoice_number'], request.form['businessname'], request.form['email'], request.form['ein'], request.form['address'], request.form['address2'], request.form['city'], request.form['state'], request.form['zip'], request.form['businessname_shipping'], request.form['email_shipping'], request.form['ein_shipping'],request.form['address_shipping'], request.form['address2_shipping'], request.form['city_shipping'], request.form['state_shipping'], request.form['zip_shipping'], date_inv, request.form['taxes'])
            db.session.add(new_invoice_data)
            db.session.commit()
            
            for desc, price, quant, amount in zip(request.form.getlist('item_desc[]'), request.form.getlist('item_price[]'), request.form.getlist('item_quant[]'), request.form.getlist('amount[]')):
                new_item = InvoiceItems(user_hashed, request.form['invoice_number'], desc, price, quant, amount)
                db.session.add(new_item)
                db.session.commit()
            new_invoice_values = InvoiceValues(user_hashed, request.form['invoice_number'], request.form['subtotal'], request.form['totaltax'], request.form['grandtotal'])
            db.session.add(new_invoice_values)
            db.session.commit()
            #return 'Invoice added to database'
            found_invoice_data = db.session.query(InvoiceData).filter_by(user_id=(user_hashed), invoice_number=(request.form['invoice_number'])).first()
            found_invoice_items = db.session.query(InvoiceItems).filter_by(user_id=(user_hashed), invoice_number=(request.form['invoice_number'])).all()
            found_invoice_values = db.session.query(InvoiceValues).filter_by(user_id=(user_hashed), invoice_number=(request.form['invoice_number'])).first() 
            return render_template('invoice-html.html', user=current_user, invoice_data=found_invoice_data, items_data=found_invoice_items, invoice_values=found_invoice_values)   
               
        
        else:
            return render_template('invoice.html', user=current_user)
    except Exception as e:
        print(str(e))
        
    #return render_template('invoice.html')
    return 'Done'
    
@app.route('/_get_data_by_ein')
def get_by_ein():
    
    ein_result = request.args.get('ein')
    print(ein_result)

    result = db.session.query(InvoiceData).filter_by(ein = ein_result).first()
    invoicedata_schema	= InvoiceDataSchema()
   
    #result = Response(jsonpickle.encode(query1), mimetype='application/json')
    
    
    #print(result)
    output = invoicedata_schema.dump(result)
    
   
    
    #return jsonify({'invoiceaddress' : output})
    return jsonify(output)
    

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# check password complexity
def password_check(password):
    """
    Verify the strength of 'password'
    Returns a dict indicating the wrong criteria
    A password is considered strong if:
        8 characters length or more
        1 digit or more
        1 symbol or more
        1 uppercase letter or more
        1 lowercase letter or more
        credit to: ePi272314
        https://stackoverflow.com/questions/16709638/checking-the-strength-of-a-password-how-to-check-conditions
    """

    # calculating the length
    length_error = len(password) <= 8

    # searching for digits
    digit_error = re.search(r"\d", password) is None

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None

    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None

    # searching for symbols
    symbol_error = re.search(r"[ !@#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) is None

    ret = {
        'Password is less than 8 characters' : length_error,
        'Password does not contain a number' : digit_error,
        'Password does not contain a uppercase character' : uppercase_error,
        'Password does not contain a lowercase character' : lowercase_error,
        'Password does not contain a special character' : symbol_error,
    }

    return ret    
    
        
if __name__ == "__main__":
    app.run()
