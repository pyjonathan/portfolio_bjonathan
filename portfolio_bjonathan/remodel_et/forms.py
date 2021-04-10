from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DecimalField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Regexp, Length
from wtforms import ValidationError

###########################################################
##################   CONTRACTOR FORMS   ###################
###########################################################

class AddContractorForm(FlaskForm):

    first_name = StringField('First Name', validators = [DataRequired()])
    last_name = StringField('Last Name', validators = [DataRequired()])
    rate = DecimalField('Rate', validators = [DataRequired()])
    submit = SubmitField('Save')

class DeleteContractorForm(FlaskForm):

    contractors = SelectField('Contractors', validators = [DataRequired()])
    submit = SubmitField('Delete Contractor')

class AddHoursForm(FlaskForm):

    contractors = SelectField('Contractors', validators = [DataRequired()])
    additional_hours = DecimalField('Additional Hours', validators = [DataRequired()])
    submit = SubmitField('Save')

class ChangeContractorRateForm(FlaskForm):
    
    contractors = SelectField('Contractors', validators = [DataRequired()])
    new_rate = DecimalField('New Rate', validators = [DataRequired()])
    submit = SubmitField('Save')

###########################################################
###################   MATERIAL FORMS   ####################
###########################################################

class AddMaterialForm(FlaskForm):

    item_name = StringField('Item Name', validators = [DataRequired()])
    quantity = DecimalField('Qty.', validators = [DataRequired()])
    cost = DecimalField('Cost', validators = [DataRequired()])
    submit = SubmitField('Save')

class DeleteMaterialForm(FlaskForm):

    item_names = SelectField('Item', validators = [DataRequired()])
    submit = SubmitField('Delete Item')

class ChangeMaterialQuantityForm(FlaskForm):

    item_names = SelectField('Item', validators = [DataRequired()])
    additional_quantity = DecimalField('Additional Qty.', validators = [DataRequired()])
    submit = SubmitField('Save')

class ChangeMaterialCostForm(FlaskForm):

    item_name = SelectField('Item', validators = [DataRequired()])
    new_cost = DecimalField('New Cost', validators = [DataRequired()])
    submit = SubmitField('Save')

class EditMaterialForm(FlaskForm):

    item_name = SelectField('Item', validators = [DataRequired()])
    submit = SubmitField('Delete Item')

