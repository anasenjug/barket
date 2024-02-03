# Generated by Django 4.2 on 2024-02-03 09:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0009_alter_topupcode_ref_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topuptransaction',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topup_transactions', to=settings.AUTH_USER_MODEL),
        ),
    ]
