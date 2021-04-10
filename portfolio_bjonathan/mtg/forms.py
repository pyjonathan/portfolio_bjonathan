from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DecimalField, SelectField, IntegerField, HiddenField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Regexp, Length
from wtforms import ValidationError

###########################################################
######################    MTG FORMS     ###################
###########################################################

class AddCardsToUserCollection(FlaskForm):

    set_name = SelectField('Choose a set', validators = [DataRequired()])
    submit_add = SubmitField('Submit')
    mythic_rare = BooleanField('Mythic Rare', default = 'checked')
    rare = BooleanField('Rare', default = 'checked')
    uncommon = BooleanField('Uncommon', default = 'checked')
    common = BooleanField('Common', default = 'checked')
    land = BooleanField('Land')
    token = BooleanField('Token')
    promo = BooleanField('Promo')
    special = BooleanField('Special')


class RemoveCardsFromUserCollection(FlaskForm):

    set_name = SelectField('Choose a set', validators = [DataRequired()])
    submit_remove = SubmitField('Submit')
    mythic_rare_remove = BooleanField('Mythic Rare', default = 'checked')
    rare_remove = BooleanField('Rare', default = 'checked')
    uncommon_remove = BooleanField('Uncommon', default = 'checked')
    common_remove = BooleanField('Common', default = 'checked')
    land_remove = BooleanField('Land')
    token_remove = BooleanField('Token')
    promo_remove = BooleanField('Promo')
    special_remove = BooleanField('Special')


class SaveCardsToUserCollection(FlaskForm):

    quantity_regular = IntegerField('Qty. Regular')
    quantity_foil = IntegerField('Qty. Foil')
    product_id = HiddenField()
    submit = SubmitField('Save')


class SaveRemovedCardsFromUserCollection(FlaskForm):

    quantity_regular = IntegerField('Qty. Regular')
    quantity_foil = IntegerField('Qty. Foil')
    product_id = HiddenField()
    submit = SubmitField('Save')
    

class ViewDifferentSet(FlaskForm):

    set_name = SelectField('Choose a set', validators = [DataRequired()])
    submit = SubmitField('Submit')
    





