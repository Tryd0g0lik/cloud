# Generated by Django 4.2.17 on 2025-01-16 12:20

import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    dependencies = [
        ("cloud_file", "0002_alter_filestorage_comment_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="filestorage",
            name="file_path",
            field=models.FileField(
                upload_to="media/uploads/",
                validators=[
                    django.core.validators.RegexValidator(
                        re.compile("^[-a-zA-Z0-9_]+\\Z"),
                        "Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.",
                        "invalid",
                    ),
                    django.core.validators.MaxLengthValidator(
                        limit_value=100,
                        message="Check the characters quantity. Max quantity of characters is 100",
                    ),
                    django.core.validators.MinValueValidator(
                        limit_value=3,
                        message="Check the characters quantity. Max quantity of characters is 100",
                    ),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="filestorage",
            name="size",
            field=models.PositiveIntegerField(
                validators=[django.core.validators.MinValueValidator(limit_value=0)],
                verbose_name="File weight",
            ),
        ),
    ]
