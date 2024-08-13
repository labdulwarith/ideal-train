# Generated by Django 5.0.7 on 2024-08-12 13:51

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_alter_adminnotification_action_type_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='accepted',
            field=models.ManyToManyField(blank=True, related_name='accepted_events', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='event',
            name='rejected',
            field=models.ManyToManyField(blank=True, related_name='rejected_events', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='message',
            name='likes',
            field=models.ManyToManyField(blank=True, related_name='liked_messages', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='poll',
            name='voted_users',
            field=models.ManyToManyField(blank=True, related_name='voted_polls', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='room',
            name='admins',
            field=models.ManyToManyField(blank=True, related_name='admin_rooms', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='room',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='member_rooms', to=settings.AUTH_USER_MODEL),
        ),
    ]
