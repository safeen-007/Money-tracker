from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from datetime import datetime
from collections import defaultdict
import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

from models import db, Expense

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Folder for uploaded receipts
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db.init_app(app)

@app.route('/')
def index():
    expenses = Expense.query.all()
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    monthly_expenses = [e for e in expenses if datetime.fromisoformat(e.date).month == current_month and datetime.fromisoformat(e.date).year == current_year]
    total = sum(expense.amount for expense in expenses)

    # Category-wise spending
    category_totals = defaultdict(float)
    for expense in monthly_expenses:
        category_totals[expense.category] += expense.amount

    # Daily trends
    daily_totals = defaultdict(float)
    for expense in monthly_expenses:
        date = expense.date
        daily_totals[date] += expense.amount
    daily_totals = dict(sorted(daily_totals.items()))

    # Daily expenses grouped by date
    daily_expenses = defaultdict(list)
    for expense in monthly_expenses:
        daily_expenses[expense.date].append(expense)

    return render_template('index.html', expenses=expenses, total=total, category_totals=category_totals, daily_totals=daily_totals, daily_expenses=daily_expenses)

@app.route('/add', methods=['POST'])
def add_expense():
    date = request.form['date']
    description = request.form['description']
    amount = float(request.form['amount'])
    category = request.form['category']
    notes = request.form.get('notes', '')
    receipt = request.files.get('receipt')
    receipt_path = None
    if receipt and receipt.filename:
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{receipt.filename}"
        receipt.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        receipt_path = f"uploads/{filename}"
    expense = Expense(date=date, description=description, amount=amount, category=category, notes=notes, receipt=receipt_path)
    db.session.add(expense)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/clear', methods=['POST'])
def clear_expenses():
    Expense.query.delete()
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/export/excel')
def export_excel():
    expenses = Expense.query.all()
    data = []
    for expense in expenses:
        data.append({
            'Date': expense.date,
            'Description': expense.description,
            'Amount': expense.amount,
            'Category': expense.category,
            'Notes': expense.notes,
            'Receipt': expense.receipt
        })
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Expenses')
    output.seek(0)
    return send_file(output, download_name='expenses.xlsx', as_attachment=True)

@app.route('/export/pdf')
def export_pdf():
    expenses = Expense.query.all()
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.drawString(100, height - 50, "Day-to-Day Expense Tracker Report")
    c.drawString(100, height - 80, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    y = height - 120
    c.drawString(50, y, "Date")
    c.drawString(150, y, "Description")
    c.drawString(300, y, "Amount")
    c.drawString(400, y, "Category")
    y -= 20

    for expense in expenses:
        if y < 50:
            c.showPage()
            y = height - 50
        c.drawString(50, y, expense.date)
        c.drawString(150, y, expense.description[:30])
        c.drawString(300, y, f"₹{expense.amount:.2f}")
        c.drawString(400, y, expense.category)
        y -= 15

    c.save()
    buffer.seek(0)
    return send_file(buffer, download_name='expenses.pdf', as_attachment=True)

@app.route('/backup/local')
def backup_local():
    import shutil
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"{backup_dir}/expenses_backup_{timestamp}.db"
    shutil.copy('instance/expenses.db', backup_file)
    return jsonify({'message': f'Backup saved to {backup_file}'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
