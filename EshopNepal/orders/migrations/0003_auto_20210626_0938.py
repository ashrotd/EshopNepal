# Generated by Django 3.2.2 on 2021-06-26 16:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20210626_0048'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='color',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='size',
        ),
    ]