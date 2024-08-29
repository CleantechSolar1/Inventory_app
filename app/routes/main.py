import io
import csv
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, Response
from flask_login import login_required, current_user
from app import db
from app.models import Inventory, Log, User
from app.forms import InventoryForm
from datetime import datetime
from flask import render_template, redirect, url_for, request, flash
from app.models import User
from app.forms import ResetPasswordForm  # Create this form as needed
from werkzeug.security import generate_password_hash
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
#from forms import ResetPasswordForm  # Update this import based on your project structure
#from models import User  # Update this import based on your project structure


# Define the main Blueprint
main = Blueprint('main', __name__)

# Dropdown options
ASSET_TYPES = ['Laptop', 'Monitors']
STATUS = ['Available', 'Sold', 'In Use', 'Retired', 'Dead']
BRANDS = ['Lenovo', 'Dell', 'HP', 'Apple', 'ViewSonic', 'Samsung']
OPERATING_SYSTEMS = ['Windows', 'Mac', 'Linux']
DEPARTMENTS = ['IT', 'Procurement', 'Legal', 'Project', 'O&M', 'Finance', 'BD', 'HR', 'Wind', 'Risk', 'Engineering']
OFFICES = ['Mumbai', 'Pune', 'Delhi', 'Hyderabad', 'Chennai', 'Singapore', 'Thailand', 'Malaysia', 'Philippines', 'Vietnam', 'Cambodia', 'Indonesia', 'India']
COUNTRIES = ['Singapore', 'Thailand', 'Malaysia', 'Philippines', 'Vietnam', 'Cambodia', 'Indonesia', 'India']
VENDOR_LOCATIONS = ['Mumbai', 'Pune', 'Delhi', 'Hyderabad', 'Chennai', 'Singapore', 'Thailand', 'Malaysia', 'Philippines', 'Vietnam', 'Cambodia', 'Indonesia', 'India']

@main.route('/', methods=['GET', 'POST'])
@login_required
def home():
    # Get aggregated data
    asset_type_counts = db.session.query(Inventory.asset_type, db.func.count(Inventory.id)).group_by(Inventory.asset_type).all()
    department_counts = db.session.query(Inventory.department, db.func.count(Inventory.id)).group_by(Inventory.department).all()
    country_counts = db.session.query(Inventory.country, db.func.count(Inventory.id)).group_by(Inventory.country).all()
    status_counts = db.session.query(Inventory.status, db.func.count(Inventory.id)).group_by(Inventory.status).all()

    # Filters
    asset_type_filter = request.args.get('asset_type')
    department_filter = request.args.get('department')
    country_filter = request.args.get('country')
    status_filter = request.args.get('status')
    purchase_date_start = request.args.get('purchase_date_start')
    purchase_date_end = request.args.get('purchase_date_end')
    warranty_end_date_start = request.args.get('warranty_end_date_start')
    warranty_end_date_end = request.args.get('warranty_end_date_end')

    # Apply filters
    items_query = Inventory.query

    if asset_type_filter:
        items_query = items_query.filter_by(asset_type=asset_type_filter)
    if department_filter:
        items_query = items_query.filter_by(department=department_filter)
    if country_filter:
        items_query = items_query.filter_by(country=country_filter)
    if status_filter:
        items_query = items_query.filter_by(status=status_filter)
    if purchase_date_start:
        items_query = items_query.filter(Inventory.purchase_date >= datetime.strptime(purchase_date_start, '%Y-%m-%d'))
    if purchase_date_end:
        items_query = items_query.filter(Inventory.purchase_date <= datetime.strptime(purchase_date_end, '%Y-%m-%d'))
    if warranty_end_date_start:
        items_query = items_query.filter(Inventory.warranty_end_date >= datetime.strptime(warranty_end_date_start, '%Y-%m-%d'))
    if warranty_end_date_end:
        items_query = items_query.filter(Inventory.warranty_end_date <= datetime.strptime(warranty_end_date_end, '%Y-%m-%d'))

    # Pagination with 20 items per page
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Number of items per page
    items = items_query.paginate(page=page, per_page=per_page, error_out=False)

    # Prepare a clean dictionary of query parameters
    query_params = request.args.copy()
    query_params.pop('page', None)  # Remove 'page' if it exists

    return render_template('home.html',
                           items=items.items,
                           asset_type_counts=asset_type_counts,
                           department_counts=department_counts,
                           country_counts=country_counts,
                           status_counts=status_counts,
                           asset_type_filter=asset_type_filter,
                           department_filter=department_filter,
                           country_filter=country_filter,
                           purchase_date_start=purchase_date_start,
                           purchase_date_end=purchase_date_end,
                           warranty_end_date_start=warranty_end_date_start,
                           warranty_end_date_end=warranty_end_date_end,
                           pagination=items,
                           query_params=query_params,
                           asset_types=ASSET_TYPES,
                           statuses=STATUS,
                           brands=BRANDS,
                           operating_systems=OPERATING_SYSTEMS,
                           departments=DEPARTMENTS,
                           offices=OFFICES,
                           countries=COUNTRIES,
                           vendor_locations=VENDOR_LOCATIONS)


@main.route('/add', methods=['GET', 'POST'])
@login_required
def add_item():
    form = InventoryForm()
    form.asset_type.choices = [(at, at) for at in ASSET_TYPES]
    form.status.choices = [(st, st) for st in STATUS]
    form.brand.choices = [(br, br) for br in BRANDS]
    form.operating_system.choices = [(os, os) for os in OPERATING_SYSTEMS]
    form.department.choices = [(dp, dp) for dp in DEPARTMENTS]
    form.office.choices = [(of, of) for of in OFFICES]
    form.country.choices = [(ct, ct) for ct in COUNTRIES]
    form.vendor_location.choices = [(vl, vl) for vl in VENDOR_LOCATIONS]

    if form.validate_on_submit():
        try:
            new_item = Inventory(
                asset_tag=form.asset_tag.data,
                asset_type=form.asset_type.data,
                status=form.status.data,
                brand=form.brand.data,
                model=form.model.data,
                fa_code=form.fa_code.data,
                serial_number=form.serial_number.data,
                operating_system=form.operating_system.data,
                purchase_date=form.purchase_date.data,
                age=form.age.data,
                current_owner=form.current_owner.data,
                previous_owner=form.previous_owner.data,
                warranty_end_date=form.warranty_end_date.data,
                condition_notes=form.condition_notes.data,
                department=form.department.data,
                office=form.office.data,
                country=form.country.data,
                vendor_location=form.vendor_location.data,
                updated_by=current_user.username
            )
            db.session.add(new_item)
            db.session.commit()

            # Log the addition
            log = Log(
                user_id=current_user.id,
                action="Added item",
                item_id=new_item.id,
                changes="Added new item with details: " + str(new_item.__dict__)
            )
            db.session.add(log)
            db.session.commit()

            current_app.logger.info(f'{current_user.username} added new item: {new_item.asset_tag}')
            flash('Item added successfully!', 'success')
            return redirect(url_for('main.home'))
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error adding item: {e}')
            flash('An error occurred while adding the item. Please try again.', 'danger')
    else:
        current_app.logger.warning(f'Form validation failed: {form.errors}')
    
    return render_template('add_item.html', form=form, asset_types=ASSET_TYPES, statuses=STATUS, brands=BRANDS,
                           operating_systems=OPERATING_SYSTEMS, departments=DEPARTMENTS, offices=OFFICES, countries=COUNTRIES,
                           vendor_locations=VENDOR_LOCATIONS)

@main.route('/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = Inventory.query.get_or_404(item_id)
    form = InventoryForm(obj=item)
    form.asset_type.choices = [(at, at) for at in ASSET_TYPES]
    form.status.choices = [(st, st) for st in STATUS]
    form.brand.choices = [(br, br) for br in BRANDS]
    form.operating_system.choices = [(os, os) for os in OPERATING_SYSTEMS]
    form.department.choices = [(dp, dp) for dp in DEPARTMENTS]
    form.office.choices = [(of, of) for of in OFFICES]
    form.country.choices = [(ct, ct) for ct in COUNTRIES]
    form.vendor_location.choices = [(vl, vl) for vl in VENDOR_LOCATIONS]
    
    if form.validate_on_submit():
        old_data = {field.name: getattr(item, field.name) for field in item.__table__.columns}
        form.populate_obj(item)
        item.updated_by = current_user.username
        
        # Detect changes
        changes = {}
        for field in item.__table__.columns:
            new_value = getattr(item, field.name)
            if old_data[field.name] != new_value:
                changes[field.name] = {'old': old_data[field.name], 'new': new_value}
        
        db.session.commit()
        
        # Log the update
        log = Log(
            user_id=current_user.id,
            action="Updated item",
            item_id=item.id,
            changes=str(changes)
        )
        db.session.add(log)
        db.session.commit()
        
        current_app.logger.info(f'{current_user.username} updated item: {item.asset_tag}')
        flash('Item updated successfully!', 'success')
        return redirect(url_for('main.home'))
    
    return render_template('edit_item.html', form=form, item=item, asset_types=ASSET_TYPES, statuses=STATUS, brands=BRANDS,
                           operating_systems=OPERATING_SYSTEMS, departments=DEPARTMENTS, offices=OFFICES, countries=COUNTRIES,
                           vendor_locations=VENDOR_LOCATIONS)

@main.route('/view_logs')
@login_required
def view_logs():
    logs = Log.query.order_by(Log.timestamp.desc()).all()
    current_app.logger.info(f"Fetched {len(logs)} logs")
    for log in logs:
        current_app.logger.debug(f"Log: ID {log.id}, Action {log.action}, Item ID {log.item_id}, Changes {log.changes}")
    return render_template('view_logs.html', logs=logs)

@main.route('/export_csv')
@login_required
def export_csv():
    # Fetch inventory items from the database
    items = Inventory.query.all()
    
    # Create a CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header row
    writer.writerow([
        'Asset Tag', 'Asset Type', 'Status', 'Brand', 'Model',
        'FA Code', 'Serial Number', 'Operating System', 'Purchase Date',
        'Age', 'Current Owner', 'Previous Owner', 'Warranty End Date',
        'Condition Notes', 'Department', 'Office', 'Country', 'Vendor Location', 'Updated By'
    ])
    
    # Write data rows
    for item in items:
        writer.writerow([
            item.asset_tag, item.asset_type, item.status, item.brand, item.model,
            item.fa_code, item.serial_number, item.operating_system, item.purchase_date,
            item.age, item.current_owner, item.previous_owner, item.warranty_end_date,
            item.condition_notes, item.department, item.office, item.country, item.vendor_location, item.updated_by
        ])
    
    # Create a response object with CSV content
    output.seek(0)
    return Response(
        output,
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=inventory_data.csv"}
    )

@main.route('/export_logs_csv')
@login_required
def export_logs_csv():
    # Fetch logs from the database
    logs = Log.query.all()
    
    # Create a CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header row
    writer.writerow([
        'Timestamp', 'User ID', 'Username', 'Action', 'Item ID', 'Changes'
    ])
    
    # Write data rows
    for log in logs:
        username = User.query.get(log.user_id).username if log.user_id else 'Unknown'
        writer.writerow([
            log.timestamp,
            log.user_id,
            username,
            log.action,
            log.item_id,
            log.changes
        ])
    
    # Create a response object with CSV content
    output.seek(0)
    return Response(
        output,
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=logs_data.csv"}
    )


@main.route('/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    if current_user.username != 'sameer':
        flash("You do not have permission to delete items.", "danger")
        return redirect(url_for('main.home'))

    item = Inventory.query.get_or_404(item_id)
    
    try:
        # Create the log entry
        log = Log(
            user_id=current_user.id,
            action="Deleted item",
            item_id=item_id,
            changes=f"Item deleted: {item.asset_tag}",
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        
        # Delete the item
        db.session.delete(item)
        
        # Commit both the log entry and the item deletion
        db.session.commit()
        
        flash('Item deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting item: {e}')
        flash('An error occurred while deleting the item. Please try again.', 'danger')
    
    return redirect(url_for('main.home'))

# User Management Routes

@main.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.username != 'sameer':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('main.add_user'))
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        # Log the user addition
        log = Log(
            user_id=current_user.id,
            action="Added user",
            item_id=None,
            changes=f"Added user with username: {username}"
        )
        db.session.add(log)
        db.session.commit()
        
        flash('User added successfully.', 'success')
        return redirect(url_for('main.home'))
    
    return render_template('add_user.html')

@main.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if user and user.username != 'sameer':
        # Delete all logs related to this user
        logs = Log.query.filter_by(user_id=user_id).all()
        for log in logs:
            db.session.delete(log)
        
        db.session.delete(user)
        db.session.commit()
        
        flash('User deleted successfully.', 'success')
    else:
        flash('Superuser cannot be deleted.', 'error')
    
    return redirect(url_for('main.view_users'))


@main.route('/view_users')
@login_required
def view_users():
    if current_user.username != 'sameer':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.home'))

    users = User.query.all()
    return render_template('view_users.html', users=users)

@main.route('/reset_password/<int:user_id>', methods=['GET', 'POST'])
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        form = ResetPasswordForm(request.form)
        if form.validate():
            user.password_hash = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash('Password reset successfully!', 'success')
            return redirect(url_for('main.view_users'))
        else:
            flash('Error resetting password. Please try again.', 'danger')
    else:
        form = ResetPasswordForm()
    return render_template('reset_password.html', form=form, user=user)

@main.route('/import_csv', methods=['GET', 'POST'])
@login_required
def import_csv():
    if request.method == 'POST':
        file = request.files['file']
        if not file:
            flash('No file selected!', 'danger')
            return redirect(request.url)

        try:
            # Read the CSV file
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_input = csv.reader(stream)

            # Skip the header row if your CSV file has one
            next(csv_input, None)

            # Iterate over the CSV rows
            for row in csv_input:
                # Assuming your CSV columns are in the same order as your Inventory model
                new_item = Inventory(
                    asset_tag=row[0],
                    asset_type=row[1],
                    status=row[2],
                    brand=row[3],
                    model=row[4],
                    fa_code=row[5],
                    serial_number=row[6],
                    operating_system=row[7],
                    purchase_date=datetime.strptime(row[8], '%Y-%m-%d'),
                    age=row[9],
                    current_owner=row[10],
                    previous_owner=row[11],
                    warranty_end_date=datetime.strptime(row[12], '%Y-%m-%d'),
                    condition_notes=row[13],
                    department=row[14],
                    office=row[15],
                    country=row[16],
                    vendor_location=row[17],
                    updated_by=current_user.username
                )
                db.session.add(new_item)

            db.session.commit()
            flash('CSV file imported successfully!', 'success')
            return redirect(url_for('main.home'))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error importing CSV file: {e}')
            flash('An error occurred while importing the file. Please check the format and try again.', 'danger')
            return redirect(request.url)
    
    return render_template('import_csv.html')
