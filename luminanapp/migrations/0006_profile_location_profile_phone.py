# Generated by Django 5.2 on 2025-06-20 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('luminanapp', '0005_like_gallery_alter_like_artwork_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='location',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
