# Generated by Django 2.1.3 on 2018-11-09 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('detection', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='id',
        ),
        migrations.AlterField(
            model_name='room',
            name='name',
            field=models.CharField(max_length=30, primary_key=True, serialize=False),
        ),
    ]
