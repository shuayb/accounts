# Generated by Django 3.1.3 on 2020-11-21 21:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vat', '0002_historicalvat'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vattransaction',
            options={'permissions': [('view_transactions_enquiry', 'Can view transactions')]},
        ),
    ]