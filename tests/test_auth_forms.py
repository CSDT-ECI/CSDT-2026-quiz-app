"""Tests for validators in app/auth/forms.py (RegisterForm / ProfileForm)."""


def test_register_form_full_name_rejects_digits(app):
    """validate_full_name rejects names containing digits (line 54)."""
    from app.auth.forms import RegisterForm

    with app.app_context():
        form = RegisterForm(data={
            "full_name": "John2Doe",
            "username": "john2user",
            "email": "john2user@example.com",
            "password": "secret123",
            "password_confirmation": "secret123",
        }, meta={"csrf": False})
        assert form.validate() is False
        assert "numeric" in str(form.full_name.errors[0]).lower()


def test_register_form_username_rejects_space_and_uppercase(app):
    """validate_username rejects spaces and uppercase (line 58)."""
    from app.auth.forms import RegisterForm

    with app.app_context():
        form = RegisterForm(data={
            "full_name": "Valid Name Here",
            "username": "bad User",
            "email": "baduser@example.com",
            "password": "secret123",
            "password_confirmation": "secret123",
        }, meta={"csrf": False})
        assert form.validate() is False
        err = str(form.username.errors[0]).lower()
        assert "space" in err or "uppercase" in err


def test_register_form_email_rejects_invalid_format(app):
    """validate_email rejects addresses that do not match EMAIL_REGEX (line 68)."""
    from app.auth.forms import RegisterForm

    with app.app_context():
        form = RegisterForm(data={
            "full_name": "Valid Name Here",
            "username": "validfmtusr",
            "email": "not-an-email",
            "password": "secret123",
            "password_confirmation": "secret123",
        }, meta={"csrf": False})
        assert form.validate() is False
        assert "invalid" in str(form.email.errors[0]).lower()
