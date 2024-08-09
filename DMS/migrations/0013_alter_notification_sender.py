# Generated by Django 5.0.7 on 2024-08-08 07:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DMS', '0012_remove_notification_user_alter_notification_sender_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='sender',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
