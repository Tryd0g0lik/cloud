# Generated by Django 4.2.17 on 2025-01-16 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cloud_file", "0003_alter_filestorage_file_path_alter_filestorage_size"),
    ]

    operations = [
        migrations.AlterField(
            model_name="filestorage",
            name="file_path",
            field=models.FileField(upload_to="media/uploads/"),
        ),
        migrations.AlterField(
            model_name="filestorage",
            name="size",
            field=models.PositiveIntegerField(verbose_name="File weight"),
        ),
    ]
