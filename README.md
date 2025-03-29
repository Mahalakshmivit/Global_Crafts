from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Sample data representing crafts
crafts = [
    {"id": 1, "name": "Handwoven Basket", "origin": "Ghana", "price": 25.00},
    {"id": 2, "name": "Ceramic Vase", "origin": "Mexico", "price": 40.00},
    {"id": 3, "name": "Silk Scarf", "origin": "India", "price": 30.00}
]

@app.route('/')
def home():
    return render_template('home.html', crafts=crafts)

@app.route('/add', methods=['GET', 'POST'])
def add_craft():
    if request.method == 'POST':
        name = request.form['name']
        origin = request.form['origin']
        price = float(request.form['price'])
        new_craft = {"id": len(crafts) + 1, "name": name, "origin": origin, "price": price}
        crafts.append(new_craft)
        return redirect(url_for('home'))
    return render_template('add_craft.html')

if __name__ == '__main__':
    app.run(debug=True)
# Global_Crafts