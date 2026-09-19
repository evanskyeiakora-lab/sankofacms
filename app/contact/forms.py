from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    TextAreaField,
    SubmitField
)

from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    Optional
)


class ContactForm(FlaskForm):

    name = StringField(
        "Full Name",
        validators=[
            DataRequired(),
            Length(min=2, max=150)
        ]
    )

    email = StringField(
        "Email Address",
        validators=[
            DataRequired(),
            Email(),
            Length(max=255)
        ]
    )

    phone = StringField(
        "Phone Number",
        validators=[
            Optional(),
            Length(max=50)
        ]
    )

    subject = StringField(
        "Subject",
        validators=[
            DataRequired(),
            Length(min=3, max=255)
        ]
    )

    message = TextAreaField(
        "Message",
        validators=[
            DataRequired(),
            Length(min=10, max=5000)
        ]
    )

    submit = SubmitField(
        "Send Message"
    )