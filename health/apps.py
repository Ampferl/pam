from django.apps import AppConfig


class HealthConfig(AppConfig):
    name = 'health'

    def ready(self):
        from . import calendar_sources
