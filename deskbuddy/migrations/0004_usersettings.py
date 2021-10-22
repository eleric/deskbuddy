# Generated by Django 2.2 on 2021-10-21 14:31

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('deskbuddy', '0003_remove_photo_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSettings',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, null=True)),
                ('photo_frequency', models.IntegerField(null=True)),
            ],
        ),
    ]