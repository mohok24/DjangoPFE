# Generated by Django 5.0.6 on 2024-05-23 01:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_alter_report_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='patient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.patient'),
        ),
    ]
