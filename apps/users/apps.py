from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class UsersConfig(AppConfig):
    name = 'apps.users'
    verbose_name = _('users')

    def ready(self):
        import apps.users.signals
