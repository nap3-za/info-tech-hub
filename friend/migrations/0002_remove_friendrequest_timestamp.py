# Generated by Django 3.2.8 on 2021-12-11 07:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('friend', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='friendrequest',
            name='timestamp',
        ),
    ]