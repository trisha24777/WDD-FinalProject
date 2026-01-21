import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from functools import wraps
from contextlib import contextmanager

app = Flask(__name__)
app.secret_key = "wh_super_secret_key"

# --- MYSQL CONFIGURATION ---
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234', # <--- Update this!
    'database': 'world_hotels',
    'auth_plugin': 'mysql_native_password' 
}

@contextmanager
def get_db_cursor():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

# --- AUTH DECORATORS ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('user_login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- PRICING & CURRENCY LOGIC ---
EXCHANGE_RATES = {
    'GBP': 1.0,
    'USD': 1.27,
    'EUR': 1.19,
    'NPR': 168.0 
}

def get_calculated_price(peak_rate, off_peak_rate, room_type, check_in_str, currency='GBP'):
    check_in = datetime.strptime(check_in_str, '%Y-%m-%d')
    
    # 1. Determine base rate based on season
    if 4 <= check_in.month <= 8 or check_in.month in [11, 12]:
        base_rate = float(peak_rate)
    else:
        base_rate = float(off_peak_rate)
    
    # 2. Room Type Multipliers
    multipliers = {'Standard': 1.0, 'Double': 1.2, 'Family': 1.5}
    price_gbp = base_rate * multipliers.get(room_type, 1.0)
    
    # 3. Advanced Booking Discounts
    days_ahead = (check_in.date() - datetime.now().date()).days
    if 80 <= days_ahead <= 90:
        price_gbp *= 0.70
    elif 60 <= days_ahead <= 79:
        price_gbp *= 0.80
    elif 45 <= days_ahead <= 59:
        price_gbp *= 0.90
    
    # 4. Currency Conversion
    rate = EXCHANGE_RATES.get(currency, 1.0)
    return round(price_gbp * rate, 2)

# --- PUBLIC ROUTES ---
@app.route('/set_currency/<curr>')
def set_currency(curr):
    if curr in EXCHANGE_RATES:
        session['currency'] = curr
    return redirect(request.referrer or url_for('index'))

@app.route('/')
def index():
    query_city = request.args.get('city', '').lower()
    max_price = request.args.get('max_price', type=float)
    search_date = request.args.get('check_in', '')
    currency = session.get('currency', 'GBP')

    booking_counts = {}
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM hotels")
        db_hotels = cursor.fetchall()
        
        if search_date:
            cursor.execute("SELECT hotel_id, COUNT(*) as count FROM bookings WHERE check_in = %s GROUP BY hotel_id", (search_date,))
            counts = cursor.fetchall()
            for c in counts:
                booking_counts[c['hotel_id']] = c['count']
    
    filtered_hotels = []
    rate = EXCHANGE_RATES.get(currency, 1.0)
    
    for h in db_hotels:
        city_name = h.get('city_name') or h.get('city', 'Unknown')
        hotel_id = h.get('hotel_id') or h.get('id')
        capacity = h.get('capacity', 100)
        
        if query_city and query_city not in city_name.lower(): continue
        
        # Seasonal Rate logic
        is_peak = False
        if search_date:
            try:
                dt = datetime.strptime(search_date, '%Y-%m-%d')
                if 4 <= dt.month <= 8 or dt.month in [11, 12]: is_peak = True
            except: pass
        
        base_gbp = h.get('peak_rate') if is_peak else h.get('off_peak_rate', h.get('base_rate', 0))
        display_rate = round(float(base_gbp) * rate, 2)
        
        if max_price and display_rate > max_price: continue
        
        filtered_hotels.append({
            'id': hotel_id,
            'city': city_name,
            'base_rate': display_rate,
            'available': (booking_counts.get(hotel_id, 0) < capacity) if search_date else True,
            'image': h.get('image_url') or "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800"
        })

    return render_template('index.html', hotels=filtered_hotels, currency=currency)

@app.route('/book', methods=['POST'])
@login_required
def book():
    if session.get('admin'):
        return "Admins cannot book destinations. Please use a regular user account for bookings.", 403

    hotel_id = int(request.form['hotel_id'])
    room_type = request.form['room_type']
    check_in = request.form['check_in']
    duration = int(request.form.get('duration', 1))
    currency = session.get('currency', 'GBP')
    
    if duration > 30:
        return "Error: Maximum stay duration is 30 days.", 400

    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM hotels WHERE hotel_id = %s", (hotel_id,))
        hotel = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE hotel_id = %s AND check_in = %s", (hotel_id, check_in))
        if cursor.fetchone()['count'] >= hotel['capacity']:
            return "Sold Out", 400

        total = get_calculated_price(hotel['peak_rate'], hotel['off_peak_rate'], room_type, check_in, currency) * duration
        
        cursor.execute("""
            INSERT INTO bookings (hotel_id, user_id, room_type, check_in, total_price)
            VALUES (%s, %s, %s, %s, %s)
        """, (hotel_id, session['user_id'], room_type, check_in, total))
    
    return render_template('confirmation.html', city=hotel['city_name'], room=room_type, date=check_in, total=total, currency=currency)

# --- USER PROFILE & BOOKING HISTORY ---
@app.route('/user/bookings')
@login_required
def user_bookings():
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT b.*, h.city_name, h.image_url 
            FROM bookings b 
            JOIN hotels h ON b.hotel_id = h.hotel_id 
            WHERE b.user_id = %s 
            ORDER BY b.check_in DESC
        """, (session['user_id'],))
        bookings = cursor.fetchall()
    
    now = datetime.now().date()
    for b in bookings:
        days_until = (b['check_in'] - now).days
        if days_until >= 60:
            b['cancel_fee'], b['can_cancel'] = 0, True
        elif 30 <= days_until < 60:
            b['cancel_fee'], b['can_cancel'] = float(b['total_price']) * 0.5, True
        else:
            b['cancel_fee'], b['can_cancel'] = float(b['total_price']), False
            
    return render_template('user_bookings.html', bookings=bookings)

@app.route('/user/cancel_booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    with get_db_cursor() as cursor:
        cursor.execute("DELETE FROM bookings WHERE booking_id = %s AND user_id = %s", (booking_id, session['user_id']))
    flash("Booking cancelled successfully.", "success")
    return redirect(url_for('user_bookings'))

# --- USER AUTHENTICATION ---
@app.route('/user/signup', methods=['GET', 'POST'])
def user_signup():
    if request.method == 'POST':
        username, email, password = request.form['username'], request.form['email'], request.form['password']
        try:
            with get_db_cursor() as cursor:
                cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
            return redirect(url_for('user_login'))
        except mysql.connector.Error as err:
            return f"Signup Error: {err.msg}"
    return render_template('user_login.html', mode='signup')

@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()

        if user:
            session.update({'user': user['username'], 'user_id': user['id']})
            return redirect(url_for('index'))
        flash("Invalid username or password. Please try again.", "danger")
    return render_template('user_login.html', mode='login')

# --- ADMIN SECTION ---
@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['admin_id'] == 'admin' and request.form['password'] == 'password123':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        flash("Invalid Admin ID or Security Key.", "danger")
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    with get_db_cursor() as cursor:
        cursor.execute("SELECT id, username, email, role, created_at FROM users ORDER BY created_at DESC")
        all_users = cursor.fetchall()
        
        cursor.execute("SELECT * FROM hotels")
        db_hotels = cursor.fetchall()
        
        cursor.execute("""
            SELECT b.*, h.city_name 
            FROM bookings b 
            JOIN hotels h ON b.hotel_id = h.hotel_id 
            ORDER BY b.booking_date DESC
        """)
        db_bookings = cursor.fetchall()
    
    formatted_bookings = [{
        'id': b['booking_id'], 'city': b['city_name'], 'room': b['room_type'],
        'date': str(b['check_in']), 'total': float(b['total_price'])
    } for b in db_bookings]

    total_rev = sum(b['total'] for b in formatted_bookings)
    
    # Chart Data Preparation
    sales_data = {}
    for b in formatted_bookings:
        sales_data[b['date']] = sales_data.get(b['date'], 0) + b['total']
    
    user_data = {}
    for u in all_users:
        d = u['created_at'].strftime('%Y-%m-%d')
        user_data[d] = user_data.get(d, 0) + 1
    
    room_types = {}
    for b in formatted_bookings:
        room_types[b['room']] = room_types.get(b['room'], 0) + 1
    
    sorted_sales = sorted(sales_data.items())
    sorted_users = sorted(user_data.items())

    return render_template('admin_dashboard.html', 
        bookings=formatted_bookings, 
        hotels=[{
            'id': h.get('hotel_id') or h.get('id'),
            'city': h.get('city_name') or h.get('city'),
            'base_rate': h.get('off_peak_rate') or h.get('base_rate', 0)
        } for h in db_hotels], 
        users=all_users,
        revenue=total_rev,
        chart_data={
            'salesDates': [d for d, v in sorted_sales],
            'salesValues': [v for d, v in sorted_sales],
            'userDates': [d for d, c in sorted_users],
            'userCounts': [c for d, c in sorted_users],
            'roomLabels': list(room_types.keys()),
            'roomCounts': list(room_types.values())
        })

@app.route('/admin/delete_user/<int:user_id>')
@admin_required
def delete_user(user_id):
    with get_db_cursor() as cursor:
        cursor.execute("DELETE FROM bookings WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_hotel', methods=['POST'])
@admin_required
def add_hotel():
    city, base_rate = request.form['city'], float(request.form['base_rate'])
    with get_db_cursor() as cursor:
        cursor.execute("""
            INSERT INTO hotels (city_name, capacity, peak_rate, off_peak_rate, image_url) 
            VALUES (%s, 100, %s, %s, 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800')
        """, (city, base_rate * 1.5, base_rate))
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update_rate', methods=['POST'])
@admin_required
def update_rate():
    hotel_id, new_rate = int(request.form['hotel_id']), float(request.form['new_rate'])
    with get_db_cursor() as cursor:
        cursor.execute("UPDATE hotels SET off_peak_rate = %s, peak_rate = %s WHERE hotel_id = %s", (new_rate, new_rate * 1.5, hotel_id))
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_hotel/<int:hotel_id>')
@admin_required
def delete_hotel(hotel_id):
    with get_db_cursor() as cursor:
        cursor.execute("DELETE FROM bookings WHERE hotel_id = %s", (hotel_id,))
        cursor.execute("DELETE FROM hotels WHERE hotel_id = %s", (hotel_id,))
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
