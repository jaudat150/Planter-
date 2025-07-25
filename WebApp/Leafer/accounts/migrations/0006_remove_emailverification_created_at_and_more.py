# Generated by Django 5.0.6 on 2025-06-28 18:07

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_emailverification'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailverification',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='emailverification',
            name='user',
        ),
        migrations.AddField(
            model_name='emailverification',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2025, 6, 28, 18, 7, 42, 370751, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='emailverification',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
