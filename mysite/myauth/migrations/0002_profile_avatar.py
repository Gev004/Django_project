# Generated by Django 5.2 on 2025-05-25 10:17

import myauth.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myauth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to=myauth.models.profile_avatar_dir_path),
        ),
    ]
