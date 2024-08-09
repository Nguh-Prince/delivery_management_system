from django.apps import AppConfig

class DmsConfig(AppConfig):
    name = 'DMS'
    def ready(self):
        import DMS.signals
