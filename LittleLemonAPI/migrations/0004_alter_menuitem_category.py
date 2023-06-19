# Generated by Django 4.2.1 on 2023-06-11 00:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("LittleLemonAPI", "0003_alter_menuitem_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="menuitem",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="LittleLemonAPI.category",
            ),
        ),
    ]