from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data import db_session
from data.cards import Cards
from data.users import User
from forms.user import RegisterForm, LoginForm
from forms.cards import CardsForm
from data.cashbacks import Cashback
from forms.cashbacks import CashbackForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init("db/database.db")
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    app.run()


@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        cards = db_sess.query(Cards).filter(
            (Cards.user == current_user) | (Cards.is_private != True)).all()
        cashback_entries = db_sess.query(Cashback).filter(
            (Cashback.user_id == current_user.id) | (Cards.is_private != True)).all()
    else:
        cards = db_sess.query(Cards).filter(Cards.is_private != True).all()
        cashback_entries = []
    sum_balance = sum(card.balance for card in cards if card.balance is not None)
    cashback_summary = {}
    for entry in cashback_entries:
        cashback_summary.setdefault(entry.category, 0)
        cashback_summary[entry.category] += entry.cashback_expected
    return render_template("index.html", cards=cards, sum_balance=sum_balance,
                           cashback_summary=cashback_summary)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/cards', methods=['GET', 'POST'])
@login_required
def add_cards():
    form = CardsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        cards = Cards()
        cards.title = form.title.data
        cards.balance = float(form.balance.data)
        cards.is_private = True
        current_user.card.append(cards)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    elif request.method == 'POST':
        return render_template('cards.html', title='Добавление новой карты',
                               form=form, message="Заполните все поля корректно")
    return render_template('cards.html', title='Добавление новой карты', form=form)


@app.route('/cards/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_cards(id):
    form = CardsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        cards = db_sess.query(Cards).filter(Cards.id == id,
                                          Cards.user == current_user
                                          ).first()
        if cards:
            form.title.data = cards.title
            form.balance.data = cards.balance
        #  else:
            #  abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        cards = db_sess.query(Cards).filter(Cards.id == id,
                                          Cards.user == current_user
                                          ).first()
        if cards:
            cards.title = form.title.data
            cards.balance = float(form.balance.data)
            cards.is_private = True
            db_sess.commit()
            return redirect('/')
    return render_template('cards.html',
                           title='Редактирование карты',
                           form=form
                           )


@app.route('/cards_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def cards_delete(id):
    db_sess = db_session.create_session()
    cards = db_sess.query(Cards).filter(Cards.id == id,
                                      Cards.user == current_user
                                      ).first()
    if cards:
        db_sess.delete(cards)
        db_sess.commit()
    return redirect('/')


@app.route('/add_cashback', methods=['GET', 'POST'])
@login_required
def add_cashback():
    form = CashbackForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        cashback_value = float(form.amount_spent.data) * float(form.cashback_percent.data) / 100
        cashback = Cashback(
            category=form.category.data,
            amount_spent=form.amount_spent.data,
            cashback_expected=cashback_value,
            user_id=current_user.id
        )
        db_sess.add(cashback)
        db_sess.commit()
        return redirect('/')
    db_sess = db_session.create_session()
    if not db_sess.query(Cards).filter(Cards.user == current_user).first():
        message = "Сначала добавьте хотя бы одну карту."
    elif request.method == "POST":
        message = "Заполните все поля корректно."
        return render_template('add_cashback.html', title="Добавление траты", form=form, message=message)
    else:
        message = None
    return render_template('add_cashback.html', title="Добавление траты", form=form, message=message)


if __name__ == '__main__':
    main()