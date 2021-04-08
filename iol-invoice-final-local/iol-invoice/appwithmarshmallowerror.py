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
import dropbox
from xhtml2pdf import pisa 




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
 
from models import User, InvoiceData, InvoiceItems, ImageData, InvoiceValues, ProfileData, TemplateData

class InvoiceDataSchema(ma.SQLAlchemyAutoSchema):
        class Meta:
        	model = InvoiceData
        	load_instance = True

# setup the login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class TransferData:
    
    def __init__(self, access_token):
        self.access_token = access_token
        
    def upload_file(self, file_from, file_to):
        
        dbx = dropbox.Dropbox(self.access_token)
        
        with open(file_from, 'rb') as f:
            dbx.files_upload(f.read(), file_to)
           
####  setup routes  ####
@app.route('/')
@login_required
def index():
    return render_template('index.html', user=current_user)
    
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    #user_id = current_user.user_id_hash
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
            if width > 200:
                img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], destination))
                wpercent = (basewidth / float(img.size[0]))
                hsize = int((float(img.size[1]) * float(wpercent)))
                img = img.resize((basewidth, hsize), Image.ANTIALIAS)
                img.save(os.path.join(app.config['UPLOAD_FOLDER'], finalimagename))
                new__image = PIL.Image.open(os.path.join(app.config['UPLOAD_FOLDER'], finalimagename))
                width, height = new__image.size
            os.chdir(r"uploads")
            os.remove(destination)
            
            access_token = 'cnX-updmdekAAAAAAAAAASkEbkYdKaLrD3o7Z7Pc7C7o7dPFnPzZmikuNdXxJI1J'
            transferData = TransferData(access_token)
            
            file_from = finalimagename
            file_to = '/iolcloud/' + finalimagename # The full path to upload the file to, including the file name
            dbx = dropbox.Dropbox(access_token)
            
              # API v2
            transferData.upload_file(file_from, file_to)
            
            try:
                dbx.files_delete_v2("/iolcloud/" + finalimagename)
                transferData.upload_file(file_from, file_to)
            except:
                transferData.upload_file(file_from, file_to)
    
            result = dbx.files_get_temporary_link(file_to)
            name_url=result.link.replace("https:","")
            print(name)  


        

            #print(url_link)
            os.chdir(r"..")
            
            
            user_hashed=current_user.user_id_hash
            
            found_image_data = db.session.query(ImageData).filter_by(user_id=(user_hashed)).all()
            for row in found_image_data:
                ImageData.query.delete()
                db.session.commit()
            
            new_image = ImageData(user_hashed, finalimagename, name_url, width, height)
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
    #pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    #user_id_hashed = bcrypt.generate_password_hash(username).decode('utf-8')
    #mobile phone
    pw_hash = bcrypt.generate_password_hash(password)
    user_id_hashed = bcrypt.generate_password_hash(username)
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
    user_hashed = current_user.user_id_hash
    if request.method == 'POST':
        new_profile = ProfileData(user_hashed, request.form.get('businessname'), request.form.get('email'), request.form.get('ein'), request.form.get('address1'), request.form.get('address2'), request.form.get('city'), request.form.get('state'), request.form.get('zip'))
        db.session.add(new_profile)
        db.session.commit()
        #flash("Profile Adeed to Database")    
        return render_template('profile-added.html', user=current_user)
    return render_template('profile.html', user=current_user)


@app.route('/invoice', methods=['GET', 'POST'])
@login_required
def invoice():
    
    user_hashed=current_user.user_id_hash
    ROWS_PER_PAGE = 7
    
    try:
        if request.method == 'POST':
            invoice_date=request.form['invoice_date']
            #print(invoice_date)
            date_inv=invoice_date.replace("-",",")
            y, m, d = date_inv.split(',')
            date_inv = date(int(y), int(m), int(d))
            # Set the pagination configuration
            page = request.args.get('page', 1, type=int)
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
            found_invoice_items = db.session.query(InvoiceItems).filter_by(user_id=(user_hashed), invoice_number=(request.form['invoice_number'])).paginate(page=page, per_page=ROWS_PER_PAGE)
            found_invoice_values = db.session.query(InvoiceValues).filter_by(user_id=(user_hashed), invoice_number=(request.form['invoice_number'])).first() 
            found_profile_data = db.session.query(ProfileData).filter_by(user_id=(user_hashed)).first() 
            found_image_data = db.session.query(ImageData).filter_by(user_id=(user_hashed)).first() 
            rows = db.session.query(InvoiceItems).filter_by(user_id=(user_hashed), invoice_number=(request.form['invoice_number'])).count()
            POST_PER_PAGE = 30
            page = 1
            query = db.session.query(InvoiceItems).filter_by(user_id=(user_hashed), invoice_number=(request.form['invoice_number'])).paginate(page=page, per_page=POST_PER_PAGE).items
            sum = 0
            item_rows = 0
            name=user_hashed
            name=name.replace("/","$$$") 
            #write html and pdf code
            print(app.config['UPLOAD_FOLDER'])
            f=open("uploads/" + name + ".html","w")
            f.write("<html><head> \
            <style> \
            @page { \
            size: a4 portrait; \
            @frame header_frame {           /* Static frame */ \
            -pdf-frame-content: header_content; \
            left: 50pt; width: 512pt; top: 20pt; height: 150pt; \
            } \
            @frame content_frame {          /* Content Frame */ \
            left: 50pt; width: 512pt; top: 150pt; height: 632pt; \
            } \
           @frame footer_frame {           /* Another static Frame */ \
            -pdf-frame-content: footer_content; \
            left: 50pt; width: 512pt; top: 780pt; height: 20pt; \
            } \
            } \
            </style> \
            </head> \
            <body style='font-family: Arial, Helvetica, Verdana; font-size: 14px;'> \
            <div id='header_content'> \
            <table border='0' cellspacing='5' cellpadding='5' width='100%' style='font-family: Arial, Helvetica, Verdana; font-size: 14px;' > \
            <tr> \
            <td style='vertical-align: top;' width='50%'> \
            <img src='https:" + found_image_data.image_url + "' alt='Logo'> \
            </td> \
            <td style='vertical-align: top; text-align:right;' width='50%'> \
            <span style='text-align:right;'>" + found_profile_data.businessname + "</span><br /> \
            <span style='text-align:right;'>" + found_profile_data.email + "</span><br /> \
            <span style='text-align:right;'>" + found_profile_data.ein + "</span><br /> \
            <span style='text-align:right;'>" + found_profile_data.address1 + "</span><br />")
            f.close()
            if found_profile_data.address2 != '':
                f=open("uploads/" + name + ".html","a")
                f.write("<span>" + found_profile_data.address2 + "</span><br />")
                f.close()
            f=open("uploads/" + name + ".html", "a")
            f.write("<span style='text-align:right;'>" + found_profile_data.city + "</span>&nbsp;<span style='text-align:right;'>" + found_profile_data.state + "</span>&nbsp;<span style='text-align:right;'>" + found_profile_data.zip + "</span> \
            </td> \
            </tr> \
            </table> \
            <table border='0' cellspacing='5' cellpadding='5' width='100%'> \
            <tr> \
            <td style='width=50%'> \
            <table border='0' cellspacing='5' cellpadding='5' width='100%' style='font-family: Arial, Helvetica, Verdana; font-size: 20px;'><tr><td style='width=100%'><strong>Billing Address</strong></td></tr></table> \
            </td> \
            <td style='width=50%'> \
            <table border='0' cellspacing='5' cellpadding='5' width='100%' style='font-family: Arial, Helvetica, Verdana; font-size: 20px;'><tr><td style='width=100%'><strong>Shipping Address</strong></td></tr></table> \
            </td> \
            </tr> \
            </table> \
            <table border='0' cellspacing='5' cellpadding='5' width='100%'> \
            <tr> \
            <td style='width=50%'> \
            <table border='0' cellspacing='5' cellpadding='5' width='100%' style='font-family: Arial, Helvetica, Verdana; font-size: 14px;'><tr><td style='width=100%'><span>" + found_invoice_data.businessname + "</span><br /> \
            <span>" + found_invoice_data.email + "</span><br /> \
            <span>" + found_invoice_data.ein + "</span><br /> \
            <span>" + found_invoice_data.address + "</span><br />")
            f.close()
            if found_invoice_data.address2 != '':
                f=open("uploads/" + name + ".html","a")
                f.write("<span>" + found_invoice_data.address2 + "</span><br />")
                f.close()
            f=open("uploads/" + name + ".html", "a")
            f.write("<span>" + found_invoice_data.city + "</span>&nbsp;<span>" + found_invoice_data.state + "&nbsp;</span>&nbsp;<span>" + found_invoice_data.zip +"</span> \
            </td></tr></table> \
            </td> \
            <td style='width=50%'> \
            <table border='0' cellspacing='5' cellpadding='5' width='100%' style='font-family: Arial, Helvetica, Verdana; font-size: 14px;'><tr><td style='width=100%'><span>" + found_invoice_data.businessname_shipping + "</span><br /> \
            <span>" + found_invoice_data.email_shipping + "</span><br /> \
            <span>" + found_invoice_data.ein_shipping + "</span><br /> \
            <span>" + found_invoice_data.address_shipping + "</span><br />")
            f.close()
            if found_invoice_data.address2_shipping != '':
                f=open("uploads/" + name + ".html","a")
                f.write("<span>" + found_invoice_data.address2_shipping + "</span><br />")
                f.close()
            f=open("uploads/" + name + ".html","a")
            f.write("<span>" + found_invoice_data.city_shipping + "</span>&nbsp;<span>" + found_invoice_data.state_shipping + "</span>&nbsp;<span>" + found_invoice_data.zip_shipping + "</span> \
            </td></tr></table> \
            </td> \
            </tr> \
            </table> \
            <table border='0' cellspacing='5' cellpadding='5' width='100%' style='font-family: Arial, Helvetica, Verdana; font-size: 14px; margin-top:20px;'> \
            <tr><td style='width: 33%'><strong>Invoice Date:</strong>&nbsp;" + str(found_invoice_data.invoice_date) +"</td><td style='width: 33%'><strong>Invoice Number</strong>&nbsp;" + found_invoice_data.invoice_number + "</td><td style='width: 33%'><strong>Taxes</strong>&nbsp;" + found_invoice_data.taxes + "</td></tr>\
            </table></div> \
            <table border='0' cellspacing='5' cellpadding='5' width='100%' style='font-family: Arial, Helvetica, Verdana; font-size: 14px; margin-top:20px;'>")
            f.close()
            
            f=open("uploads/" + name + ".html","a")
            
            for item in query:
                f.write("<tr><td style='width: 25%'><span><strong>Description</strong><br />" + item.item_desc +"</span></td><td style='width: 25%'><span><strong>Price</strong><br />" + str(item.item_price) + "</span></td><td style='width: 25%'><span><strong>Quantity</strong><br />" + str(item.item_quant) + "</span></td><td style='width: 25%'><span><strong>Total</strong><br />" + str(item.amount) + "</span></td></tr>")
                sum += item.amount
                print(sum)
            f.write("</table>")
            f.close()
            '''f=open("uploads/" + name + ".html","a")
            f.write("<table border='0' cellspacing='5' cellpadding='5' width='100%' style='font-family: Arial, Helvetica, Verdana; font-size: 14px; margin-top:20px;'> \
            <tr><td style='width: 50%'><p></p></td><td style='width: 50%'><table border='0' cellspacing='5' cellpadding='5' width='100%' style='font-family: Arial, Helvetica, Verdana; font-size: 14px; margin-top:20px;'>")
            f.close()
            
            f=open("uploads/" + name + ".html","a")
            f.write("<tr><td style='width: 50%'><strong>Subtotal</strong></td><td style='width: 50%'>" + str(found_invoice_values.subtotal) + "</td></tr>")
            f.write("<tr><td style='width: 50%'><strong>Taxes</strong></td><td style='width: 50%'>" + str(found_invoice_values.taxes) + "</td></tr>")
            f.write("<tr><td style='width: 50%'><strong>Total</strong></td><td style='width: 50%'>" + str(found_invoice_values.total) + "</td></tr>")
            f.close()'''
            
            f=open("uploads/" + name + ".html","a")
            #f.write("</table> \
            f.write("<div id='footer_content' style='text-align: center;'>page <pdf:pagenumber> \
            of <pdf:pagecount> \
            </div> \
            </body> \
            </html>")
            f.close()
            
            OUTPUT_FILENAME = app.config['UPLOAD_FOLDER'] + "/" + name + ".pdf"
            TEMPLATE_FILE = app.config['UPLOAD_FOLDER'] + "/" + name + ".html"
            
            # Methods section ....
            def html_to_pdf(content, output):
            
                # Open file to write
                result_file = open(output, "w+b") # w+b to write in binary mode.

                # convert HTML to PDF
                pisa_status = pisa.CreatePDF(
                content,                   # the HTML to convert
                dest=result_file           # file handle to recieve result
                )           

                # close output file
                result_file.close()

                result = pisa_status.err

                if not result:
                    print("Successfully created PDF")
                else:
                    print("Error: unable to create the PDF")    

                # return False on success and True on errors
                return result



            def from_template(template, output):
   
                # Reading our template
                source_html = open(template, "r")
                content = source_html.read() # the HTML to convert
                source_html.close() # close template file

                html_to_pdf(content, output)
    
            from_template(TEMPLATE_FILE, OUTPUT_FILENAME)
            
            name=user_hashed
            name=name.replace("/","$$$") 
            
            #INPUT_FILENAME = app.config['UPLOAD_FOLDER'] + "/" + name + ".pdf"
            #OUTPUT_TEMPLATE = '/iolcloud/' + name + ".pdf"
            
            access_token = 'cnX-updmdekAAAAAAAAAASkEbkYdKaLrD3o7Z7Pc7C7o7dPFnPzZmikuNdXxJI1J'
            
            dbx = dropbox.Dropbox(access_token)
            found_template_data = db.session.query(TemplateData).filter_by(user_id=(user_hashed)).all()
            for row in found_template_data:
                
                TemplateData.query.delete()
                db.session.commit()
            
            
                
                
            transferData = TransferData(access_token)   
            file_from = app.config['UPLOAD_FOLDER'] + "/" + name + ".pdf" # This is name of the file to be uploaded
            file_to = "/iolcloud/" + name + ".pdf"  # This is the full path to upload the file to, including name that you wish the file to be called once uploaded.
            print(file_from)
            print(file_to)
            
            """if found_template_data:    
                dbx.files_delete_v2("/iolcloud/" + name + ".pdf")
                transferData.upload_file(file_from, file_to)
            else:
                transferData.upload_file(file_from, file_to)"""
            # dbx.files_upload(data, '/file.py', mode=dropbox.files.WriteMode.overwrite)
            #transferData.files_upload(file_from, file_to, mode=dropbox.files.WriteMode.overwrite)
            #dbx.upload_file(file_from, file_to, mode=dropbox.files.WriteMode.overwrite)
            try:
                dbx.files_delete_v2("/iolcloud/" + name + ".pdf")
                transferData.upload_file(file_from, file_to)
            except:
                transferData.upload_file(file_from, file_to)
                
                    
            
            result = dbx.files_get_temporary_link(file_to)
            print(result.link)
            
            new_template = TemplateData(user_hashed, result.link)
            db.session.add(new_template)
            db.session.commit()           
            found_template_data = db.session.query(TemplateData).filter_by(user_id=(user_hashed)).first()
            
            return render_template('invoice-html.html', user=current_user, invoice_data=found_invoice_data, items_data=found_invoice_items, invoice_values=found_invoice_values, profile_data=found_profile_data, image_data=found_image_data, template_data=found_template_data)   
               
        
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
