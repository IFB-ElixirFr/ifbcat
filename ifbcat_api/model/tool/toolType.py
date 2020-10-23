from django.db import models


class ToolType(models.Model):
    TOOLTYPE_CHOICES = (
        ("Bioinformatics portal", "Bioinformatics portal"),
        ("Command-line tool", "Command-line tool"),
        ("Database portal", "Database portal"),
        ("Desktop application", "Desktop application"),
        ("Library", "Library"),
        ("Ontology", "Ontology"),
        ("Plug-in", "Plug-in"),
        ("Script", "Script"),
        ("SPARQL endpoint", "SPARQL endpoint"),
        ("Suite", "Suite"),
        ("Web application", "Web application"),
        ("Web API", "Web API"),
        ("Web service", "Web service"),
        ("Workbench", "Workbench"),
        ("Workflow", "Workflow"),
    )
    # name = models.CharField(max_length=10000, choices=TOOLTYPE_CHOICES)
    name = models.CharField(
        unique=True,
        blank=True,
        null=True,
        max_length=100,
        choices=TOOLTYPE_CHOICES,
    )

    # metadata
    additionDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
