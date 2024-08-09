# Generated by Django 5.0.7 on 2024-08-09 08:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DMS', '0019_article_delivery_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='delivery_status',
        ),
        migrations.RemoveField(
            model_name='article',
            name='products',
        ),
        migrations.AddField(
            model_name='article',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='article',
            name='receiver_name',
            field=models.CharField(default=None, max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='article',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DMS.client'),
        ),
        migrations.AlterField(
            model_name='article',
            name='destination_address',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='article',
            name='pickup_address',
            field=models.TextField(),
        ),
    ]
