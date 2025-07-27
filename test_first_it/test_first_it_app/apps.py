from django.apps import AppConfig


class TestFirstItAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = 'Тестовое задание от "Первая IT-компания"'
    name = 'test_first_it_app'
