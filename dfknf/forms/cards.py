from flask_wtf import FlaskForm
from wtforms import StringField, FloatField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class CardsForm(FlaskForm):
    title = StringField('Название карты', validators=[DataRequired()])
    balance = FloatField("Баланс", validators=[DataRequired()])
    submit = SubmitField('Добавить')