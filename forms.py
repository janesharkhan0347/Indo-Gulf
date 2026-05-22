from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, PasswordField, SelectField, TextAreaField,
                     IntegerField, FloatField, BooleanField, SubmitField,
                     SelectMultipleField, widgets)
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
                                 Optional, NumberRange, ValidationError)


# ---------- Auth ----------

class LoginForm(FlaskForm):
    email       = StringField('Email', validators=[DataRequired(), Email()])
    password    = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit      = SubmitField('Login')


class BuyerRegisterForm(FlaskForm):
    name         = StringField('Full Name', validators=[DataRequired(), Length(2, 100)])
    email        = StringField('Email', validators=[DataRequired(), Email()])
    password     = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    confirm      = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    company_name = StringField('Company Name', validators=[DataRequired(), Length(2, 200)])
    country      = SelectField('Country', choices=[
        ('UAE', 'UAE 🇦🇪'), ('Saudi Arabia', 'Saudi Arabia 🇸🇦'),
        ('Qatar', 'Qatar 🇶🇦'), ('Oman', 'Oman 🇴🇲'),
        ('Kuwait', 'Kuwait 🇰🇼'), ('Bahrain', 'Bahrain 🇧🇭')
    ])
    phone        = StringField('Phone Number', validators=[DataRequired(), Length(7, 30)])
    submit       = SubmitField('Register as Buyer')


class SellerRegisterForm(FlaskForm):
    name         = StringField('Full Name', validators=[DataRequired(), Length(2, 100)])
    email        = StringField('Email', validators=[DataRequired(), Email()])
    password     = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    confirm      = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    company_name = StringField('Company Name', validators=[DataRequired(), Length(2, 200)])
    gst_number   = StringField('GST Number', validators=[Optional(), Length(max=50)])
    iec_code     = StringField('IEC Export Code', validators=[Optional(), Length(max=50)])
    country      = SelectField('Country', choices=[('India', 'India 🇮🇳')])
    phone        = StringField('Phone Number', validators=[DataRequired(), Length(7, 30)])
    submit       = SubmitField('Register as Seller/Exporter')


# ---------- Product ----------

class ProductForm(FlaskForm):
    title            = StringField('Product Title', validators=[DataRequired(), Length(3, 255)])
    category_id      = SelectField('Category', coerce=int, validators=[DataRequired()])
    description      = TextAreaField('Description', validators=[DataRequired(), Length(20)])
    price            = FloatField('Price (USD)', validators=[DataRequired(), NumberRange(min=0)])
    unit             = SelectField('Unit', choices=[
        ('kg','kg'), ('ton','ton'), ('piece','piece'),
        ('box','box'), ('liter','liter'), ('dozen','dozen')
    ])
    moq              = IntegerField('MOQ (Min Order Qty)', validators=[DataRequired(), NumberRange(min=1)])
    export_countries = StringField('Export Countries (comma-separated)',
                                   validators=[Optional()],
                                   default='UAE,Saudi Arabia,Qatar,Oman,Kuwait,Bahrain')
    availability     = BooleanField('Available for Export', default=True)
    image            = FileField('Product Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'webp', 'gif'], 'Images only!')
    ])
    submit           = SubmitField('Save Product')


# ---------- RFQ ----------

class RFQForm(FlaskForm):
    quantity = IntegerField('Quantity Required', validators=[DataRequired(), NumberRange(min=1)])
    unit     = SelectField('Unit', choices=[
        ('kg','kg'), ('ton','ton'), ('piece','piece'),
        ('box','box'), ('liter','liter'), ('dozen','dozen')
    ])
    message  = TextAreaField('Message to Seller', validators=[DataRequired(), Length(10, 2000)])
    submit   = SubmitField('Send Request for Quote')


# ---------- Profile ----------

class ProfileForm(FlaskForm):
    name         = StringField('Full Name', validators=[DataRequired(), Length(2, 100)])
    company_name = StringField('Company Name', validators=[Optional()])
    phone        = StringField('Phone Number', validators=[Optional(), Length(7, 30)])
    about        = TextAreaField('About / Bio', validators=[Optional(), Length(max=1000)])
    website      = StringField('Website', validators=[Optional(), Length(max=255)])
    logo         = FileField('Company Logo', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images only!')
    ])
    submit       = SubmitField('Update Profile')