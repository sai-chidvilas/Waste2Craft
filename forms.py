from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Length

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=150)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    role = SelectField('Role', choices=[('customer', 'Customer'), ('waste_buyer', 'Waste Buyer'), ('staff', 'Staff')], validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('customer', 'Customer'), ('waste_buyer', 'Waste Buyer'), ('staff', 'Staff')], validators=[DataRequired()])
    submit = SubmitField('Login')

class WasteCollectionForm(FlaskForm):
    waste_details = TextAreaField('Waste Details', validators=[DataRequired()])
    weight = FloatField('Weight (kg)', validators=[DataRequired()])
    waste_type = SelectField('Waste Type', choices=[('plastic', 'Plastic'), ('metal', 'Metal'), ('fabric', 'Fabric'), ('wood', 'Wood')], validators=[DataRequired()])
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    submit = SubmitField('Request Collection')

class WasteListingForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = SelectField('Category', choices=[('plastic', 'Plastic'), ('metal', 'Metal'), ('fabric', 'Fabric'), ('wood', 'Wood')], validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    submit = SubmitField('List Waste')

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    submit = SubmitField('Add Product')