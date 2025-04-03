import os
import sys
import sqlite3
import traceback
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from datetime import datetime

# Absolute path to the project directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Directories
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
DB_PATH = os.path.join(BASE_DIR, 'global_crafts.db')

# Ensure directories exist
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATE_DIR, exist_ok=True)

# Create Flask app
app = Flask(__name__, 
            static_folder=STATIC_DIR, 
            template_folder=TEMPLATE_DIR)

def create_database():
    """Initialize the database with tables and sample data."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create products table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            image TEXT,
            stock INTEGER NOT NULL
        )
        ''')
        
        # Create orders table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            quantity INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            customer_address TEXT NOT NULL,
            total_price REAL NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        ''')
        
        # Create cart table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            product_id INTEGER,
            quantity INTEGER NOT NULL,
            PRIMARY KEY (product_id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        ''')
        
        # Insert sample products if table is empty
        cursor.execute('SELECT COUNT(*) FROM products')
        if cursor.fetchone()[0] == 0:
            sample_products = [
                ('Handmade Ceramic Vase', 'Beautiful hand-crafted ceramic vase', 49.99, 'vase.jpg', 10),
                ('Silk Scarf', 'Luxurious hand-woven silk scarf', 79.99, 'scarf.jpg', 15),
                ('Wooden Sculpture', 'Intricate wooden sculpture from local artisans', 129.99, 'sculpture.jpg', 5),
                ('Jeans pants','Beautiful printed jeans', 49.00, 'jeans.jpg', 10),
            ]
            cursor.executemany('''
                INSERT INTO products (name, description, price, image, stock) 
                VALUES (?, ?, ?, ?, ?)
            ''', sample_products)
        
        conn.commit()
        conn.close()
        print("Database created successfully")
    except Exception as e:
        print(f"Database creation error: {e}")
        print(traceback.format_exc())
        raise

# Create database on startup
create_database()

def add_to_cart(product_id, quantity=1):
    """Add a product to the cart."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if product exists
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            conn.close()
            return False, "Product not found"
        
        # Check stock availability
        if product[5] < quantity:
            conn.close()
            return False, "Insufficient stock"
        
        # Insert or update cart item
        cursor.execute('''
            INSERT OR REPLACE INTO cart 
            (product_id, quantity) 
            VALUES (?, ?)
        ''', (product_id, quantity))
        
        conn.commit()
        conn.close()
        return True, "Product added to cart"
    
    except Exception as e:
        print(f"Add to cart error: {e}")
        return False, str(e)

@app.route('/')
def home():
    """Render home page with product listings."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        
        conn.close()
        return render_template('home.html', products=products)
    except Exception as e:
        print(f"Home page error: {e}")
        print(traceback.format_exc())
        return f"An error occurred: {e}", 500

@app.route('/order/<int:product_id>', methods=['GET', 'POST'])
def order(product_id):
    """Handle product order page."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            conn.close()
            return "Product not found", 404
        
        if request.method == 'POST':
            # Collect form data
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            address = request.form.get('address', '').strip()
            quantity = request.form.get('quantity', 0)
            
            # Validate inputs
            if not all([name, email, address, quantity]):
                conn.close()
                return "Please fill in all fields", 400
            
            try:
                quantity = int(quantity)
                if quantity <= 0:
                    conn.close()
                    return "Quantity must be positive", 400
                
                # Calculate total price
                total_price = product[3] * quantity
                
                # Insert order
                cursor.execute('''
                    INSERT INTO orders 
                    (product_id, quantity, customer_name, customer_email, customer_address, total_price) 
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (product_id, quantity, name, email, address, total_price))
                
                conn.commit()
                order_id = cursor.lastrowid
                conn.close()
                
                return redirect(url_for('order_confirmation', order_id=order_id))
            
            except ValueError:
                conn.close()
                return "Invalid quantity", 400
        
        conn.close()

        return render_template('order.html', product=product)
    
    except Exception as e:
        print(f"Order page error: {e}")
        print(traceback.format_exc())
        return f"An error occurred: {e}", 500

@app.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    """Render order confirmation page."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Fetch order details with product information
        cursor.execute('''
            SELECT 
                o.id, o.quantity, o.customer_name, o.customer_email, o.customer_address, 
                o.total_price, p.name, p.description, p.image 
            FROM orders o 
            JOIN products p ON o.product_id = p.id 
            WHERE o.id = ?
        ''', (order_id,))
        order = cursor.fetchone()
        
        conn.close()
        
        if not order:
            return "Order not found", 404
        
        current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        return render_template('order_confirmation.html', order=order, current_time=current_time)
    
    except Exception as e:
        print(f"Order confirmation error: {e}")
        print(traceback.format_exc())
        return f"An error occurred: {e}", 500

if __name__ == '__main__':
    print("Starting Global Crafts E-Commerce Application")
    print(f"Database located at: {DB_PATH}")
    print(f"Static files served from: {STATIC_DIR}")
    print(f"Templates loaded from: {TEMPLATE_DIR}")
    print("Open http://127.0.0.1:5000/ in your web browser")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
