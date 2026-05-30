from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import requests
import os
import random
import string
import json
from datetime import datetime

app = Flask(__name__,
    template_folder=os.path.dirname(os.path.abspath(__file__)),
    static_folder=os.path.dirname(os.path.abspath(__file__)))

app.secret_key = 'kfresh_secret_2024'

MAKE_WEBHOOK = "https://hook.eu1.make.com/d6wxt51artyxnblpaiia60f45nvpmx4x"
MANAGER_PASSWORD = "KFresh@2024"

PRICES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prices.json')

def get_prices():
    if os.path.exists(PRICES_FILE):
        with open(PRICES_FILE, 'r') as f:
            return json.load(f)
    default_prices = {
        "Celebration Cake": 2000,
        "Coconut Cake": 2500,
        "Red Velvet Cake": 3500,
        "Loaf Cake": 800,
        "Assorted Cake Display": 10000,
        "Brown Bread": 65,
        "Classic Muffins": 250,
        "Red Muffins": 300,
        "Dark Muffins": 300
    }
    save_prices(default_prices)
    return default_prices

def save_prices(prices):
    with open(PRICES_FILE, 'w') as f:
        json.dump(prices, f)

def generate_order_code():
    date = datetime.now().strftime("%d%m")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"KF-{date}-{random_part}"

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/products')
def products():
    prices = get_prices()
    return render_template('products.html', prices=prices)

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

@app.route('/submit-order', methods=['POST'])
def submit_order():
    order_code = generate_order_code()
    data = {
        "order_code": order_code,
        "name": request.form.get('name'),
        "phone": request.form.get('phone'),
        "email": request.form.get('email'),
        "order_details": request.form.get('order_details'),
        "total": request.form.get('total'),
        "address": request.form.get('address'),
        "delivery": request.form.get('delivery'),
        "mpesa_code": request.form.get('mpesa_code'),
        "instructions": request.form.get('instructions'),
    }
    try:
        requests.post(MAKE_WEBHOOK, json=data)
        return render_template('checkout.html', success=True, order_code=order_code)
    except Exception as e:
        print(f"Error: {e}")
        return render_template('checkout.html', success=True, order_code=order_code)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == MANAGER_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error=True)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    prices = get_prices()
    return render_template('dashboard.html', prices=prices)

@app.route('/update-prices', methods=['POST'])
def update_prices():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    prices = get_prices()
    for product in prices:
        new_price = request.form.get(product)
        if new_price:
            try:
                prices[product] = int(new_price)
            except:
                pass
    save_prices(prices)
    return redirect(url_for('dashboard') + '?updated=true')

if __name__ == '__main__':
    app.run(debug=True)
