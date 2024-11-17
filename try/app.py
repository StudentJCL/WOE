from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages and session management

# MySQL Database connection
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',  # Your MySQL host, default is 'localhost'
        user='root',  # Your MySQL username
        password='',  # Your MySQL password
        database='ecomdb'  # The database you want to connect to
    )
    return conn

# Route to display the homepage
@app.route('/')
def homepage():
    return render_template('homepage.html')

# Route to display the registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        email = request.form['email']
        password = request.form['password']
        role = 'customer'  # Default role is 'customer'

        # Insert the user data into the MySQL database
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                '''INSERT INTO users (email, password, role) 
                VALUES (%s, %s, %s)''', (email, password, role)
            )
            conn.commit()

            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

        except mysql.connector.Error as err:
            flash(f"Error: {err}", 'danger')
        finally:
            conn.close()

    return render_template('register.html')

# Route to display the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and user[2] == password:
            session['user_id'] = user[0]
            role = user[3]

            flash('Login successful!', 'success')

            if role == 'superadmin':
                return redirect(url_for('superadmin_dashboard'))
            elif role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('homepage'))

        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Route to handle logout functionality
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('homepage'))

# Admin route
@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

# Superadmin route
@app.route('/superadmin_dashboard')
def superadmin_dashboard():
    return render_template('superadmin_dashboard.html')

# Seller registration route
@app.route('/seller-registration', methods=['GET', 'POST'])
def seller_registration():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        phonenumber = request.form['phonenumber']
        address = request.form['address']
        businessname = request.form['businessname']
        description = request.form['description']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            query = """
                INSERT INTO sellers (firstname, lastname, email, phonenumber, address, businessname, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (firstname, lastname, email, phonenumber, address, businessname, description)
            cursor.execute(query, values)
            conn.commit()

            flash('Seller registered successfully!', 'success')
            return redirect('/seller-registration')

        except mysql.connector.Error as err:
            flash(f"Error registering seller: {err}", 'danger')

        finally:
            conn.close()

    return render_template('seller_registration.html')

# Route to manage sellers
@app.route('/manage_sellers')
def manage_sellers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT sellerid, firstname, lastname, email, phonenumber, address, businessname, description, createdtime, status 
            FROM sellers
        """)
        sellers = cursor.fetchall()

    except Exception as e:
        print(f"Error fetching sellers data: {e}")
        sellers = []

    finally:
        cursor.close()
        conn.close()

    return render_template('manage_sellers.html', sellers=sellers)

# Route to approve seller
@app.route('/approve_seller/<int:sellerid>', methods=['POST'])
def approve_seller(sellerid):
    conn = get_db_connection()

    try:
        cursor = conn.cursor()
        query = "UPDATE sellers SET status = 'Approved' WHERE sellerid = %s"
        cursor.execute(query, (sellerid,))
        conn.commit()

        flash("Seller approved successfully!", category="success")
        return redirect(url_for('manage_sellers'))

    except Error as e:
        flash(f"Error: {e}", category="danger")
        return redirect(url_for('manage_sellers'))

    finally:
        if conn:
            conn.close()

# Route to decline seller
@app.route('/decline_seller/<int:sellerid>', methods=['POST'])
def decline_seller(sellerid):
    conn = get_db_connection()

    try:
        cursor = conn.cursor()
        query = "UPDATE sellers SET status = 'Declined' WHERE sellerid = %s"
        cursor.execute(query, (sellerid,))
        conn.commit()

        flash("Seller declined successfully!", category="danger")
        return redirect(url_for('manage_sellers'))

    except Error as e:
        flash(f"Error: {e}", category="danger")
        return redirect(url_for('manage_sellers'))

    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
