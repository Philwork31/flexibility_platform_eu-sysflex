# Generated by Django 2.0.7 on 2020-04-21 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bidding', '0007_auto_20200414_1520'),
        ('activation', '0003_auto_20200414_1520'),
    ]

    operations = [
        migrations.AddField(
            model_name='flexibilityactivationrequest',
            name='bid_affected',
            field=models.ManyToManyField(to='bidding.FlexibilityBid'),
        ),
    ]
