from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import logging
import boto3
import uuid
from botocore.exceptions import ClientError

# ---------- Flask App Setup ----------
app = Flask(__name__)
app.secret_key = 'capture_moments_secret_key_2024'

# ---------- Logging ----------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- AWS DynamoDB Setup ----------
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
users_table = dynamodb.Table('photography_users')
bookings_table = dynamodb.Table('photography_bookings')

# ---------- Routes ----------

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

        try:
            response = users_table.get_item(Key={'username': username})
            user = response.get('Item')

            if user and check_password_hash(user['password'], password):
                session['username'] = username
                session['fullname'] = user['fullname']
                flash('Login successful!', 'success')

                next_page = request.args.get('next')
                return redirect(next_page if next_page else url_for('home'))
            else:
                flash('Invalid username or password', 'error')
        except ClientError as e:
            logger.error(f"Database error during login: {e}")
            flash('An error occurred during login. Please try again.', 'error')

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

        try:
            response = users_table.get_item(Key={'username': username})
            if 'Item' in response:
                flash('Username already exists!', 'error')
                return redirect(url_for('signup'))

            users_table.put_item(Item={
                'username': username,
                'password': generate_password_hash(password),
                'fullname': fullname,
                'email': email,
                'created_at': datetime.now().isoformat()
            })
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))

        except ClientError as e:
            logger.error(f"Database error during signup: {e}")
            flash('An error occurred during registration. Please try again.', 'error')

    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('fullname', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))


@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login', next=request.path))
    return render_template('home.html', username=session['username'])


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/photographers')
def photographers():
    return render_template('photographers.html')


@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if 'username' not in session:
        flash('Please login to book a photographer', 'error')
        return redirect(url_for('login', next=request.path))

    event_type = request.args.get('event', '')

    if request.method == 'POST':
        try:
            response = users_table.get_item(Key={'username': session['username']})
            user = response.get('Item', {})

            required_fields = ['event_type', 'photographer', 'start_date', 'end_date', 'name', 'email', 'phone', 'package', 'payment']
            missing_fields = [field for field in required_fields if not request.form.get(field)]

            if missing_fields:
                flash(f"Please fill all required fields: {', '.join(missing_fields)}", 'error')
                return redirect(url_for('booking', event=event_type))

            booking_id = str(uuid.uuid4())
            booking_data = {
                'booking_id': booking_id,
                'username': session['username'],
                'user': session['fullname'],
                'user_email': user.get('email', ''),
                'name': request.form['name'],
                'email': request.form['email'],
                'phone': request.form['phone'],
                'event_type': request.form['event_type'],
                'photographer': request.form['photographer'],
                'start_date': request.form['start_date'],
                'end_date': request.form['end_date'],
                'package': request.form['package'],
                'payment_method': request.form['payment'],
                'notes': request.form.get('notes', ''),
                'booking_date': datetime.now().isoformat(),
                'status': 'Confirmed'
            }

            bookings_table.put_item(Item=booking_data)
            logger.info(f"Booking created with ID: {booking_id}")
            session['last_booking_id'] = booking_id

            return redirect(url_for('success'))

        except Exception as e:
            logger.error(f"Error in booking form: {str(e)}")
            flash(f'An error occurred: {str(e)}', 'error')
            return redirect(url_for('booking', event=event_type))

    return render_template('booking.html', event_type=event_type)


@app.route('/success')
def success():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('success.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


# ---------- App Startup ----------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
