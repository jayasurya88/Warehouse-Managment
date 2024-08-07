# Generated by Django 5.0.6 on 2024-06-14 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0011_order_dispatch_location_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='client_marked_completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_person_marked_completed',
            field=models.BooleanField(default=False),
        ),
    ]
