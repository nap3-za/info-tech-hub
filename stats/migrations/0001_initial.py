# Generated by Django 3.2.8 on 2021-12-14 13:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Interactions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('likes', models.IntegerField(blank=True, default=0, null=True, verbose_name='likes')),
                ('dislikes', models.IntegerField(blank=True, default=0, null=True, verbose_name='dislikes')),
                ('comments', models.IntegerField(blank=True, default=0, null=True, verbose_name='comments')),
                ('sent_friendreq', models.IntegerField(blank=True, default=0, null=True, verbose_name='sent_friendreq')),
                ('received_friendreq', models.IntegerField(blank=True, default=0, null=True, verbose_name='received_friendreq')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='interactions_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(choices=[('Account', 'Account'), ('Post', 'Post'), ('Poll', 'Poll'), ('Resource', 'Resource'), ('Comment', 'Comment')], max_length=500, verbose_name='subject')),
                ('subject_id', models.IntegerField(default=0, verbose_name='subject_id')),
                ('reason', models.CharField(default='default', max_length=1000, verbose_name='reason')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserAppData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_count', models.IntegerField(blank=True, default=0, null=True, verbose_name='questions')),
                ('feedback_count', models.IntegerField(blank=True, default=0, null=True, verbose_name='feedback')),
                ('content_count', models.IntegerField(blank=True, default=0, null=True, verbose_name='content_count')),
                ('positive_responses', models.IntegerField(blank=True, default=0, null=True, verbose_name='positive_responses')),
                ('negative_responses', models.IntegerField(blank=True, default=0, null=True, verbose_name='negative_responses')),
                ('Interactions', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='interactions', to='stats.interactions')),
                ('reports', models.ManyToManyField(blank=True, related_name='reports', to='stats.Report')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='appdata_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
