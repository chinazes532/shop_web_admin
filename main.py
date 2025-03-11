from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://gen_user:h9tHujOOdgO)m=@109.73.206.226:5432/default_db'
db = SQLAlchemy(app)


class Texts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tg_id = db.Column(db.BigInteger, nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    ref_link = db.Column(db.Text, nullable=False)
    invited_by = db.Column(db.BigInteger, nullable=True)
    ref_count = db.Column(db.Integer, nullable=False)
    balance = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Text, nullable=False)


class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)


class Percents(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, nullable=False)


class promocodes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    percent = db.Column(db.Integer, nullable=False)
    count = db.Column(db.Integer, nullable=False)
    end_date = db.Column(db.Text, nullable=False)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/texts')
def texts():
    texts = Texts.query.order_by(Texts.id).all()  # Сортировка по id
    return render_template('texts.html', texts=texts)


@app.route('/edit_text/<int:id>', methods=['GET', 'POST'])
def edit_text(id):
    text = Texts.query.get_or_404(id)
    if request.method == 'POST':
        text.text = request.form['text']
        db.session.commit()
        return redirect(url_for('texts'))
    return render_template('edit_text.html',
                           text=text)


@app.route('/percent')
def percents():
    percents = Percents.query.order_by(Percents.id).all()  # Сортировка по id
    return render_template('percents.html',
                           percents=percents)


@app.route('/edit_percent/<int:id>', methods=['GET', 'POST'])
def edit_percent(id):
    percent = Percents.query.get_or_404(id)
    if request.method == 'POST':
        try:
            percent.count = int(request.form['count'])  # Преобразуем в число
            db.session.commit()
            return redirect(url_for('percents'))
        except ValueError:
            # Обработка ошибки, если введенное значение не является числом
            flash('Пожалуйста, введите корректное число.', 'danger')
            return render_template('edit_percent.html', percent=percent)
    return render_template('edit_percent.html', percent=percent)


@app.route('/users')
def users():
    users = Users.query.order_by(Users.id).all()  # Сортировка по id
    return render_template('users.html',
                           users=users)


@app.route('/categories')
def categories():
    categories = Categories.query.order_by(Categories.id).all()  # Сортировка по id
    return render_template('categories.html',
                           categories=categories)


@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        category = Categories(name=request.form['name'])
        db.session.add(category)
        db.session.commit()
        return redirect(url_for('categories'))
    return render_template('add_category.html')


@app.route('/edit_category/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    category = Categories.query.get_or_404(id)
    if request.method == 'POST':
        if 'name' in request.form:  # Проверка на наличие поля 'name'
            category.name = request.form['name']
            db.session.commit()
            return redirect(url_for('categories'))
        else:
            # Обработка случая, когда поле 'name' отсутствует
            flash('Ошибка: название категории не может быть пустым.', 'danger')
            return render_template('edit_category.html', category=category)
    return render_template('edit_category.html', category=category)


@app.route('/delete_category/<int:id>', methods=['GET', 'POST'])
def delete_category(id):
    category = Categories.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('categories'))


@app.route('/products')
def products():
    products = Products.query.order_by(Products.id).all()
    categories = {category.id: category.name for category in Categories.query.all()}  # Создаем словарь для быстрого доступа к названиям категорий
    for product in products:
        product.category_name = categories.get(product.category_id)  # Предполагается, что у продукта есть поле category_id
    return render_template('products.html', products=products)


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product = Products(title=request.form['title'],
                           description=request.form['description'],
                           price=request.form['price'],
                           category_id=request.form['category_id'])
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('products'))

    categories = Categories.query.all()
    return render_template('add_product.html', categories=categories)


@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = Products.query.get_or_404(id)
    if request.method == 'POST':
        product.title = request.form['title']
        product.description = request.form['description']
        product.price = request.form['price']
        product.category_id = request.form['category_id']
        db.session.commit()
        return redirect(url_for('products'))
    categories = Categories.query.all()
    return render_template('edit_product.html', product=product, categories=categories)


@app.route('/delete_product/<int:id>', methods=['GET', 'POST'])
def delete_product(id):
    product = Products.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('products'))


@app.route('/promocodes')
def promo_codes_func():
    promo_codes = promocodes.query.order_by(promocodes.id).all()  # Сортировка по id
    return render_template('promo_codes.html',
                           promo_codes=promo_codes)


@app.route('/add_promocode', methods=['GET', 'POST'])
def add_promocode():
    if request.method == 'POST':
        promo_code = promocodes(name=request.form['name'],
                                percent=request.form['percent'],
                                count=request.form['count'],
                                end_date=request.form['end_date'])
        db.session.add(promo_code)
        db.session.commit()
        return redirect(url_for('promo_codes_func'))
    return render_template('add_promocode.html')


@app.route('/edit_promocode/<int:id>', methods=['GET', 'POST'])
def edit_promocode(id):
    promo_code = promocodes.query.get_or_404(id)
    if request.method == 'POST':
        promo_code.name = request.form['name']
        promo_code.percent = request.form['percent']
        promo_code.count = request.form['count']
        promo_code.end_date = request.form['end_date']
        db.session.commit()
        return redirect(url_for('promo_codes_func'))
    return render_template('edit_promocode.html', promo_code=promo_code)


@app.route('/delete_promocode/<int:id>', methods=['GET', 'POST'])
def delete_promocode(id):
    promo_code = promocodes.query.get_or_404(id)
    db.session.delete(promo_code)
    db.session.commit()
    return redirect(url_for('promo_codes_func'))


if __name__ == '__main__':
    app.run()