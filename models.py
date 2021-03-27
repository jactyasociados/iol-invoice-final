from app import db, ma
from datetime import datetime

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, index=True)
    user_id_hash = db.Column(db.String(255), index=True)
    password = db.Column(db.String(255))
    email = db.Column(db.String(60), unique=True, index=True)
    registered_on = db.Column(db.DateTime)

    def __init__(self, username, user_id_hash, password, email):
        self.username = username
        self.user_id_hash = user_id_hash
        self.password = password
        self.email = email
        self.registered_on = datetime.utcnow()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)

    # don't judge me...
    def unique(self):

        e_e = email_e = db.session.query(User.email).filter_by(email=self.email).scalar() is None
        u_e = username_e = db.session.query(User.username).filter_by(username=self.username).scalar() is None

        # none exist
        if e_e and u_e:
            return 0

        # email already exists
        elif e_e == False and u_e == True:
            return -1

        # username already exists
        elif e_e == True and u_e == False:
            return -2

        # both already exists
        else:
            return -3
            
        def serialize(self):
            return {
            'id': self.id, 
            'username': self.username,
            'user_id_hash': self.user_id_hash,
            'password': self.password,
            'email': self.email,
            'registered_on': self.registered_on
            }
            
class ImageData(db.Model):
    __tablename__ = "imagedata"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), index=True)
    image_name = db.Column(db.String(255))
    image_url = db.Column(db.String(255)) 
    width = db.Column(db.String(10))
    height = db.Column(db.String(10))
    
    def __init__(self, user_id, image_name, image_url, width, height):
        self.user_id = user_id
        self.image_name = image_name
        self.image_url = image_url
        self.width = width
        self.height = height
        
    def __repr__(self):
        return '<id {}>'.format(self.id)
        
    def serialize(self):
        return {
            'id': self.id, 
            'user_id': self.user_id,
            'image_name': self.image_name,
            'image_url': self.image_url,
            'width': width,
            'height': height
        }

class InvoiceData(db.Model):
    __tablename__ = "invoicedata"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), index=True)
    invoice_number = db.Column(db.String(100)) 
    businessname = db.Column(db.String(100))
    email = db.Column(db.String(150))
    ein = db.Column(db.String(100))
    address = db.Column(db.String(255))
    address2 = db.Column(db.String(255))
    city = db.Column(db.String(30))
    state = db.Column(db.String(30))
    zip = db.Column(db.String(30))
    businessname_shipping = db.Column(db.String(100))
    email_shipping = db.Column(db.String(150))
    ein_shipping = db.Column(db.String(100))
    address_shipping = db.Column(db.String(255))
    address2_shipping = db.Column(db.String(255))
    city_shipping = db.Column(db.String(30))
    state_shipping = db.Column(db.String(30))
    zip_shipping = db.Column(db.String(30))
    invoice_date = db.Column(db.Date)
    taxes = db.Column(db.String(10))
    

    def __init__(self, user_id, invoice_number, businessname, email, ein, address, address2, city, state, zip, businessname_shipping, email_shipping, ein_shipping, address_shipping, address2_shipping, city_shipping, state_shipping, zip_shipping, invoice_date, taxes):
        self.user_id = user_id
        self.invoice_number = invoice_number
        self.businessname = businessname
        self.email = email
        self.ein = ein
        self.address = address
        self.address2 = address2
        self.city = city
        self.state = state
        self.zip = zip
        self.businessname_shipping = businessname_shipping
        self.email_shipping = email_shipping
        self.ein_shipping = ein_shipping
        self.address_shipping = address_shipping
        self.address2_shipping = address2_shipping
        self.city_shipping = city_shipping
        self.state_shipping = state_shipping
        self.zip_shipping = zip_shipping
        self.invoice_date = invoice_date
        self.taxes = taxes 
        

    def __repr__(self):
        return '<id {}>'.format(self.id)
    
    def serialize(self):
        return {
            'id': self.id, 
            'user_id': self.user_id,
            'invoice_number': self.invoice_number,
            'businessname': self.businessname,
            'email': self.email,
            'ein': self.ein,
            'address': self.address,
            'address2': self.address2,
            'city': self.city,
            'state': self.state,
            'zip': self.zip,
            'businessname_shipping': self.businessname_shipping,
            'email_shipping': self.email_shipping,
            'ein_shipping': self.ein_shipping,
            'address_shipping': self.address_shipping,
            'address2_shipping': self.address2_shipping,
            'city_shipping': self.city_shipping,
            'state_shipping': self.state_shipping,
            'zip_shipping': self.zip_shipping,
            'invoice_date': self.invoice_date,
            'taxes': self.taxes
            
        }
        

            
class InvoiceItems(db.Model):
    __tablename__ = 'invoice-items'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), index=True)
    invoice_number = db.Column(db.Integer)
    item_desc = db.Column(db.String(100))
    item_price = db.Column(db.Float)
    item_quant = db.Column(db.Float)
    amount = db.Column(db.Float)
    

    def __init__(self, user_id, invoice_number, item_desc, item_price, item_quant, amount):
        self.user_id = user_id
        self.invoice_number = invoice_number
        self.item_desc = item_desc
        self.item_price = item_price
        self.item_quant = item_quant
        self.amount = amount
        

    def __repr__(self):
        return '<id {}>'.format(self.id)
    
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id, 
            'invoice_number': self.invoice_number,
            'item_desc': self.item_desc,
            'item_price': self.item_price,
            'item_quant': self.item_quant,
            'amount': self.amount
        }        
        
class InvoiceValues(db.Model):
    __tablename__ = 'invoicevalues'
	
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), index=True)
    invoice_number = db.Column(db.Integer)
    subtotal = db.Column(db.Float)
    taxes = db.Column(db.Float)
    total = db.Column(db.Float)
    
    def __init__(self, user_id, invoice_number, subtotal, taxes, total):
        self.user_id = user_id
        self.invoice_number = invoice_number
        self.subtotal = subtotal
        self.taxes = taxes
        self.total = total
 
    def __repr__(self):
        return '<id {}>'.format(self.id)
    
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id, 
            'invoice_number': self.invoice_number,
            'subtotal': self.subtotal,
            'taxes': self.taxes,
            'total': self.total
        }
        
class ProfileData(db.Model):
    __tablename__ = "profiledata"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), index=True)
    businessname = db.Column(db.String(255))
    email = db.Column(db.String(255)) 
    ein = db.Column(db.String(255))
    address1 = db.Column(db.String(255)) 
    address2 = db.Column(db.String(255)) 
    city = db.Column(db.String(255)) 
    state = db.Column(db.String(255)) 
    zip = db.Column(db.String(255)) 
    
    def __init__(self, user_id, businessname, email, ein, address1, address2, city, state, zip):
        self.user_id = user_id
        self.businessname = businessname
        self.email = email
        self.ein = ein
        self.address1 = address1
        self.address2 = address2
        self.city = city
        self.state = state
        self.zip = zip
        
    def __repr__(self):
        return '<id {}>'.format(self.id)
        
    def serialize(self):
        return {
            'id': self.id, 
            'user_id': self.user_id,
            'businessname': self.businessname,
            'email': self.email,
            'ein': self.ein,
            'address1': self.address1,
            'address2': self.address2,
            'city': self.city,
            'state': self.state,
            'zip': self.zip
        }     