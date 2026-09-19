from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed

from wtforms import (
    StringField,
    TextAreaField,
    DateField,
    TimeField,
    IntegerField,
    BooleanField,
    SubmitField
)

from wtforms.validators import (
    DataRequired,
    Optional,
    URL,
    NumberRange,
    ValidationError
)


class EventForm(FlaskForm):

    # ==========================================================
    # TITLE
    # ==========================================================

    title = StringField(
        "Event Title",
        validators=[
            DataRequired(
                message="Please enter the event title."
            )
        ]
    )

    # ==========================================================
    # DESCRIPTION
    # ==========================================================

    description = TextAreaField(
        "Description",
        validators=[
            Optional()
        ]
    )

    # ==========================================================
    # VENUE
    # ==========================================================

    venue = StringField(
        "Venue",
        validators=[
            Optional()
        ]
    )

    # ==========================================================
    # ORGANIZER
    # ==========================================================

    organizer = StringField(
        "Organizer",
        validators=[
            Optional()
        ]
    )

    # ==========================================================
    # START DATE
    # ==========================================================

    start_date = DateField(
        "Start Date",
        format="%Y-%m-%d",
        validators=[
            DataRequired(
                message="Please select the event start date."
            )
        ]
    )

    # ==========================================================
    # END DATE
    # ==========================================================

    end_date = DateField(
        "End Date",
        format="%Y-%m-%d",
        validators=[
            Optional()
        ]
    )

    # ==========================================================
    # START TIME
    # ==========================================================

    start_time = TimeField(
        "Start Time",
        format="%H:%M",
        validators=[
            Optional()
        ]
    )

    # ==========================================================
    # END TIME
    # ==========================================================

    end_time = TimeField(
        "End Time",
        format="%H:%M",
        validators=[
            Optional()
        ]
    )

    # ==========================================================
    # REGISTRATION LINK
    # ==========================================================

    registration_link = StringField(
        "Registration Link",
        validators=[
            Optional(),
            URL(
                message="Please enter a valid registration URL."
            )
        ]
    )

    # ==========================================================
    # FEATURED IMAGE
    # ==========================================================

    featured_image = FileField(
        "Featured Image",
        validators=[
            Optional(),
            FileAllowed(
                [
                    "jpg",
                    "jpeg",
                    "png",
                    "webp"
                ],
                "Images only! Allowed formats: JPG, JPEG, PNG and WEBP."
            )
        ]
    )

    # ==========================================================
    # FEATURED EVENT
    # ==========================================================

    is_featured = BooleanField(
        "Featured Event",
        default=False
    )

    # ==========================================================
    # PUBLISHED
    # ==========================================================

    is_published = BooleanField(
        "Publish Event",
        default=True
    )

    # ==========================================================
    # DISPLAY ORDER
    # ==========================================================

    display_order = IntegerField(
        "Display Order",
        default=1,
        validators=[
            Optional(),
            NumberRange(
                min=1,
                message="Display order must be 1 or greater."
            )
        ]
    )

    # ==========================================================
    # SUBMIT
    # ==========================================================

    submit = SubmitField(
        "Save Event"
    )

    # ==========================================================
    # EVENT DATE/TIME VALIDATION
    # ==========================================================

    def validate_end_date(self, field):

        """
        Make sure the end date is not before
        the start date.
        """

        if (
            field.data
            and self.start_date.data
            and field.data < self.start_date.data
        ):

            raise ValidationError(
                "End date cannot be earlier than the start date."
            )

    # ==========================================================
    # END TIME VALIDATION
    # ==========================================================

    def validate_end_time(self, field):

        """
        Make sure the end time is not before
        the start time when the event occurs
        on the same day.
        """

        if not field.data or not self.start_time.data:
            return

        # ------------------------------------------------------
        # Determine whether this is a single-day event
        # ------------------------------------------------------

        same_day = False

        if self.start_date.data:

            if self.end_date.data:

                same_day = (
                    self.end_date.data
                    == self.start_date.data
                )

            else:

                # No end date means the event is treated
                # as a single-day event.
                same_day = True

        # ------------------------------------------------------
        # Compare times
        # ------------------------------------------------------

        if same_day:

            if field.data < self.start_time.data:

                raise ValidationError(
                    "End time cannot be earlier than the start time."
                )

    # ==========================================================
    # FORM-LEVEL VALIDATION
    # ==========================================================

    def validate(self, extra_validators=None):

        """
        Additional validation that checks the
        relationship between event dates and times.
        """

        if not super().validate(extra_validators):

            return False

        # ------------------------------------------------------
        # START DATE MUST EXIST
        # ------------------------------------------------------

        if not self.start_date.data:

            return False

        # ------------------------------------------------------
        # END DATE CANNOT BE BEFORE START DATE
        # ------------------------------------------------------

        if self.end_date.data:

            if self.end_date.data < self.start_date.data:

                self.end_date.errors.append(
                    "End date cannot be earlier than the start date."
                )

                return False

        # ------------------------------------------------------
        # SAME-DAY TIME VALIDATION
        # ------------------------------------------------------

        if (
            self.start_time.data
            and self.end_time.data
        ):

            same_day = False

            if self.end_date.data:

                same_day = (
                    self.end_date.data
                    == self.start_date.data
                )

            else:

                same_day = True

            if same_day:

                if self.end_time.data < self.start_time.data:

                    self.end_time.errors.append(
                        "End time cannot be earlier than the start time."
                    )

                    return False

        # ------------------------------------------------------
        # VALID
        # ------------------------------------------------------

        return True