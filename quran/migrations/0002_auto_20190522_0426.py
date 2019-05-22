# Generated by Django 2.2.1 on 2019-05-22 04:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quran', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='surah',
            name='name',
        ),
        migrations.AddField(
            model_name='surah',
            name='name_ar',
            field=models.CharField(max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='surah',
            name='name_en',
            field=models.CharField(max_length=32, null=True),
        ),
    ]
