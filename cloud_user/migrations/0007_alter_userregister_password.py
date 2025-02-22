# Generated by Django 4.2.17 on 2025-02-06 16:23

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cloud_user", "0006_userregister_is_superuser_alter_userregister_email"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userregister",
            name="password",
            field=models.BinaryField(
                help_text="Password of user",
                max_length=128,
                validators=[
                    django.core.validators.MinLengthValidator(3),
                    django.core.validators.MaxLengthValidator(128),
                    django.core.validators.RegexValidator(regex=" "),
                ],
                verbose_name="password",
            ),
        ),
    ]
