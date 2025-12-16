from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from flask import (
    Flask, render_template, request,
    redirect, url_for, flash, jsonify, session, Response
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user,
    logout_user, login_required, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import os
from datetime import datetime
import csv
from io import StringIO
import logging

# ================= APP CONFIG =================
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'cryptonest-dev-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cryptonest.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'warning'

# ================= DATABASE MODELS =================
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Portfolio(db.Model):
    __tablename__ = 'portfolio'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    symbol = db.Column(db.String(10), nullable=False, index=True)  # BTC, ETH, SOL
    name = db.Column(db.String(50))  # Full name like "Bitcoin"
    buy_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    buy_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('portfolio_items', lazy='dynamic'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ================= CURRENCY SUPPORT =================
CURRENCY_RATES = {
    'USD': 1.0,
    'EUR': 0.92,
    'GBP': 0.79,
    'INR': 84.5,
    'JPY': 150.2,
    'CAD': 1.38,
    'AUD': 1.52
}

def get_currency_symbol(currency):
    symbols = {'USD': '$', 'EUR': '€', 'GBP': '£', 'INR': '₹', 'JPY': '¥', 'CAD': 'C$', 'AUD': 'A$'}
    return symbols.get(currency, '$')

# ================= FIXED PRICE FETCHING =================
def get_coingecko_price(symbol, currency='USD'):
    """ Works for ALL your coins"""
    symbol_map = {
        'BTC': 'bitcoin', 'ETH': 'ethereum', 'ETC': 'ethereum-classic',
        'SOL': 'solana', 'ADA': 'cardano', 'DOT': 'polkadot',
        'MATIC': 'polygon', 'LINK': 'chainlink', 'LTC': 'litecoin',
        'BNB': 'binancecoin', 'XRP': 'ripple', 'DOGE': 'dogecoin',
        'AVAX': 'avalanche-2', 'UNI': 'uniswap', 'USDT': 'tether',
        'PEPE': 'pepe', 'SHIB': 'shiba-inu', 'BONK': 'bonk', 'WIF': 'dogwifcoin'
    }
    
    coin_id = symbol_map.get(symbol, symbol.lower())
    vs_currency = currency.lower()
    
    try:
        # SINGLE API CALL - FASTEST METHOD
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {'ids': coin_id, 'vs_currencies': vs_currency}
        response = requests.get(url, params=params, timeout=8)
        data = response.json()
        
        price = data.get(coin_id, {}).get(vs_currency, 0.0)
        
        if price > 0:
            print(f" {symbol}: ${price} {currency}")
            return price
        else:
            print(f"NO PRICE {symbol} (id: {coin_id})")
            return 0.0
            
    except Exception as e:
        print(f" ERROR {symbol}: {e}")
        return 0.0




def get_portfolio_data(user, currency='USD'):
    """  Proper currency conversion + prices"""
    portfolio = []
    total_value = 0.0
    total_pnl = 0.0
    
    items = user.portfolio_items.all()
    if not items:
        return portfolio, total_value, total_pnl
    
    # Get ALL prices in ONE BATCH (faster!)
    symbols = [item.symbol for item in items]
    all_prices = get_batch_prices(symbols, currency)
    
    for item in items:
        # Get current price (already in SELECTED currency)
        current_price = all_prices.get(item.symbol, 0.0)
        
        # Buy price was ALWAYS stored in USD → convert to current currency
        usd_to_current = CURRENCY_RATES.get(currency, 1.0)
        buy_price_current = item.buy_price * usd_to_current
        
        current_value = item.quantity * current_price
        pnl_24h = ((current_price - buy_price_current) / buy_price_current * 100) if buy_price_current > 0 else 0
        
        portfolio.append({
            'id': item.id,
            'name': item.name or item.symbol,
            'symbol': item.symbol,
            'quantity': item.quantity,
            'buy_price': buy_price_current,
            'current_price': current_price,
            'current_value': current_value,
            'pnl_24h': pnl_24h
        })
        
        total_value += current_value
    
    print(f" PORTFOLIO ({len(portfolio)} coins): Total ${total_value:,.2f}")
    return portfolio, total_value, total_pnl
def get_batch_prices(symbols, currency='USD'):
    """ BATCH API - Get ALL prices in 1 call"""
    if not symbols:
        return {}
    
    symbol_map = {
        'BTC': 'bitcoin', 'ETH': 'ethereum', 'ETC': 'ethereum-classic',
        'SOL': 'solana', 'ADA': 'cardano', 'DOT': 'polkadot',
        'MATIC': 'polygon', 'LINK': 'chainlink', 'LTC': 'litecoin',
        'BNB': 'binancecoin', 'XRP': 'ripple', 'DOGE': 'dogecoin',
        'AVAX': 'avalanche-2', 'UNI': 'uniswap', 'USDT': 'tether',
        'PEPE': 'pepe', 'SHIB': 'shiba-inu', 'BONK': 'bonk', 'WIF': 'dogwifcoin'
    }
    
    coin_ids = [symbol_map.get(s, s.lower()) for s in symbols]
    vs_currency = currency.lower()
    
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {'ids': ','.join(coin_ids), 'vs_currencies': vs_currency}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        prices = {}
        for symbol in symbols:
            coin_id = symbol_map.get(symbol, symbol.lower())
            price = data.get(coin_id, {}).get(vs_currency, 0.0)
            prices[symbol] = price
            if price > 0:
                print(f"✅ BATCH {symbol}: ${price}")
        
        return prices
        
    except Exception as e:
        print(f" BATCH ERROR: {e}")
        return {symbol: 0.0 for symbol in symbols}


# ================= ROUTES (UNCHANGED except dashboard) =================
@app.route('/')
def index():
    currency = request.args.get('currency', 'USD').upper()
    if currency not in CURRENCY_RATES:
        currency = 'USD'
    currency_symbol = get_currency_symbol(currency)
    
    return render_template('index.html', 
                           currency=currency,
                           currency_symbol=currency_symbol)

# ---------- AUTH ROUTES (UNCHANGED) ----------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if len(name) < 2:
            flash('Name must be at least 2 characters.', 'danger')
            return render_template('signup.html')
        if '@' not in email:
            flash('Please enter a valid email.', 'danger')
            return render_template('signup.html')
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('signup.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please login.', 'danger')
            return redirect(url_for('login'))
        
        try:
            user = User(
                name=name, 
                email=email, 
                password=generate_password_hash(password)
            )
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            logger.error(f"Signup error: {e}")
            flash('Registration failed. Please try again.', 'danger')
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Invalid email or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        flash('Password reset link sent! Check your email. (Demo mode)', 'success')
        return redirect(url_for('login'))
    return render_template('forgot_password.html')

# ---------- DASHBOARD (UNCHANGED) ----------
@app.route('/dashboard')
@login_required
def dashboard():
    currency = request.args.get('currency', session.get('currency', 'USD')).upper()
    if currency not in CURRENCY_RATES:
        currency = 'USD'
    session['currency'] = currency
    
    portfolio, total_value, total_pnl = get_portfolio_data(current_user, currency)
    return render_template('dashboard.html', 
                           portfolio=portfolio, 
                           total_value=total_value, 
                           total_pnl=total_pnl,
                           currency=currency,
                           currency_symbol=get_currency_symbol(currency))

# ---------- ADD/DELETE COIN (UNCHANGED) ----------
@app.route('/add_coin', methods=['POST'])
@login_required
def add_coin():
    symbol_raw = request.form.get('symbol', '').strip().upper()
    buy_price = float(request.form.get('buy_price') or 0)
    quantity = float(request.form.get('quantity') or 0)
    buy_date_str = request.form.get('buy_date')
    
    symbol = ''.join(c for c in symbol_raw if c.isalpha()).upper()
    
    print(f"RAW: '{request.form.get('symbol')}' → CLEANED: '{symbol}'")
    print(f"Price: {buy_price}, Qty: {quantity}, Date: '{buy_date_str}'")
    
    if len(symbol) < 2:
        flash(f' Symbol too short: "{symbol}" (min 2 chars)', 'danger')
        return redirect(url_for('dashboard'))
    
    if buy_price <= 0 or quantity <= 0 or not buy_date_str:
        flash(' All values must be > 0 and date required', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        from datetime import datetime
        buy_date = datetime.strptime(buy_date_str, '%Y-%m-%d').date()
    except:
        flash(' Bad date', 'danger')
        return redirect(url_for('dashboard'))
    
    coin = Portfolio(
        user_id=current_user.id,
        symbol=symbol,
        name=symbol,
        buy_price=buy_price,
        quantity=quantity,
        buy_date=buy_date
    )
    db.session.add(coin)
    db.session.commit()
    
    flash(f'✅ {symbol} ADDED SUCCESSFULLY!', 'success')
    print(f" ✅SAVED {symbol}!")
    
    return redirect(url_for('dashboard'))

@app.route('/delete_coin/<int:coin_id>', methods=['POST'])
@login_required
def delete_coin(coin_id):
    coin = Portfolio.query.filter_by(id=coin_id, user_id=current_user.id).first()
    if coin:
        symbol = coin.symbol
        db.session.delete(coin)
        db.session.commit()
        flash(f'🗑️ {symbol} removed from portfolio.', 'success')
    else:
        flash('Coin not found or access denied.', 'danger')
    return redirect(url_for('dashboard'))

# ---------- EXPORT ROUTES (UNCHANGED) ----------
@app.route('/export_csv')
@login_required
def export_csv():
    currency = session.get('currency', 'USD')
    currency_symbol = get_currency_symbol(currency)
    
    portfolio, _, _ = get_portfolio_data(current_user, currency)
    si = StringIO()
    cw = csv.writer(si)
    
    cw.writerow(['Coin', 'Symbol', 'Quantity', f'Buy Price ({currency_symbol})', f'Current Price ({currency_symbol})', f'Value ({currency_symbol})', '24h P&L %'])
    cw.writerow(['-' * 20, '-' * 10, '-' * 12, '-' * 12, '-' * 14, '-' * 15, '-' * 12])
    
    for coin in portfolio:
        cw.writerow([
            coin['name'], coin['symbol'], 
            f"{coin['quantity']:.6f}",
            f"{currency_symbol}{coin['buy_price']:.4f}",
            f"{currency_symbol}{coin['current_price']:.4f}",
            f"{currency_symbol}{coin['current_value']:.2f}",
            f"{coin['pnl_24h']:.2f}%"
        ])
    
    output = si.getvalue()
    filename = f"cryptonest-portfolio-{currency}-{current_user.email.split('@')[0]}-{datetime.now().strftime('%Y%m%d')}.csv"
    
    return Response(
        output,
        mimetype='text/csv',
        headers={
            "Content-disposition": f"attachment; filename={filename}",
            "Content-Type": "text/csv"
        }
    )

@app.route('/export_pdf')
@login_required
def export_pdf():
    try:
        currency = session.get('currency', 'USD')
        currency_symbol = get_currency_symbol(currency)
        portfolio, total_value, total_pnl = get_portfolio_data(current_user, currency)
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        title = Paragraph("CryptoNest Portfolio Report", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        user_info = f"""
        <b>User:</b> {current_user.name}<br/>
        <b>Email:</b> {current_user.email}<br/>
        <b>Currency:</b> {currency} ({currency_symbol})<br/>
        <b>Total Value:</b> {currency_symbol}{total_value:,.2f}<br/>
        <b>24h P&L:</b> {total_pnl:+.2f}%<br/>
        <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M IST')}
        """
        story.append(Paragraph(user_info, styles['Normal']))
        story.append(Spacer(1, 30))
        
        if portfolio:
            table_data = [['Coin', 'Symbol', 'Qty', f'Buy {currency_symbol}', f'Current {currency_symbol}', f'Value {currency_symbol}', 'P&L']]
            
            for coin in portfolio:
                pnl_color = '<font color="green">' if coin['pnl_24h'] >= 0 else '<font color="red">'
                table_data.append([
                    coin['name'],
                    coin['symbol'],
                    f"{coin['quantity']:.6f}",
                    f"{currency_symbol}{coin['buy_price']:,.4f}",
                    f"{currency_symbol}{coin['current_price']:,.4f}",
                    f"{currency_symbol}{coin['current_value']:.2f}",
                    f"{pnl_color}{coin['pnl_24h']:.2f}%</font>"
                ])
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                ('ALIGN', (5, 1), (6, -1), 'RIGHT'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            story.append(table)
        else:
            story.append(Paragraph("No coins in portfolio yet.", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        
        filename = f"cryptonest-portfolio-{currency}-{current_user.email.split('@')[0]}-{datetime.now().strftime('%Y%m%d')}.pdf"
        
        return Response(
            buffer.getvalue(),
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment; filename="{filename}"'}
        )
        
    except Exception as e:
        logger.error(f"PDF Error: {e}")
        flash('❌ PDF failed. CSV works perfectly!', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/api/prices')
@login_required
def api_prices():
    symbols = request.args.get('symbols', '').split(',')
    prices = {}
    
    for symbol in symbols:
        if symbol:
            prices[symbol.strip().upper()] = get_coingecko_price(symbol.strip().upper())
    
    return jsonify(prices)

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"500 error: {e}")
    flash('Something went wrong. Please try again.', 'danger')
    return redirect(url_for('dashboard'))

def init_db():
    with app.app_context():
        db.create_all()
        print("✅ Database initialized successfully!")

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



