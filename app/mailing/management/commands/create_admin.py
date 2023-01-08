from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
User = get_user_model()


class Command(BaseCommand):

    ADMINS_LIST = [
        {
            "username": "admin",
            "password": "12345",
            "email": "admin@admin.com"
        },
    ]

    def handle(self, *args, **options):
        if User.objects.count() == 0:
            for user in self.ADMINS_LIST:

                username = user["username"]
                password = user["password"]
                email = user["email"]

                print('Creating account for %s ' % (username))

                try:
                    admin = User.objects.create_superuser(
                        username=username, password=password, email=email)
                    admin.is_active = True
                    admin.is_admin = True

                    admin.save()
                except Exception as e:
                    print(e)
        else:
            print('Admin accounts can only be initialized if no Users exist')