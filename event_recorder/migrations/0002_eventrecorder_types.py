# Generated by Django 2.0.7 on 2019-12-04 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event_recorder', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventrecorder',
            name='types',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]
