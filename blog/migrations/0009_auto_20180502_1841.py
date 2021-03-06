# Generated by Django 2.0.4 on 2018-05-02 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_auto_20180502_1818'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='author_info',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='author',
            name='birth_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='author',
            name='country',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='author',
            name='nickname',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
