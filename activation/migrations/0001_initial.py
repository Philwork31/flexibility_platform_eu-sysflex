# Generated by Django 2.0.7 on 2020-03-31 01:45

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('flexibility_platform', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FlexibilityActivationRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=3, max_digits=10, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('direction', models.CharField(choices=[('plus', 'Up'), ('moins', 'Down')], max_length=1)),
                ('localization_factor', models.TextField()),
                ('maximum_price', models.DecimalField(decimal_places=3, max_digits=10, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('start_of_delivery', models.DateTimeField()),
                ('status', models.CharField(choices=[('treated', 'TREATED'), ('waiting', 'WAITING')], default='waiting', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='flexibility_platform.Product')),
                ('system_operator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='flexibility_platform.SystemOperator')),
            ],
        ),
    ]
