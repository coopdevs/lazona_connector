# Generated by Django 3.1.12 on 2021-07-26 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20210721_1928'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Última actualització'),
        ),
    ]
