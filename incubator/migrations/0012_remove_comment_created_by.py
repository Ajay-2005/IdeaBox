# Generated by Django 5.1.3 on 2024-12-20 07:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('incubator', '0011_tag_remove_thread_category_remove_thread_author_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='created_by',
        ),
    ]