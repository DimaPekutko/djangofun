# Generated by Django 4.0.6 on 2022-07-13 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('page', '0007_alter_page_follow_requests'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='is_blocked',
            field=models.BooleanField(default=False),
        ),
    ]