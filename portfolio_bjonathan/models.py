from portfolio_bjonathan import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import locale

locale.setlocale( locale.LC_ALL, 'en-US' )

###########################################################
##################   USER MANAGEMENT   ####################
###########################################################

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):

    __bind_key__ = 'portfolio_users'

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique = True, index = True)
    password_hash = db.Column(db.String(128))

    def __init__(self, username, password):
        self.username = username
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash,password)

    def __repr__(self):
        return f"Username: {self.username}"



###########################################################
#############   REMODEL EXPENSE TRACKER   #################
###########################################################

class Contractor(db.Model):

    __bind_key__ = 'portfolio_rmet'

    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(64), index = True)
    last_name = db.Column(db.String(64), index = True)
    rate = db.Column(db.String(), index = True)
    hours_worked = db.Column(db.String(), index = True)
    total_comp = db.Column(db.String(), index = True)

    def __init__(self, first_name = "", last_name = "", rate = "", hours_worked = "", total_comp = ""):
        self.first_name = first_name
        self.last_name = last_name
        self.rate = rate
        self.hours_worked = hours_worked
        self.total_comp = total_comp

    def get_labor_cost(self):
        labor_cost = float(self.rate) * float(self.hours_worked)
        labor_cost = locale.currency( labor_cost, grouping = True)
        labor_list = [self.first_name, self.hours_worked, labor_cost]
        return labor_list

    def get_total_labor_cost(self):
        total_labor = float(self.rate) *  float(self.hours_worked)
        return total_labor
    
    def __repr__(self):
        return f"{self.first_name} {self.last_name}"

class Material(db.Model):

    __bind_key__ = 'portfolio_rmet'

    id = db.Column(db.Integer, primary_key = True)
    item_name = db.Column(db.String(128), index = True)
    quantity = db.Column(db.String(), index = True)
    cost = db.Column(db.String(), index = True)
    total_cost = db.Column(db.String(), index = True)

    def __init__(self, item_name = "", catagory = "", quantity = "", cost = "", total_cost = ""):
        self.item_name = item_name
        self.catagory = catagory
        self.quantity = quantity
        self.cost = cost
        self.total_cost = total_cost

    def __repr__(self):
        return f"{self.item_name}"

###########################################################
#############   MTG COLLECTOR AND PRICE   #################
###########################################################

class MagicSet(db.Model):
    __bind_key__ = 'portfolio_mtg'
    id = db.Column(db.Integer, primary_key = True)
    group_id = db.Column(db.String(), index = True)
    name = db.Column(db.String(), index = True)
    abbreviation = db.Column(db.String(), index = True)
    is_supplemental = db.Column(db.Boolean())
    published_on = db.Column(db.String())
    modified_on = db.Column(db.String())
    category_id = db.Column(db.String())

    def __init__(self, group_id = '', name = '', abbreviation = '', is_supplemental = '', published_on = '', modified_on = '', category_id = ''):
        self.group_id = group_id
        self.name = name
        self.abbreviation = abbreviation
        self.is_supplemental = is_supplemental
        self.published_on = published_on
        self.modified_on = modified_on
        self.category_id = category_id

    def __repr__(self):
        return f"{self.name}" 

class MagicCard(db.Model):
    __bind_key__ = 'portfolio_mtg'
    id = db.Column(db.Integer(), primary_key = True)
    product_id = db.Column(db.String(), index = True)
    name = db.Column(db.String(), index = True)
    clean_name = db.Column(db.String(), index = True)
    image_url = db.Column(db.String())
    category_id = db.Column(db.String())
    group_id = db.Column(db.String())
    tgc_url = db.Column(db.String())
    modified_on = db.Column(db.String())
    rarity = db.Column(db.String())

    def __init__(self, product_id = '', name = '', clean_name = '', image_url = '', category_id = '', group_id = '', tgc_url = '', modified_on = '', rarity = '', card_number = ''):
        self.product_id = product_id
        self.name = name
        self.clean_name = clean_name
        self.image_url = image_url
        self.category_id = category_id
        self.group_id = group_id
        self.tgc_url = tgc_url
        self.modified_on = modified_on
        self.rarity = rarity        

    def __repr__(self):
        return f"{self.name}"

class OwnedCard(db.Model):
    __bind_key__ = 'portfolio_mtg'
    id = db.Column(db.Integer(), primary_key = True)
    owner = db.Column(db.String())
    clean_name = db.Column(db.String())
    product_id = db.Column(db.String())
    group_id = db.Column(db.String())
    quantity_regular = db.Column(db.String())
    quantity_foil = db.Column(db.String())

    def __init__(self, owner = '', clean_name = '', product_id = '', group_id = '', quantity_regular = '', quantity_foil = ''):
        self.owner = owner
        self.clean_name = clean_name
        self.product_id = product_id
        self.group_id = group_id
        self.quantity_regular = quantity_regular
        self.quantity_foil = quantity_foil

    def __repr__(self):
        return f"{self.clean_name}"

class CardValue(db.Model):
    __bind_key__ = 'portfolio_mtg'
    id = db.Column(db.Integer(), primary_key = True)
    product_id = db.Column(db.String())
    value_regular = db.Column(db.String())
    value_foil = db.Column(db.String())
    last_update = db.Column(db.String())

    def __init__(self, product_id = '', value_regular = '', value_foil = '', last_update = ''):
        self.product_id = product_id
        self.value_regular = value_regular
        self.value_foil = value_foil
        self.last_update = last_update

    def __repr__(self):
        return f"{self.product_id}"


class LastFullUpdate(db.Model):
    __bind_key__ = 'portfolio_mtg'
    id = db.Column(db.Integer(), primary_key = True)
    last_push = db.Column(db.String())

    def __init__(self, last_push = ''):
        self.last_push = last_push


    def __repr__(self):
        return f"{self.last_push}"

class AuthToken(db.Model):
    __bind_key__ = 'portfolio_mtg'
    id = db.Column(db.Integer(), primary_key = True)
    token = db.Column(db.String())
    expiration_date = db.Column(db.String())

    def __init__(self, token = '', expiration_date = ''):
        self.token = token
        self.expiration_date = expiration_date

