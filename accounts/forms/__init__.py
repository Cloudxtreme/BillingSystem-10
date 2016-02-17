from register import Registration_Form
from sign_in import Sign_In_Form

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from accounts.models import User

class UserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """

    def __init__(self, *args, **kargs):
        super(UserCreationForm, self).__init__(*args, **kargs)

    class Meta:
        model = User
        fields = ("email",)

class UserChangeForm(UserChangeForm):
    """
    A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    def __init__(self, *args, **kargs):
        super(UserChangeForm, self).__init__(*args, **kargs)

    class Meta:
        model = User
        fields = ('email',)