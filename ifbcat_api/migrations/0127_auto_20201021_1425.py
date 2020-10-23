# Generated by Django 3.0.7 on 2020-10-21 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0126_auto_20201021_1229'),
    ]

    operations = [
        migrations.CreateModel(
            name='TypeRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ToolCredit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.CharField(blank=True, max_length=100, null=True)),
                ('url', models.CharField(blank=True, max_length=500, null=True)),
                ('orcidid', models.CharField(blank=True, max_length=100, null=True)),
                ('gridid', models.CharField(blank=True, max_length=100, null=True)),
                ('typeEntity', models.CharField(blank=True, max_length=100, null=True)),
                ('note', models.CharField(blank=True, max_length=2000, null=True)),
                ('typeRole', models.ManyToManyField(blank=True, to='ifbcat_api.TypeRole')),
            ],
        ),
        migrations.AddField(
            model_name='tool',
            name='tool_credit',
            field=models.ManyToManyField(blank=True, to='ifbcat_api.ToolCredit'),
        ),
    ]
