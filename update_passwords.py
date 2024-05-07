from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
import os
import django

# Set the Django settings module for the script
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "/DjangoWebProject1.settings")
django.setup()

# Now you can import Django modules
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

def update_user_passwords():
    # Retrieve all users from the database
    users = User.objects.all()

    for user in users:
        # Assuming 'user.password' is the plaintext password stored in the database
        old_password = user.password

        # Hash the old password
        hashed_password = make_password(old_password)

        # Update the user's password in the database
        user.password = hashed_password
        user.save()

if __name__ == '__main__':
    update_user_passwords()