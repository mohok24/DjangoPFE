# Generated by Django 5.0.6 on 2024-05-08 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_report_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentFolderPath',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('folder_path', models.CharField(default='D:\\reports\\meow', max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='report',
            name='acr',
            field=models.CharField(default='N/A', max_length=255),
        ),
        migrations.AddField(
            model_name='report',
            name='noneE',
            field=models.CharField(default='N/A', max_length=255),
        ),
        migrations.AddField(
            model_name='report',
            name='noneM',
            field=models.CharField(default='N/A', max_length=255),
        ),
    ]
