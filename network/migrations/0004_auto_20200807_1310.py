# Generated by Django 3.0.8 on 2020-08-07 19:10

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0003_auto_20200806_1728'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='likes',
            field=models.ManyToManyField(related_name='liker', to=settings.AUTH_USER_MODEL),
        ),
    ]
