# -*- coding: utf-8 -*-
"""
@author: Adam Getbags
CoinMarketCap API: Advanced Guide 
"""

# Install dependencies with: pip install flask flask_sqlalchemy flask_login python-dotenv requests plotly pandas
import sqlite3
import os
import time as t
import datetime as dt
import logging
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.offline import plot
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'my-hardcoded-dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crypto_wallet.db'
db = SQLAlchemy(app)

# Login manager setup
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

CMC_API_KEY = os.getenv('CMC_API_KEY', 'feece7e9-ec98-41b1-a135-603bb475534b')

# -----------------------
# Database Models
# -----------------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    wallets = db.relationship('Wallet', backref='user', lazy=True)

class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    crypto_symbol = db.Column(db.String(10), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    transactions = db.relationship('Transaction', backref='wallet', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=dt.datetime.utcnow)
    fiat_value = db.Column(db.Float)
    fiat_currency = db.Column(db.String(3), default='USD')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -----------------------
# External API Integration
# -----------------------

def get_crypto_rates(symbols, fiat_currency):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': CMC_API_KEY,
    }
    params = {
        'symbol': ','.join(symbols),
        'convert': fiat_currency
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        return {
            symbol: {fiat_currency.lower(): data['data'][symbol]['quote'][fiat_currency]['price']}
            for symbol in symbols if symbol in data['data']
        }
    except Exception as e:
        logger.error(f"Error fetching data from CoinMarketCap: {e}")
        return {}

# -----------------------
# Routes
# -----------------------

@app.route('/')
@login_required
def dashboard():
    wallets = Wallet.query.filter_by(user_id=current_user.id).all()
    fiat_currency = request.args.get('fiat', 'USD').upper()
    symbols = [wallet.crypto_symbol for wallet in wallets]
    rates = get_crypto_rates(symbols, fiat_currency)

    wallet_data, total_value = [], 0
    for wallet in wallets:
        symbol = wallet.crypto_symbol
        rate = rates.get(symbol, {}).get(fiat_currency.lower())
        fiat_value = wallet.balance * rate if rate else 0
        total_value += fiat_value
        wallet_data.append({
            'id': wallet.id,
            'symbol': symbol,
            'balance': wallet.balance,
            'fiat_value': fiat_value,
            'fiat_currency': fiat_currency,
            'rate': rate
        })

    return render_template('dashboard.html', wallets=wallet_data, total_value=total_value, fiat_currency=fiat_currency)

@app.route('/api/rates')
@login_required
def get_rates():
    fiat_currency = request.args.get('fiat', 'USD').upper()
    symbols = request.args.get('symbols', '').split(',')
    if not symbols:
        return jsonify({'error': 'No symbols provided'}), 400
    return jsonify(get_crypto_rates(symbols, fiat_currency))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash('Registration successful')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/add_crypto', methods=['POST'])
@login_required
def add_crypto():
    symbol = request.form.get('symbol', '').upper()
    try:
        initial_amount = float(request.form.get('amount', 0))
    except ValueError:
        flash('Invalid amount')
        return redirect(url_for('dashboard'))

    if Wallet.query.filter_by(user_id=current_user.id, crypto_symbol=symbol).first():
        flash(f'Wallet for {symbol} already exists')
        return redirect(url_for('dashboard'))

    wallet = Wallet(user_id=current_user.id, crypto_symbol=symbol, balance=initial_amount)
    db.session.add(wallet)
    db.session.flush()  # Get wallet.id before commit

    if initial_amount > 0:
        db.session.add(Transaction(wallet_id=wallet.id, transaction_type='deposit', amount=initial_amount))

    db.session.commit()
    flash(f'Added {symbol} wallet')
    return redirect(url_for('dashboard'))

@app.route('/update_balance', methods=['POST'])
@login_required
def update_balance():
    wallet_id = request.form.get('wallet_id')
    transaction_type = request.form.get('type')
    try:
        amount = float(request.form.get('amount'))
    except ValueError:
        flash('Invalid amount')
        return redirect(url_for('dashboard'))

    wallet = Wallet.query.get_or_404(wallet_id)
    if wallet.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    if transaction_type == 'withdraw':
        if amount > wallet.balance:
            flash('Insufficient balance')
            return redirect(url_for('dashboard'))
        wallet.balance -= amount
    else:
        wallet.balance += amount

    db.session.add(Transaction(wallet_id=wallet.id, transaction_type=transaction_type, amount=amount))
    db.session.commit()

    flash(f'{transaction_type.capitalize()} successful')
    return redirect(url_for('dashboard'))

@app.route('/transactions')
@login_required
def transactions():
    wallet_id = request.args.get('wallet_id')
    fiat_currency = request.args.get('fiat', 'USD').upper()
    
    if wallet_id:
        wallet = Wallet.query.get_or_404(wallet_id)
        if wallet.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        txns = Transaction.query.filter_by(wallet_id=wallet_id).order_by(Transaction.timestamp.desc()).all()
        symbols = [wallet.crypto_symbol]
    else:
        wallet_ids = [w.id for w in Wallet.query.filter_by(user_id=current_user.id)]
        txns = Transaction.query.filter(Transaction.wallet_id.in_(wallet_ids)).order_by(Transaction.timestamp.desc()).all()
        symbols = [w.crypto_symbol for w in Wallet.query.filter_by(user_id=current_user.id)]

    # Get current rates for all crypto symbols
    rates = get_crypto_rates(symbols, fiat_currency)
    
    # Add fiat values to transactions
    for txn in txns:
        wallet = Wallet.query.get(txn.wallet_id)
        rate = rates.get(wallet.crypto_symbol, {}).get(fiat_currency.lower(), 0)
        txn.fiat_value = txn.amount * rate
        txn.fiat_currency = fiat_currency

    return render_template('transactions.html', transactions=txns, fiat_currency=fiat_currency)

@app.route('/profit_loss')
@login_required
def profit_loss():
    fiat_currency = request.args.get('fiat', 'USD').upper()
    wallets = Wallet.query.filter_by(user_id=current_user.id).all()
    symbols = [wallet.crypto_symbol for wallet in wallets]
    rates = get_crypto_rates(symbols, fiat_currency)
    
    profit_loss_data = []
    total_profit_loss = 0
    
    for wallet in wallets:
        # Get all transactions for this wallet
        transactions = Transaction.query.filter_by(wallet_id=wallet.id).all()
        
        # Calculate total deposits and withdrawals in crypto
        total_deposits = sum(t.amount for t in transactions if t.transaction_type == 'deposit')
        total_withdrawals = sum(t.amount for t in transactions if t.transaction_type == 'withdraw')
        
        # Get current rate
        current_rate = rates.get(wallet.crypto_symbol, {}).get(fiat_currency.lower(), 0)
        
        # Calculate values in fiat
        initial_investment = total_deposits * current_rate
        withdrawals_value = total_withdrawals * current_rate
        current_balance_value = wallet.balance * current_rate
        
        # Calculate profit/loss
        profit_loss = current_balance_value - (initial_investment - withdrawals_value)
        profit_loss_percentage = (profit_loss / (initial_investment - withdrawals_value)) * 100 if (initial_investment - withdrawals_value) > 0 else 0
        
        total_profit_loss += profit_loss
        
        profit_loss_data.append({
            'symbol': wallet.crypto_symbol,
            'initial_investment': initial_investment,
            'withdrawals': withdrawals_value,
            'current_balance': current_balance_value,
            'profit_loss': profit_loss,
            'profit_loss_percentage': profit_loss_percentage
        })
    
    return render_template('profit_loss.html', 
                         profit_loss_data=profit_loss_data,
                         total_profit_loss=total_profit_loss,
                         fiat_currency=fiat_currency)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
