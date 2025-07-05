from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

# ----------- Flask Setup ------------
app = Flask(__name__)
app.secret_key = 'mock_testing_secret_key'

# ----------- Mock In-Memory Storage ------------
mock_users = {
    "alice": {
        "fullname": "Alice Johnson",
        "email": "alice@example.com",
        "password": generate_password_hash("alicepass"),
        "created_at": "2025-07-01T09:00:00"
    },
    "bob": {
        "fullname": "Bob Singh",
        "email": "bob@example.com",
        "password": generate_password_hash("bobpass"),
        "created_at": "2025-07-02T09:30:00"
    },
    "charlie": {
        "fullname": "Charlie Patel",
        "email": "charlie@example.com",
        "password": generate_password_hash("charliepass"),
        "created_at": "2025-07-03T10:00:00"
    }
}

mock_bookings = {
    "bkg-1": {
        "booking_id": "bkg-1",
        "username": "alice",
        "fullname": "Alice Johnson",
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "phone": "9876543210",
        "event_type": "Wedding",
        "photographer": "Lens Masters",
        "start_date": "2025-08-15",
        "end_date": "2025-08-16",
        "package": "Gold",
        "payment_method": "Credit Card",
        "notes": "Outdoor shoot required",
        "status": "Confirmed",
        "created_at": "2025-07-04T10:00:00"
    },
    "bkg-2": {
        "booking_id": "bkg-2",
        "username": "bob",
        "fullname": "Bob Singh",
        "name": "Bob Singh",
        "email": "bob@example.com",
        "phone": "9123456780",
        "event_type": "Fashion Show",
        "photographer": "Shutter Studio",
        "start_date": "2025-09-10",
        "end_date": "2025-09-10",
        "package": "Platinum",
        "payment_method": "UPI",
        "notes": "",
        "status": "Confirmed",
        "created_at": "2025-07-04T10:15:00"
    },
    "bkg-3": {
        "booking_id": "bkg-3",
        "username": "charlie",
        "fullname": "Charlie Patel",
        "name": "Charlie Patel",
        "email": "charlie@example.com",
        "phone": "9988776655",
        "event_type": "Baby Shoot",
        "photographer": "Candid Clicks",
        "start_date": "2025-07-20",
        "end_date": "2025-07-20",
        "package": "Silver",
        "payment_method": "Cash",
        "notes": "Indoor studio session",
        "status": "Confirmed",
        "created_at": "2025-07-04T10:30:00"
    }
}

# ----------- Routes ------------

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = mock_users.get(username)
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            session['fullname'] = user['fullname']
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        fullname = request.form['fullname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if username in mock_users:
            flash('Username already exists!', 'error')
            return redirect(url_for('signup'))
        mock_users[username] = {
            'fullname': fullname,
            'email': email,
            'password': generate_password_hash(password),
            'created_at': datetime.now().isoformat()
        }
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('fullname', None)
    flash('Logged out successfully', 'info')
    session.clear
    return redirect(url_for('index'))

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    user_bookings = [b for b in mock_bookings.values() if b['username'] == session['username']]
    return render_template('home.html', username=session['username'], bookings=user_bookings)
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if 'username' not in session:
       
        return redirect(url_for('login'))

  
    photographers = [
        {
            'name': 'Jane Smith',
            'image_url': 'https://images.unsplash.com/photo-1511367461989-f85a21fda167?w=600&q=80',
            'specialty': 'Wedding & Portrait Specialist'
        },
        {
            'name': 'John Doe',
            'image_url': 'https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=600&q=80',
            'specialty': 'Wildlife & Nature Photographer'
        },
        {
            'name': 'Priya Patel',
            'image_url': 'https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?w=600&q=80',
            'specialty': 'Events & Candid Moments'
        },
        {
            'name': 'Alex Lee',
            'image_url': 'https://images.unsplash.com/photo-1465101178521-c1a9136a0b5b?w=600&q=80',
            'specialty': 'Fashion & Editorial Photography'
        },
        {
            'name': 'Sara Kim',
            'image_url': 'https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?w=600&q=80',
            'specialty': 'Travel & Landscape Expert'
        },
        {
            'name': 'Rohit Sharma',
            'image_url': 'https://images.unsplash.com/photo-1519340333755-c1aa5571fd46?w=600&q=80',
            'specialty': 'Corporate & Product Shoots'
        }
    ]
    photographer_name = request.args.get('photographer', '')
    photographer = next((p for p in photographers if p['name'] == photographer_name), None)

    if request.method == 'POST':
        form = request.form
        required_fields = ['event_type', 'photographer', 'start_date', 'end_date', 'name', 'email', 'phone', 'package', 'payment']
        missing = [field for field in required_fields if not form.get(field)]

        if missing:
            flash(f'Missing fields: {", ".join(missing)}', 'error')
            return redirect(url_for('booking', photographer=photographer_name))

        booking_id = str(uuid.uuid4())
        mock_bookings[booking_id] = {
            'booking_id': booking_id,
            'username': session['username'],
            'fullname': session['fullname'],
            'name': form['name'],
            'email': form['email'],
            'phone': form['phone'],
            'event_type': form['event_type'],
            'photographer': form['photographer'],
            'start_date': form['start_date'],
            'end_date': form['end_date'],
            'package': form['package'],
            'payment_method': form['payment'],
            'notes': form.get('notes', ''),
            'status': 'Confirmed',
            'created_at': datetime.now().isoformat()
        }

        session['last_booking_id'] = booking_id
        # flash('Booking successful!', 'success')
        return redirect(url_for('success'))

    return render_template('booking.html', photographer=photographer, photographer_name=photographer_name)

@app.route('/success')
def success():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('success.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/photographers')
def photographers():
    # Just render the static template, do not pass mock_photographers
    return render_template('photographers.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/my_bookings')
def my_bookings():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Get user's bookings from mock data
    user_bookings = [b for b in mock_bookings.values() if b['username'] == session['username']]
    return render_template('success.html')  # Just return success.html as requested

# ---------- Run ----------
if __name__ == '__main__':
    app.run(debug=True)