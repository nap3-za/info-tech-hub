# Generated by Django 3.2.8 on 2021-12-13 19:27

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('nomad', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Suggestion',
            new_name='Feedback',
        ),
    ]
