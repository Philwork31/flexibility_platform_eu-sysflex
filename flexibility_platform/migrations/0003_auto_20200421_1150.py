# Generated by Django 2.0.7 on 2020-04-21 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flexibility_platform', '0002_auto_20200415_1129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliveryperiod',
            name='starting_date',
            field=models.DateTimeField(),
        ),
    ]
