from portfolio_bjonathan.models import MagicSet, MagicCard, OwnedCard, CardValue
from portfolio_bjonathan import db
from .constants import *
import requests
import json
import math
import locale

locale.setlocale( locale.LC_ALL, '' )

def get_token():
    url = "https://api.tcgplayer.com/token"

    payload="grant_type=client_credentials&client_id=ed6044e3-5994-47af-ad45-fdd78276c2e6&client_secret=aa14beb5-9c08-422f-b011-a174fa98d030"
    headers = {
        'Content-Type': 'application/json',
        }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response


### (API) RETRIEVES THE VALUE OF A CARD BY product_id
def get_card_value(PRICING_PREFIX, HEADERS, PAYLOAD, product_id):
    URL = f"{PRICING_PREFIX}/{product_id}"
    r = requests.request("GET", URL, headers = HEADERS, data = PAYLOAD).json()
    return r

### (API) GETS A LIST OF ALL MTG SETS
def get_sets(URL_PREFIX, HEADERS, PAYLOAD):
    URL = f"{URL_PREFIX}/categories/1/groups"
    PARAMS = {'limit': 1000}
    first_page = requests.request("GET", URL, headers=HEADERS, data = PAYLOAD, params = PARAMS).json()
    yield first_page
    response_length = first_page['totalItems']
    number_of_pages = math.ceil(response_length / 100)

    index = 1
    for page in range(2, number_of_pages + 1):        
        offset = index * 100
        next_page = requests.request("GET", URL, headers=HEADERS, data = PAYLOAD, params = {'offset': offset, 'limit': 100 })
        next_page = next_page.json()
        index = index + 1
        yield next_page

### (API) GETS THE DETAILS OF THE RETRIEVED SETS (MAX RETURN LIMIT WITH THE API IS 100 AS IT IS PAGINATED)
def get_set_details(page):
    set_information = []
    for item in page['results']:
        group_id = item['groupId']
        name = item['name']
        abbreviation = item['abbreviation']
        is_supplemental = item['isSupplemental']
        published_on = item['publishedOn']
        modified_on = item['modifiedOn']
        category_id = item['categoryId']

        temp_list = []
        temp_list.append(group_id)
        temp_list.append(name)
        temp_list.append(abbreviation)
        temp_list.append(is_supplemental)
        temp_list.append(published_on)
        temp_list.append(modified_on)
        temp_list.append(category_id)
        set_information.append(temp_list)
    return set_information
        
### (DATABASE) COMMITS THE SET INFORMATION INTO THE LOCAL DATABASE
def add_sets_to_database(set_information):
    for information in set_information:
        if not MagicSet.query.filter(MagicSet.group_id == str(information[0])).first():
            magic_set = MagicSet(
                group_id = information[0],
                name = information[1],
                abbreviation = information[2],
                is_supplemental = information[3],
                published_on = information[4],
                modified_on = information[5],
                category_id = information[6]
            )

            db.session.add(magic_set)
            db.session.commit()
    return


### (API) GETS THE CARD LIST IN A SPECIFIC SET BY group_id
def get_card_list(URL_PREFIX, HEADERS, PAYLOAD, group_id):
    URL = f"{URL_PREFIX}/products"
    PARAMS = {'categoryId': CATEGORY_ID,
              'productTypes': 'cards',
              'groupId': group_id,
              'limit': 1000,
              'getExtendedFields': 'true'}
    first_page = requests.request("GET", URL, headers=HEADERS, data = PAYLOAD, params = PARAMS).json()
    yield first_page
    response_length = first_page['totalItems']
    number_of_pages = math.ceil(response_length / 100)
    index = 1
    for page in range(2, number_of_pages + 1):        
        offset = index * 100
        next_page = requests.request("GET", URL, headers=HEADERS, data = PAYLOAD, params = {'offset': offset,
                                                                                            'categoryId': 1,
                                                                                            'productTypes': 'cards',
                                                                                            'groupId': group_id,
                                                                                            'limit': 1000,
                                                                                            'getExtendedFields': 'true' })
        next_page = next_page.json()
        index = index + 1
        yield next_page

### (API) GETS THE DETAILS FOR CARD IN THE SPECIFIED SET (MAX RETURN LIMIT WITH THE API IS 100 AS IT IS PAGINATED)
def get_card_details(page):
    set_information = []
    for item in page['results']:
        product_id = item['productId']
        name = item['name']
        clean_name = item['cleanName']
        image_url = item['imageUrl']
        category_id = item['categoryId']
        group_id = item['groupId']
        tgc_url = item['url']
        modified_on = item['modifiedOn']
        rarity = item['extendedData'][0]['value']     

        temp_list = []
        temp_list.append(product_id)
        temp_list.append(name)
        temp_list.append(clean_name)
        temp_list.append(image_url)
        temp_list.append(category_id)
        temp_list.append(group_id)
        temp_list.append(tgc_url)
        temp_list.append(modified_on)
        temp_list.append(rarity)
        set_information.append(temp_list)

    return set_information


### (DATABASE) COMMITS THE CARDS AND DETAILS TO THE DATABASE
def add_cards_to_database(set_information):
    for information in set_information:
        magic_card = MagicCard(
            product_id = information[0],
            name = information[1],
            clean_name = information[2],
            image_url = information[3],
            category_id = information[4],
            group_id = information[5],
            tgc_url = information[6],
            modified_on = information[7],
            rarity = information[8],
        )

        db.session.add(magic_card)
        db.session.commit()
    return


### (GUI) RETRIEVES A LIST OF SETS IN THE DATABASE FOR DROPDOWNS
def get_set_choices():
    mtg_sets = MagicSet.query.order_by(MagicSet.name).all()
    mtg_set_group_ids = []
    for mtg_set in mtg_sets:
        mtg_set_group_ids.append(mtg_set.group_id)

    mtg_sets = MagicSet.query.filter(MagicSet.group_id.in_(mtg_set_group_ids)).all()
    choices = [(mtg_set.group_id, mtg_set.name) for mtg_set in mtg_sets]
    return (sorted(choices, key = lambda x: x[1]))

def get_users_sets(username):
    users_sets = OwnedCard.query.distinct(OwnedCard.group_id).filter(OwnedCard.owner == username).all()
    set_group_ids = []
    for user_set in users_sets:
        set_group_ids.append(user_set.group_id)
        
    users_sets = MagicSet.query.filter(MagicSet.group_id.in_(set_group_ids)).all()
    choices = [(user_set.group_id, user_set.name) for user_set in users_sets]
    return (sorted(choices, key = lambda x: x[1]))


### (DATABASE) RETRIEVES HOW MANY OF EACH RARITY A USER'S COLLECTION CONTAINS
def get_card_amounts_by_rarity_full(user):

    mythic_quantity = db.session.query(MagicCard).join(OwnedCard, MagicCard.product_id == OwnedCard.product_id)\
                                            .filter(OwnedCard.owner == user)\
                                            .filter(MagicCard.rarity == 'M').all()

    rare_quantity = db.session.query(MagicCard).join(OwnedCard, MagicCard.product_id == OwnedCard.product_id)\
                                               .filter(OwnedCard.owner == user)\
                                               .filter(MagicCard.rarity == 'R').all()

    uncommon_quantity = db.session.query(MagicCard).join(OwnedCard, MagicCard.product_id == OwnedCard.product_id)\
                                                   .filter(OwnedCard.owner == user)\
                                                   .filter(MagicCard.rarity == 'U').all()

    common_quantity = db.session.query(MagicCard).join(OwnedCard, MagicCard.product_id == OwnedCard.product_id)\
                                                 .filter(OwnedCard.owner == user)\
                                                 .filter(MagicCard.rarity == 'C').all()

    promo_quantity = db.session.query(MagicCard).join(OwnedCard, MagicCard.product_id == OwnedCard.product_id)\
                                                 .filter(OwnedCard.owner == user)\
                                                 .filter(MagicCard.rarity == 'P').all()

    land_quantity = db.session.query(MagicCard).join(OwnedCard, MagicCard.product_id == OwnedCard.product_id)\
                                                 .filter(OwnedCard.owner == user)\
                                                 .filter(MagicCard.rarity == 'L').all()

    token_quantity = db.session.query(MagicCard).join(OwnedCard, MagicCard.product_id == OwnedCard.product_id)\
                                                 .filter(OwnedCard.owner == user)\
                                                 .filter(MagicCard.rarity == 'T').all()

    special_quantity = db.session.query(MagicCard).join(OwnedCard, MagicCard.product_id == OwnedCard.product_id)\
                                                 .filter(OwnedCard.owner == user)\
                                                 .filter(MagicCard.rarity == 'S').all()

    return [len(mythic_quantity), len(rare_quantity), len(uncommon_quantity), len(common_quantity)]


### (DATABASE) RETRIEVES A CARD VALUE BY product_id
def update_card_values_by_product_id(product_id):
    card = CardValue.query.filter(CardValue.product_id == product_id).first()
    return card

def get_values_by_product_id(user, rarity):

    result = db.session.query(MagicCard, OwnedCard, CardValue).join(OwnedCard, MagicCard.product_id == OwnedCard.product_id)\
                                                              .join(CardValue, OwnedCard.product_id == CardValue.product_id)\
                                                              .filter(MagicCard.rarity == rarity)\
                                                              .filter(OwnedCard.owner == user).all()
    return result


### (DATABASE) RETRIEVES THE TOTAL VALUE OF CARDS BY RARITY (TAKES WHAT IS RETURNED FROM update_card_values_by_product_id(product_id))
def get_total_values(card_list_by_rarity):
    total_regular = 0
    total_foil = 0
    for card in card_list_by_rarity:
        if int(card[1].quantity_regular) > 0:
            if card[2].value_regular != 'None':
                total_regular_single = float(card[2].value_regular)        
                total_regular_single = total_regular_single * int(card[1].quantity_regular)
                total_regular += total_regular_single
            else:
                total_regular = 0

        if int(card[1].quantity_foil) > 0:
            if card[2].value_foil != 'None':
                total_foil_single = float(card[2].value_foil)       
                total_foil_single = total_foil_single * int(card[1].quantity_foil)
                total_foil += total_foil_single
            else:
                total_foil = 0

    total_value = total_regular + total_foil
    total_regular_value = total_regular
    total_foil_value = total_foil
    total_regular = locale.currency(total_regular, grouping = True)
    total_foil = locale.currency(total_foil, grouping = True)
    return [total_regular, total_foil, total_value, total_regular_value, total_foil_value]


### (DATABASE) RETRIEVES THE TOTAL QUANTITY OF CARDS BY TYPE (TAKES WHAT IS RETURNED FROM update_card_values_by_product_id(product_id))
def get_total_card_quantities(card_list_by_rarity):
    total_regular = 0
    total_foil = 0
    for card in card_list_by_rarity:
        total_regular += int(card[1].quantity_regular)
        total_foil += int(card[1].quantity_foil)
    total_cards = total_regular + total_foil
    return [total_regular, total_foil, total_cards]



### (DATABASE) RETRIEVES A CARD VALUE BY GROUP_ID
def get_values_by_rarity_and_group_id(user, rarity, group_id):

    result = db.session.query(MagicCard, OwnedCard, CardValue).join(OwnedCard, MagicCard.product_id == OwnedCard.product_id)\
                                                              .join(CardValue, OwnedCard.product_id == CardValue.product_id)\
                                                              .filter(MagicCard.rarity == rarity)\
                                                              .filter(MagicCard.group_id == group_id)\
                                                              .filter(OwnedCard.owner == user).all()
    return result