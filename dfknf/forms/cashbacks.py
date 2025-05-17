from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import DataRequired


class CashbackForm(FlaskForm):
    category = StringField('Категория', validators=[DataRequired()])
    amount_spent = FloatField('Сумма траты', validators=[DataRequired()])
    cashback_percent = FloatField('Процент кэшбэка', validators=[DataRequired()])
    submit = SubmitField('Добавить')