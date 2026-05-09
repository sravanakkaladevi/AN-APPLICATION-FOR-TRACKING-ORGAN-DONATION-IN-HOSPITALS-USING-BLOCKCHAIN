# Generated for Ganache/Web3 donation receipt tracking.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_donorprofile_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='organrecord',
            name='blockchain_tx_hash',
            field=models.CharField(blank=True, db_index=True, max_length=66, null=True),
        ),
        migrations.AddField(
            model_name='organrecord',
            name='blockchain_block_number',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='organrecord',
            name='blockchain_timestamp',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
