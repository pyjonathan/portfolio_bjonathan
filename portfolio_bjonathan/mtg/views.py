from flask import render_template, request, Blueprint, redirect, url_for, flash, session, abort
from flask_login import login_user, current_user, logout_user, login_required
from portfolio_bjonathan.models import MagicSet, MagicCard, OwnedCard, User, CardValue, LastFullUpdate, AuthToken
from portfolio_bjonathan import db
from .constants import *
from .helper import *
from .forms import *
from datetime import datetime
from datetime import timedelta
import requests
import locale
import functools

locale.setlocale( locale.LC_ALL, '' )

def check_auth_token(f):
    @functools.wraps(f)
    def decorated_function():

        #locale.setlocale( locale.LC_ALL, 'en-US.utf8' )

        auth_token = AuthToken.query.first()
        format = '%a, %d %b %Y %H:%M:%S %Z'

        if auth_token == None:
            r = get_token()
            r = r.json()

            new_auth_token = AuthToken(
                token = r['access_token'],
                expiration_date = r['.expires']
            )

            db.session.add(new_auth_token)
            db.session.commit()
            return f()
            
        elif datetime.strptime(auth_token.expiration_date, format) <= datetime.today():
            db.session.delete(auth_token)

            r = get_token()
            r = r.json()

            new_auth_token = AuthToken(
                token = r['access_token'],
                expiration_date = r['.expires']
            )

            db.session.add(new_auth_token)
            db.session.commit()
            return f()
        return f()

    return decorated_function

mtg = Blueprint('mtg', __name__)

@mtg.route('/mtg', methods=['GET', 'POST'])
@login_required
@check_auth_token
def main():

    from datetime import datetime
    from datetime import timedelta
    import locale
    #locale.setlocale( locale.LC_ALL, 'en-US.utf8' )

    last_full_update = LastFullUpdate.query.first()
    format = '%Y-%m-%d %H:%M:%S.%f'
    last_full_update_string = datetime.strptime(last_full_update.last_push, format)
    if last_full_update_string + timedelta(hours = 48) < datetime.today():
        update_card_values = True
    else:
        update_card_values = False

    user = current_user.username

    ### FORMS ###
    # user add
    form_user_add = AddCardsToUserCollection()
    form_user_add.set_name.choices = get_set_choices()
    form_user_add.set_name.choices.insert(0, ('', ''))

    # user remove
    form_user_remove = RemoveCardsFromUserCollection()
    form_user_remove.set_name.choices = get_users_sets(current_user.username)
    form_user_remove.set_name.choices.insert(0, ('', ''))
    #############
    
    if form_user_add.submit_add.data and form_user_add.validate_on_submit():
        user_selection = form_user_add.set_name.data
        if MagicCard.query.filter(MagicCard.group_id == user_selection).first() == None:
            for page in get_card_list(URL_PREFIX, HEADERS, PAYLOAD, user_selection):
                card_information = get_card_details(page)
                add_cards_to_database(card_information)
            rarity_choices = []
            rarity_form_values = [(form_user_add.mythic_rare, 'M'), 
                                  (form_user_add.rare, 'R'), 
                                  (form_user_add.uncommon, 'U'), 
                                  (form_user_add.common, 'C'),
                                  (form_user_add.land, 'L'),
                                  (form_user_add.token, 'T'),
                                  (form_user_add.promo, 'P'),
                                  (form_user_add.special, 'S')]
            for rarity in rarity_form_values:
                if rarity[0].data == True:
                    rarity_choices.append(rarity[1])
            if len(rarity_choices) == 0:
                flash('Please select at least one rarity.', 'rarity_choice')
                return redirect(url_for('mtg.main'))
            session['rarity_choices'] = rarity_choices
            return redirect(url_for('mtg.card_list_add', set_id = user_selection))

        else:
            rarity_choices = []
            rarity_form_values = [(form_user_add.mythic_rare, 'M'), 
                                  (form_user_add.rare, 'R'), 
                                  (form_user_add.uncommon, 'U'), 
                                  (form_user_add.common, 'C'),
                                  (form_user_add.land, 'L'),
                                  (form_user_add.token, 'T'),
                                  (form_user_add.promo, 'P'),
                                  (form_user_add.special, 'S')]
            for rarity in rarity_form_values:
                if rarity[0].data == True:
                    rarity_choices.append(rarity[1])
            if len(rarity_choices) == 0:
                flash('Please select at least one rarity.', 'rarity_choice')
                return redirect(url_for('mtg.main'))
            session['rarity_choices'] = rarity_choices
            return redirect(url_for('mtg.card_list_add', set_id = user_selection))

    if form_user_remove.submit_remove.data and form_user_remove.validate_on_submit():
        
        user_selection = form_user_remove.set_name.data
        rarity_choices = []
        rarity_form_values = [(form_user_remove.mythic_rare_remove, 'M'), 
                              (form_user_remove.rare_remove, 'R'), 
                              (form_user_remove.uncommon_remove, 'U'), 
                              (form_user_remove.common_remove, 'C'),
                              (form_user_remove.land_remove, 'L'),
                              (form_user_remove.token_remove, 'T'),
                              (form_user_remove.promo_remove, 'P'),
                              (form_user_remove.special_remove, 'S')]
        for rarity in rarity_form_values:
            if rarity[0].data == True:
                rarity_choices.append(rarity[1])
        if len(rarity_choices) == 0:
            flash('Please select at least one rarity.', 'rarity_choice')
            return redirect(url_for('mtg.main'))

        session['rarity_choices'] = rarity_choices        
        
        return redirect(url_for('mtg.card_list_remove', set_id = user_selection))

    return render_template('mtg/main.html', form_user_add = form_user_add, form_user_remove = form_user_remove, user = user, update_card_values = update_card_values)


@mtg.route('/mtg/update-mtg-sets')
@login_required
@check_auth_token
def update_mtg_sets():

    current_number_of_sets = len(MagicSet.query.all())

    for page in get_sets(URL_PREFIX, HEADERS, PAYLOAD):
        set_information = get_set_details(page)
        add_sets_to_database(set_information)

    new_number_of_sets = len(MagicSet.query.all())

    number_of_sets_added = new_number_of_sets - current_number_of_sets

    flash(f"{str(number_of_sets_added)} set(s) added to the database.", 'successful_set_database_update')

    return redirect(url_for('mtg.main'))


@mtg.route('/mtg/add-cards-to-collection',  methods=['GET', 'POST'])
@login_required
def add_cards_to_collection():

    form = AddCardsToCollection()

    form.set_name.choices = get_set_choices()

    if form.validate_on_submit():
        return redirect(url_for('mtg.card_list', set_id = form.set_name.data))

    return render_template('mtg/add_cards_to_collection.html', form = form)


@mtg.route('/mtg/card-list/<set_id>/add',  methods=['GET', 'POST'])
@login_required
def card_list_add(set_id):

    form = SaveCardsToUserCollection()

    group_id = str(set_id)
    rarity_choices = session['rarity_choices']
    magic_set = MagicSet.query.filter(MagicSet.group_id == set_id).first()

    full_card_list = db.session.query(MagicCard).join(MagicSet, MagicCard.group_id == MagicSet.group_id)\
                                                .filter(MagicCard.group_id == group_id)\
                                                .filter(MagicCard.rarity.in_(rarity_choices)).all()

    card_list_attributes = []
    for card in full_card_list:
        temp_list = []
        temp_list.append(card.rarity)
        temp_list.append(card.clean_name)
        temp_list.append(card.image_url)
        temp_list.append(card.product_id)
        temp_list.append(group_id)

        card_list_attributes.append(temp_list)
    
    card_list_attributes.sort(key = lambda card_list_attributes: card_list_attributes[1])

    if form.validate_on_submit():

        product_ids = request.form.getlist('product_id')
        quantity_regular = request.form.getlist('quantity_regular')
        quantity_foil = request.form.getlist('quantity_foil')

        count = 0
        owned_card_list = []
        for product_id in product_ids:
            temp_list = []
            if int(quantity_regular[count]) != 0 or int(quantity_foil[count]) != 0:
                temp_list.append(product_id)
                temp_list.append(quantity_regular[count])
                temp_list.append(quantity_foil[count])
                owned_card_list.append(temp_list)
            count += 1

        for owned_card in owned_card_list:
            magic_card = MagicCard.query.filter(MagicCard.product_id == owned_card[0]).first()
            owned_card.append(magic_card.clean_name)
            owned_card.append(magic_card.group_id)
    
        
        for card in owned_card_list:
            if OwnedCard.query.filter(OwnedCard.product_id == card[0]).filter(OwnedCard.owner == current_user.username).first():
                already_owned_card = OwnedCard.query.filter(OwnedCard.product_id == card[0]).first()
                already_owned_card_quantity_regular = int(already_owned_card.quantity_regular)
                already_owned_card_quantity_foil = int(already_owned_card.quantity_foil)
                already_owned_card.quantity_regular = str(already_owned_card_quantity_regular + int(card[1]))
                already_owned_card.quantity_foil = str(already_owned_card_quantity_foil + int(card[2]))
            else:
                new_owned_card = OwnedCard(
                    owner = current_user.username,
                    clean_name = card[3],
                    product_id = card[0],
                    group_id = card[4],
                    quantity_regular = card[1],
                    quantity_foil = card[2]
                )

                db.session.add(new_owned_card)
        
        db.session.commit()
        #locale.setlocale( locale.LC_ALL, 'en-US.utf8' )

        format = '%Y-%m-%d %H:%M:%S.%f'
        for card in owned_card_list:
            product_id = card[0]
            owned_card_to_price = update_card_values_by_product_id(card[0])

            if owned_card_to_price != None:
                last_update = datetime.strptime(owned_card_to_price.last_update, format)
                if last_update + timedelta(hours = 24) < datetime.today():
                    r = get_card_value(PRICING_PREFIX, HEADERS, PAYLOAD, product_id)
                    if r['results'][0]['subTypeName'] == 'Normal':
                        value_regular = str(r['results'][0]['marketPrice'])
                        value_foil = str(r['results'][1]['marketPrice'])
                    else:
                        value_regular = str(r['results'][1]['marketPrice'])
                        value_foil = str(r['results'][0]['marketPrice'])

                    owned_card_to_price.value_regular = value_regular
                    owned_card_to_price.value_foil = value_foil
                    owned_card_to_price.last_update = datetime.today()        
                    db.session.commit()
            else:
                r = get_card_value(PRICING_PREFIX, HEADERS, PAYLOAD, product_id)
                if r['results'][0]['subTypeName'] == 'Normal':
                    value_regular = str(r['results'][0]['marketPrice'])
                    value_foil = str(r['results'][1]['marketPrice'])
                else:
                    value_regular = str(r['results'][1]['marketPrice'])
                    value_foil = str(r['results'][0]['marketPrice'])

                card_value = CardValue(
                    product_id = product_id,
                    value_regular = value_regular,
                    value_foil = value_foil,
                    last_update = datetime.today()
                )

                db.session.add(card_value)
                db.session.commit()

        return redirect(url_for('mtg.main'))

    return render_template('mtg/card_list_add.html', card_list_attributes = card_list_attributes,
                                                 form = form)


@mtg.route('/mtg/card-list/<set_id>/remove',  methods=['GET', 'POST'])
@login_required
def card_list_remove(set_id):

    form = SaveRemovedCardsFromUserCollection()

    group_id = str(set_id)
    rarity_choices = session['rarity_choices']
    user_owned_card_list_in_set = db.session.query(MagicCard).join(OwnedCard, MagicCard.product_id == OwnedCard.product_id)\
                                                             .filter(OwnedCard.owner == current_user.username)\
                                                             .filter(MagicCard.group_id == group_id)\
                                                             .filter(MagicCard.rarity.in_(rarity_choices)).all()

    card_list_attributes = []
    for card in user_owned_card_list_in_set:
        temp_list = []
        temp_list.append(card.rarity)
        temp_list.append(card.clean_name)
        temp_list.append(card.image_url)
        temp_list.append(card.product_id)
        temp_list.append(group_id)
        matching_card = OwnedCard.query.filter(OwnedCard.product_id == card.product_id).filter(OwnedCard.owner == current_user.username).first()
        temp_list.append(matching_card.quantity_regular)
        temp_list.append(matching_card.quantity_foil)
        card_list_attributes.append(temp_list)

    if form.validate_on_submit():

        product_ids = request.form.getlist('product_id')
        quantity_regular = request.form.getlist('quantity_regular')
        quantity_foil = request.form.getlist('quantity_foil')

        count = 0
        owned_card_list = []
        for product_id in product_ids:
            temp_list = []
            temp_list.append(product_id)
            temp_list.append(quantity_regular[count])
            temp_list.append(quantity_foil[count])
            owned_card_list.append(temp_list)
            count += 1

        for owned_card in owned_card_list:
            if int(owned_card[1]) == 0 and int(owned_card[2]) == 0:
                removed_magic_card = OwnedCard.query.filter(OwnedCard.product_id == owned_card[0]).first()
                db.session.delete(removed_magic_card)
                db.session.commit()
            else:
                removed_magic_card = OwnedCard.query.filter(OwnedCard.product_id == owned_card[0]).first()
                if int(owned_card[1]) < int(removed_magic_card.quantity_regular):
                    removed_magic_card.quantity_regular = owned_card[1]
                if int(owned_card[2]) < int(removed_magic_card.quantity_foil):
                    removed_magic_card.quantity_foil = owned_card[2]
                db.session.commit()

        return redirect(url_for('mtg.main'))

    return render_template('mtg/card_list_remove.html', card_list_attributes = card_list_attributes, form = form)


@mtg.route('/mtg/user-collection/<user>', methods = ['GET', 'POST'])
@mtg.route('/mtg/user-collection/<user>/<group_id>', methods = ['GET', 'POST'])
def user_collection(user,group_id = 'overview'):

    form = ViewDifferentSet()
    form.set_name.choices = get_users_sets(user)
    form.set_name.choices.insert(0, ('overview', 'Full Collection'))
    form.set_name.choices.insert(0, ('', ''))

    if group_id == 'overview':
        set_name = 'Full Collection Overview'

        mythic_rare_list = get_values_by_product_id(user, 'M')
        mythic_rare_values_list = get_total_values(mythic_rare_list)

        rare_list = get_values_by_product_id(user, 'R')
        rare_values_list = get_total_values(rare_list)

        uncommon_list = get_values_by_product_id(user, 'U')
        uncommon_values_list = get_total_values(uncommon_list)

        common_list = get_values_by_product_id(user, 'C')
        common_values_list = get_total_values(common_list)

        land_list = get_values_by_product_id(user, 'L')
        land_values_list = get_total_values(land_list)

        token_list = get_values_by_product_id(user, 'T')
        token_values_list = get_total_values(token_list)

        special_list = get_values_by_product_id(user, 'S')
        special_values_list = get_total_values(special_list)

        promo_list = get_values_by_product_id(user, 'P')
        promo_values_list = get_total_values(promo_list)

        total_value = mythic_rare_values_list[2]\
                    + rare_values_list[2]\
                    + common_values_list[2]\
                    + uncommon_values_list[2]\
                    + land_values_list[2]\
                    + token_values_list[2]\
                    + special_values_list[2]\
                    + promo_values_list[2]
        total_value = locale.currency(total_value, grouping = True)

        total_foil_value = mythic_rare_values_list[4]\
                    + rare_values_list[4]\
                    + common_values_list[4]\
                    + uncommon_values_list[4]\
                    + land_values_list[4]\
                    + token_values_list[4]\
                    + special_values_list[4]\
                    + promo_values_list[4]
        total_foil_value = locale.currency(total_foil_value, grouping = True)

        total_regular_value = mythic_rare_values_list[3]\
                    + rare_values_list[3]\
                    + common_values_list[3]\
                    + uncommon_values_list[3]\
                    + land_values_list[3]\
                    + token_values_list[3]\
                    + special_values_list[3]\
                    + promo_values_list[3]
        total_regular_value = locale.currency(total_regular_value, grouping = True)

        mythic_rare_card_quantities = get_total_card_quantities(mythic_rare_list)
        rare_card_quantities = get_total_card_quantities(rare_list)
        uncommon_card_quantities = get_total_card_quantities(uncommon_list)
        common_card_quantities = get_total_card_quantities(common_list)
        land_card_quantities = get_total_card_quantities(land_list)
        token_card_quantities = get_total_card_quantities(token_list)
        special_card_quantities = get_total_card_quantities(special_list)
        promo_card_quantities = get_total_card_quantities(promo_list)
        
        total_cards = mythic_rare_card_quantities[2]\
                            + rare_card_quantities[2]\
                            + common_card_quantities[2]\
                            + uncommon_card_quantities[2]\
                            + land_card_quantities[2]\
                            + token_card_quantities[2]\
                            + special_card_quantities[2]\
                            + promo_card_quantities[2]

        total_foil_cards = mythic_rare_card_quantities[1]\
                            + rare_card_quantities[1]\
                            + common_card_quantities[1]\
                            + uncommon_card_quantities[1]\
                            + land_card_quantities[1]\
                            + token_card_quantities[1]\
                            + special_card_quantities[1]\
                            + promo_card_quantities[1]

        total_regular_cards = mythic_rare_card_quantities[0]\
                            + rare_card_quantities[0]\
                            + common_card_quantities[0]\
                            + uncommon_card_quantities[0]\
                            + land_card_quantities[0]\
                            + token_card_quantities[0]\
                            + special_card_quantities[0]\
                            + promo_card_quantities[0]
        card_list_attributes = ''
        
    else:
        if MagicSet.query.filter(MagicSet.group_id == group_id).first() != None:
            set_name = MagicSet.query.filter(MagicSet.group_id == group_id).first()
            set_name = set_name.name

            mythic_rare_list = get_values_by_rarity_and_group_id(user, 'M', group_id)
            mythic_rare_values_list = get_total_values(mythic_rare_list)

            rare_list = get_values_by_rarity_and_group_id(user, 'R', group_id)
            rare_values_list = get_total_values(rare_list)

            uncommon_list = get_values_by_rarity_and_group_id(user, 'U', group_id)
            uncommon_values_list = get_total_values(uncommon_list)

            common_list = get_values_by_rarity_and_group_id(user, 'C', group_id)
            common_values_list = get_total_values(common_list)
            
            land_list = get_values_by_rarity_and_group_id(user, 'L', group_id)
            land_values_list = get_total_values(land_list)

            token_list = get_values_by_rarity_and_group_id(user, 'T', group_id)
            token_values_list = get_total_values(token_list)

            special_list = get_values_by_rarity_and_group_id(user, 'S', group_id)
            special_values_list = get_total_values(special_list)

            promo_list = get_values_by_rarity_and_group_id(user, 'P', group_id)
            promo_values_list = get_total_values(promo_list)
            
            total_value = mythic_rare_values_list[2]\
                        + rare_values_list[2]\
                        + common_values_list[2]\
                        + uncommon_values_list[2]\
                        + land_values_list[2]\
                        + token_values_list[2]\
                        + special_values_list[2]\
                        + promo_values_list[2]
            total_value = locale.currency(total_value, grouping = True)

            total_foil_value = mythic_rare_values_list[4]\
                        + rare_values_list[4]\
                        + common_values_list[4]\
                        + uncommon_values_list[4]\
                        + land_values_list[4]\
                        + token_values_list[4]\
                        + special_values_list[4]\
                        + promo_values_list[4]
            total_foil_value = locale.currency(total_foil_value, grouping = True)

            total_regular_value = mythic_rare_values_list[3]\
                        + rare_values_list[3]\
                        + common_values_list[3]\
                        + uncommon_values_list[3]\
                        + land_values_list[3]\
                        + token_values_list[3]\
                        + special_values_list[3]\
                        + promo_values_list[3]
            total_regular_value = locale.currency(total_regular_value, grouping = True)

            mythic_rare_card_quantities = get_total_card_quantities(mythic_rare_list)
            rare_card_quantities = get_total_card_quantities(rare_list)
            uncommon_card_quantities = get_total_card_quantities(uncommon_list)
            common_card_quantities = get_total_card_quantities(common_list)
            land_card_quantities = get_total_card_quantities(land_list)
            token_card_quantities = get_total_card_quantities(token_list)
            special_card_quantities = get_total_card_quantities(special_list)
            promo_card_quantities = get_total_card_quantities(promo_list)
            
            total_cards = mythic_rare_card_quantities[2]\
                                + rare_card_quantities[2]\
                                + common_card_quantities[2]\
                                + uncommon_card_quantities[2]\
                                + land_card_quantities[2]\
                                + token_card_quantities[2]\
                                + special_card_quantities[2]\
                                + promo_card_quantities[2]


            total_foil_cards = mythic_rare_card_quantities[1]\
                                + rare_card_quantities[1]\
                                + common_card_quantities[1]\
                                + uncommon_card_quantities[1]\
                                + land_card_quantities[1]\
                                + token_card_quantities[1]\
                                + special_card_quantities[1]\
                                + promo_card_quantities[1]

            total_regular_cards = mythic_rare_card_quantities[0]\
                                + rare_card_quantities[0]\
                                + common_card_quantities[0]\
                                + uncommon_card_quantities[0]\
                                + land_card_quantities[0]\
                                + token_card_quantities[0]\
                                + special_card_quantities[0]\
                                + promo_card_quantities[0]

            user_owned_card_list_in_set = db.session.query(MagicCard).join(OwnedCard, MagicCard.product_id == OwnedCard.product_id)\
                                                                        .filter(OwnedCard.owner == user)\
                                                                        .filter(MagicCard.group_id == group_id).all()

            card_list_attributes = []
            for card in user_owned_card_list_in_set:
                temp_list = []
                temp_list.append(card.rarity)
                temp_list.append(card.clean_name)
                temp_list.append(card.image_url)
                temp_list.append(card.tgc_url)
                temp_list.append(card.product_id)
                temp_list.append(group_id)
                matching_card = OwnedCard.query.filter(OwnedCard.product_id == card.product_id).filter(OwnedCard.owner == user).first()
                temp_list.append(matching_card.quantity_regular)
                temp_list.append(matching_card.quantity_foil)
                card_list_attributes.append(temp_list)
            
            for card in card_list_attributes:
                card_value = CardValue.query.filter(CardValue.product_id == card[4]).first()
                if card_value.value_regular != 'None':
                    total_value_regular = int(card[6]) * float(card_value.value_regular)
                    total_value_regular = locale.currency(total_value_regular, grouping = True)
                else:
                    total_value_regular = ''
                
                if card_value.value_foil != 'None':
                    total_value_foil = int(card[7]) * float(card_value.value_foil)
                    total_value_foil = locale.currency(total_value_foil, grouping = True)
                else:
                    total_value_foil = ''

                if card_value.value_regular != 'None':
                    single_value_regular = float(card_value.value_regular)
                    single_value_regular = locale.currency(single_value_regular, grouping = True)
                else:
                    single_value_regular = 'N/a'

                if card_value.value_foil != 'None':
                    single_value_foil = float(card_value.value_foil)
                    single_value_foil = locale.currency(single_value_foil, grouping = True)
                else:
                    single_value_foil = 'N/a'

                card.append(single_value_regular)
                card.append(single_value_foil)
                card.append(total_value_regular)
                card.append(total_value_foil)   

            card_list_attributes.sort(key = lambda card_list_attributes: card_list_attributes[1])

        else:
            print('Not Found')

    if not User.query.filter(User.username == user).first():
        abort(404)

    if form.validate_on_submit():
        set_name = form.set_name.data
        return redirect(url_for('mtg.user_collection', user=user, group_id = set_name))

    return render_template('mtg/user_collection.html', user = user,
                                                       form = form,
                                                       set_name = set_name,
                                                       mythic_rare_values_list = mythic_rare_values_list,
                                                       rare_values_list = rare_values_list,
                                                       uncommon_values_list = uncommon_values_list,
                                                       common_values_list = common_values_list,
                                                       total_value = total_value,
                                                       mythic_rare_card_quantities = mythic_rare_card_quantities,
                                                       rare_card_quantities = rare_card_quantities,
                                                       uncommon_card_quantities = uncommon_card_quantities,
                                                       common_card_quantities = common_card_quantities,
                                                       total_cards = total_cards,
                                                       total_foil_cards = total_foil_cards,
                                                       total_regular_cards = total_regular_cards,
                                                       total_foil_value = total_foil_value,
                                                       total_regular_value = total_regular_value,
                                                       card_list_attributes = card_list_attributes) 


@mtg.route('/mtg/full-card-value-update',  methods=['GET', 'POST'])
@login_required
@check_auth_token
def full_card_value_update():

###  THIS IS COMMENTED OUT IN THE DEMO VERSION  ###

#     locale.setlocale( locale.LC_ALL, 'en-US.utf8' )

#     last_full_update = LastFullUpdate.query.first()
#     format = '%Y-%m-%d %H:%M:%S.%f'
#     last_full_update = datetime.strptime(last_full_update.last_push, format)
#     if last_full_update + timedelta(hours = 48) < datetime.today():
#         magic_cards = CardValue.query.all()
#         for card in magic_cards:
#             db_last_update = datetime.strptime(card.last_update, format)
#             if db_last_update + timedelta(hours = 24) < datetime.today():
#                 r = get_card_value(PRICING_PREFIX, HEADERS, PAYLOAD, card.product_id)
#                 if r['results'][0]['subTypeName'] == 'Normal':
#                     value_regular = str(r['results'][0]['marketPrice'])
#                     value_foil = str(r['results'][1]['marketPrice'])
#                 else:
#                     value_regular = str(r['results'][1]['marketPrice'])
#                     value_foil = str(r['results'][0]['marketPrice'])
#                 card.value_regular = value_regular
#                 card.value_foil = value_foil
#                 card.last_update = datetime.today()        
#                 db.session.commit()
#         last_push = LastFullUpdate.query.first()
#         last_push.last_push = datetime.today()
#         db.session.commit()

    return redirect(url_for('mtg.main'))

