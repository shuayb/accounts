# Generated by Django 3.0.7 on 2020-07-25 17:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('nominals', '0005_auto_20200725_1719'),
        ('purchases', '0010_auto_20200720_1956'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseline',
            name='nominal_transaction',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='nominals.NominalTransaction'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='purchaseheader',
            name='type',
            field=models.CharField(choices=[('pbi', 'Brought Forward Invoice'), ('pbc', 'Brought Forward Credit Note'), ('pbp', 'Brought Forward Payment'), ('pbr', 'Brought Forward Refund'), ('pp', 'Payment'), ('pr', 'Refund'), ('pi', 'Invoice'), ('pc', 'Credit Note')], max_length=3),
        ),
    ]