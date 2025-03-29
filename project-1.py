



from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Sample product data (replace with your actual data)
products = [
    {'id': 1, 'name': 'Handwoven Rug', 'price': 50.00, 'image': 'rug.jpg', 'description': 'Beautiful handwoven rug from India'},
    {'id': 2, 'name': 'Ceramic Vase', 'price': 25.00, 'image': 'vase.jpg', 'description': 'Handcrafted ceramic vase from Mexico'},
    {'id': 3, 'name': 'Wooden Sculpture', 'price': 75.00, 'image': 'sculpture.jpg', 'description': 'Intricate wooden sculpture from Bali'},
]

@app.route('/')
def index():
  return render_template('index.html', products=products)

@app.route('/product/<int:product_id>')
def product(product_id):
  product = next((p for p in products if p['id'] == product_id), None)
  if product:
    return render_template('product.html', product=product)
  else:
    return "Product not found", 404

@app.route('/cart', methods=['GET', 'POST'])
def cart():
  if request.method == 'POST':
    # Add product to cart (implementation depends on your cart system)
    product_id = int(request.form['product_id'])
    # ... (add product_id to cart)
    return redirect(url_for('cart'))
  else:
    # Display cart contents
    # ... (retrieve cart contents)
    return render_template('cart.html')

@app.route('/checkout')
def checkout():
  # Implement checkout process (payment gateway integration, order confirmation, etc.)
  return render_template('checkout.html')

if __name__ == '__main__':
  app.run(debug=True)
