from django.contrib.auth.models import User
from onadata.apps.logger.models import XForm
from onadata.apps.logger.models import Instance
from onadata.apps.logger.models import Project
from django.core.management.base import BaseCommand
from django.db import connection


def fetch_user_formbuilder_details(self, user):
    with connection.cursor() as cursor:
        cursor.execute(
            "select * from hub_extrauserdetail where user_id={}".format(
                user.pk))
        cursor.execute(
            "select * from hub_perusersetting where name={}".format(
                user.username))
        rows = cursor.fetchall()
        return rows

    if rows:
        for row in rows:
            row.delete()


def get_user_projects(self, username):  # pylint: disable=R0201
    user = User.objects.get(username=username)
    user_projects = Project.objects.filter(created_by=user).count()

    return user_projects


def get_user_forms(self, username):  # pylint: disable=R0201
    user = User.objects.get(username=username)
    user_forms = XForm.objects.filter(user=user)

    for form in user_forms:
        form_name = form.title
        form_sumbissions = Instance.objects.filter(xform=form).count()

        result = {
            form_name: form_sumbissions,
        }

        return result

    return len(user_forms)


def get_user_account_details(self, username):  # pylint: disable=R0201
    try:
        inactivate_user(self, username)
        self.stdout.write(
            'User {} deleted with success!'.format(username))
    except User.DoesNotExist:
        self.stdout.write('User {} does not exist.' % username)


def inactivate_user(self, username):
    try:
        user = User.objects.get(username=username)
        user.is_active = False
        user.save()
    except User.DoesNotExist:
        self.stdout.write('User {} does not exist.' % username)


def delete_user(self, username):
    try:
        user = User.objects.get(username=username)
        fetch_user_formbuilder_details(self, user)
        user.delete()
    except User.DoesNotExist:
        self.stdout.write('User {} does not exist.' % username)


class Command(BaseCommand):
    help = 'Delete users'

    def add_arguments(self, parser):
        parser.add_argument('user', nargs='*')

        parser.add_argument(
                '--user_input',
                action='store_true',
                help='Confirm deletion of user account',
            )

    def handle(self, *args, **kwargs):
        users = kwargs['user']
        user_input = kwargs['user_input']

        if users and user_input is not None:
            for user in users:
                user_details = user.split(':')
                username = user_details[0]
                user_projects = get_user_projects(self, username)
                user_forms = get_user_forms(self, username)
                if user_input is True:
                    return get_user_account_details(self, username)
                elif user_input is False:
                    return self.stdout.write(
                        'User account {} not deleted.'.format(username))

        user_projects = get_user_projects(self, username)
        user_forms = len(get_user_forms(self, username))
        user_input = input("User has {} projects, {} forms. \
            Do you wish to continue deleting this account?".format(
            user_projects, user_forms))

        if user_input is True:
            get_user_account_details(self, username)
        else:
            self.stdout.write('User account {} not deleted.'.format(username))
