# Generated by Django 3.1.1 on 2020-09-22 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0002_saleline_item'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='email',
            field=models.EmailField(default='duh', max_length=254),
            preserve_default=False,
        ),
    ]