# Generated by Django 3.0.7 on 2020-10-16 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ifbcat_api', '0120_tool'),
    ]

    operations = [
        migrations.CreateModel(
            name='ToolType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, choices=[('Bioinformatics portal', 'Bioinformatics portal'), ('Command-line tool', 'Command-line tool'), ('Database portal', 'Database portal'), ('Desktop application', 'Desktop application'), ('Library', 'Library'), ('Ontology', 'Ontology'), ('Plug-in', 'Plug-in'), ('Script', 'Script'), ('SPARQL endpoint', 'SPARQL endpoint'), ('Suite', 'Suite'), ('Web application', 'Web application'), ('Web API', 'Web API'), ('Web service', 'Web service'), ('Workbench', 'Workbench'), ('Workflow', 'Workflow')], max_length=100, null=True)),
                ('additionDate', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='tool',
            name='tool_type',
            field=models.ManyToManyField(blank=True, to='ifbcat_api.ToolType'),
        ),
    ]