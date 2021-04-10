from flask import render_template, request, Blueprint, redirect, url_for, flash, session
from flask_login import login_user, current_user, logout_user, login_required
from portfolio_bjonathan.models import Contractor, Material
from portfolio_bjonathan import db
from portfolio_bjonathan.remodel_et.forms import *
import locale
import decimal

locale.setlocale( locale.LC_ALL, 'en-US' )

remodel_et = Blueprint('remodel_et', __name__)

@remodel_et.route('/remodel-et/main')
@login_required
def main():
    contractors = Contractor.query.all()
    materials = Material.query.all()

    # total labor cost #
    total_labor_cost_list = []
    for contractor in contractors:
        total_labor_cost_list.append((decimal.Decimal(contractor.total_comp)))
    
    total_labor_cost = sum(total_labor_cost_list)
    total_labor_cost_dollars = locale.currency(total_labor_cost, grouping = True)

    # total materials cost #
    total_materials_cost_list = []
    for material in materials:
        total_materials_cost_list.append((decimal.Decimal(material.total_cost)))
    
    total_materials_cost = sum(total_materials_cost_list)
    total_materials_cost_dollars = locale.currency(total_materials_cost, grouping = True)

    # total overall cost #
    overall_cost = total_labor_cost + total_materials_cost
    overall_cost_dollars = locale.currency(overall_cost, grouping = True)    

    # contractor information #
    contractor_info = []
    for contractor in contractors:
        temp_contractor = []
        temp_contractor.append(contractor.id)
        temp_contractor.append(contractor.first_name)
        temp_contractor.append(contractor.last_name)

        # Rate decimal and currency conversion
        contractor_rate = contractor.rate
        contractor_rate = decimal.Decimal(contractor_rate)
        rate_dollars = locale.currency(contractor_rate, grouping = True)
        temp_contractor.append(rate_dollars)

        # Hours Worked decimal conversion
        contractor_hours_worked = contractor.hours_worked
        contractor_hours_worked = decimal.Decimal(contractor_hours_worked)
        temp_contractor.append(contractor_hours_worked)

        # Total Comp decimal and currency conversion
        contractor_total_comp = contractor.total_comp
        contractor_total_comp = decimal.Decimal(contractor_total_comp)
        total_comp_dollars = locale.currency(contractor_total_comp, grouping = True)
        temp_contractor.append(total_comp_dollars)

        contractor_info.append(temp_contractor)

    # materials information #
    material_info = []
    for material in materials:
        temp_material = []
        temp_material.append(material.id)
        temp_material.append(material.item_name)   
        temp_material.append(material.quantity)

        # Cost decimal and currency conversion
        material_cost = material.cost
        material_cost = decimal.Decimal(material_cost)
        cost_dollars = locale.currency(material_cost, grouping = True)
        temp_material.append(cost_dollars)

        # Total Cost decimal and currency conversion
        material_total_cost = material.total_cost
        material_total_cost = decimal.Decimal(material_total_cost)
        total_cost_dollars = locale.currency(material_total_cost)
        temp_material.append(total_cost_dollars)

        material_info.append(temp_material) 

    return render_template('remodel_et/main.html', contractor_info = contractor_info,
                                                   material_info = material_info,
                                                   total_labor_cost_dollars = total_labor_cost_dollars,
                                                   total_materials_cost_dollars = total_materials_cost_dollars,
                                                   overall_cost_dollars = overall_cost_dollars)


@remodel_et.route('/remodel-et/add-contractor', methods=['GET', 'POST'])
@login_required
def add_contractor():
    form = AddContractorForm()

    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        rate = form.rate.data

        contractor = Contractor(first_name = first_name,
                                last_name = last_name,
                                rate = rate,
                                hours_worked = '0.0',
                                total_comp = '0.0')

        db.session.add(contractor)
        db.session.commit()

        return redirect(url_for('remodel_et.main'))

    return render_template('remodel_et/add_contractor.html', form = form)


@remodel_et.route('/remodel-et/delete-contractor', methods = ['GET', 'POST'])
@login_required
def delete_contractor():

    form = DeleteContractorForm()
    form.contractors.choices = [(f"{c.id}", f"{c.first_name} {c.last_name}") for c in Contractor.query.all()]

    if form.validate_on_submit():
        contractor_to_delete = Contractor.query.filter_by(id = form.contractors.data).first()

        db.session.delete(contractor_to_delete)
        db.session.commit()

        return redirect(url_for('remodel_et.main'))

    return render_template('remodel_et/delete_contractor.html', form = form)


@remodel_et.route('/remodel-et/add-hours', methods = ['GET', 'POST'])
@login_required
def add_hours():

    form = AddHoursForm()
    form.contractors.choices = [(f"{c.id}", f"{c.first_name} {c.last_name}") for c in Contractor.query.all()]

    if form.validate_on_submit():
        contractor = Contractor.query.filter_by(id = form.contractors.data).first()
        weekly_comp = decimal.Decimal(form.additional_hours.data) * decimal.Decimal(contractor.rate)
        total_comp = str(decimal.Decimal(contractor.total_comp) + weekly_comp)
        contractor.hours_worked = str(decimal.Decimal(contractor.hours_worked) + decimal.Decimal(form.additional_hours.data))
        contractor.total_comp = total_comp

        db.session.commit()

        return redirect(url_for('remodel_et.main'))

    return render_template('remodel_et/add_hours.html', form = form)


@remodel_et.route('/remodel-et/change-rate', methods = ['GET', 'POST'])
@login_required
def change_rate():

    form = ChangeContractorRateForm()
    form.contractors.choices = [(f"{c.id}", f"{c.first_name} {c.last_name}") for c in Contractor.query.all()]

    if form.validate_on_submit():
        contractor = Contractor.query.filter_by(id = form.contractors.data).first()
        contractor.rate = form.new_rate.data

        db.session.commit()

        return redirect(url_for('remodel_et.main'))

    return render_template('remodel_et/change_rate.html', form = form)

# MATERIALS #

@remodel_et.route('/remodel-et/add-material', methods=['GET', 'POST'])
@login_required
def add_material():
    form = AddMaterialForm()

    if form.validate_on_submit():
        item_name = form.item_name.data
        quantity = form.quantity.data
        cost = form.cost.data
        if cost == '0' or cost == 'None' or cost == '':
            cost = '0.0'
            total_cost = '0.0'
        else:
            total_cost = decimal.Decimal(cost) * decimal.Decimal(quantity)
                

        material = Material(item_name = item_name,
                            quantity = quantity,
                            cost = cost,
                            total_cost = str(total_cost))

        db.session.add(material)
        db.session.commit()

        return redirect(url_for('remodel_et.main'))

    return render_template('remodel_et/add_material.html', form = form)


@remodel_et.route('/remodel-et/delete-material', methods = ['GET', 'POST'])
@login_required
def delete_material():

    form = DeleteMaterialForm()
    form.item_names.choices = [(f"{m.id}", f"{m.item_name}") for m in Material.query.all()]

    if form.validate_on_submit():
        material_to_delete = Material.query.filter_by(id = form.item_names.data).first()

        db.session.delete(material_to_delete)
        db.session.commit()

        return redirect(url_for('remodel_et.main'))

    return render_template('remodel_et/delete_material.html', form = form)


@remodel_et.route('/remodel-et/change-quantity', methods = ['GET', 'POST'])
@login_required
def change_quantity():

    form = ChangeMaterialQuantityForm()
    form.item_names.choices = [(f"{m.id}", f"{m.item_name}") for m in Material.query.all()]

    if form.validate_on_submit():
        material = Material.query.filter_by(id = form.item_names.data).first()
        new_cost = decimal.Decimal(form.additional_quantity.data) * decimal.Decimal(material.cost)
        total_cost = str(decimal.Decimal(material.total_cost) + new_cost)
        material.quantity = str(decimal.Decimal(material.quantity) + decimal.Decimal(form.additional_quantity.data))
        material.total_cost = total_cost

        db.session.commit()

        return redirect(url_for('remodel_et.main'))

    return render_template('remodel_et/change_quantity.html', form = form)


@remodel_et.route('/remodel-et/change-cost', methods = ['GET', 'POST'])
@login_required
def change_cost():

    form = ChangeMaterialCostForm()
    form.item_name.choices = [(f"{m.id}", f"{m.item_name}") for m in Material.query.all()]

    if form.validate_on_submit():
        material = Material.query.filter_by(id = form.item_name.data).first()
        material.cost = form.new_cost.data

        db.session.commit()

        return redirect(url_for('remodel_et.main'))

    return render_template('remodel_et/change_cost.html', form = form)

