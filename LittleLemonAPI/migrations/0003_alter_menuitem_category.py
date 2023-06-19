# Generated by Django 4.2.1 on 2023-06-10 19:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("LittleLemonAPI", "0002_alter_orderitem_order"),
    ]

    operations = [
        migrations.AlterField(
            model_name="menuitem",
            name="category",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="LittleLemonAPI.category",
            ),
        ),
    ]
