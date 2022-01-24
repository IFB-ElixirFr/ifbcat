# Generated by Django 3.2.5 on 2022-01-24 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0170_auto_20220111_2219'),
    ]

    operations = [
        migrations.CreateModel(
            name='Licence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Such as GLPv3, Apache 2.0, ...', max_length=255, unique=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='trainingmaterial',
            name='license',
        ),
        migrations.AddField(
            model_name='trainingmaterial',
            name='license',
            field=models.ManyToManyField(blank=True, help_text='License under which the training material is made available.', to='ifbcat_api.Licence'),
        ),
    ]
