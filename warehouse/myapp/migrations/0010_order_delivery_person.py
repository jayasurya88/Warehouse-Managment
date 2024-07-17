# Generated by Django 5.0.6 on 2024-06-13 09:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]