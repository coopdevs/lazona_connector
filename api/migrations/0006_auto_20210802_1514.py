# Generated by Django 3.1.12 on 2021-08-02 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20210802_1332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipment',
            name='status',
            field=models.CharField(
                choices=[
                    ('ERROR_FROM_BODY', 'Error alta enviament'),
                    ('LABEL_SENT', 'Etiqueta enviada al venedor'),
                    ('IN_PROCESS', 'En proces'),
                    ('ON_HOLD', "Particularitat al proces d'enviament"),
                    ('ERROR_FROM_TRACKING', 'Error API de seguiment'),
                    ('DELIVERED', 'Entregat')
                ],
                max_length=20,
                verbose_name="Estat de l'enviament"
            ),
        ),
    ]
