from django.db import models

# from database.model.resource import *
# from database.model.keyword import *

from ifbcat_api.model.tool.toolType import ToolType

# from database.model.tool.language import *
# from ifbcat_api.model.tool.topic import *
# from database.model.tool_model.publication import *
# from database.model.tool.elixirPlatform import *
# from database.model.tool.elixirNode import *
from ifbcat_api.model.tool.operatingSystem import OperatingSystem
from ifbcat_api.model.tool.toolCredit import ToolCredit, TypeRole
from ifbcat_api.model.tool.collection import Collection
from ifbcat_api.models import Keyword


# from ifbcat_api.model.tool.function import *

# from database.model.platform_model.platform import *

from ifbcat_api.model.misc import Topic, Doi


class Tool(models.Model):

    name = models.CharField(
        unique=True,
        blank=False,
        null=False,
        max_length=100,
    )
    description = models.TextField(blank=True)
    homepage = models.URLField(max_length=512, help_text="Homepage of the tool.")  # , blank=True, null=True)
    biotoolsID = models.CharField(blank=False, null=False, max_length=100)
    tool_type = models.ManyToManyField(ToolType, blank=True)
    # Use edam topics from Topic table
    scientific_topics = models.ManyToManyField(
        Topic,
        blank=True,
    )
    keywords = models.ManyToManyField(
        Keyword,
        blank=True,
        related_name='toolsKeywords',
        help_text="A keyword (beyond EDAM ontology scope) describing the tool.",
    )
    operating_system = models.ManyToManyField(
        OperatingSystem,
        blank=True,
    )
    tool_credit = models.ManyToManyField(ToolCredit, blank=True)
    tool_license = models.CharField(max_length=1000, blank=True, null=True)
    # add operation/function here
    # Primary publication DOI storedin DOI table
    primary_publication = models.ManyToManyField(
        Doi,
        related_name='tools',
        blank=True,
        help_text="Publication(s) that describe the tool as a whole.",
    )
    collection = models.ManyToManyField(Collection, blank=True)

    biotoolsCURIE = models.CharField(blank=False, null=False, max_length=109)  # because of biotools: prefix

    # software_version = models.CharField(max_length=200, blank=True, null=True)

    citations = models.CharField(max_length=1000, blank=True, null=True)
    logo = models.URLField(max_length=200, blank=True, null=True)
    access_condition = models.TextField(blank=True, null=True)
    contact_support = models.CharField(max_length=1000, blank=True, null=True)

    # link = models.CharField(max_length=1000, blank=True, null=True)
    # keywords = models.ManyToManyField(Keyword, blank=True)
    prerequisites = models.TextField(blank=True, null=True)
    # operating_system = models.CharField(max_length=50, blank=True, null=True, choices=OPERATING_SYSTEM_CHOICES)
    # topic = models.CharField(max_length=1000, blank=True, null=True)
    # downloads = models.CharField(max_length=1000, blank=True, null=True)

    annual_visits = models.IntegerField(blank=True, null=True)
    unique_visits = models.IntegerField(blank=True, null=True)

    # many_to_many
    # platform = models.ManyToManyField(Platform, blank=True)

    # language = models.ManyToManyField(Language, blank=True)

    # elixir_platform = models.ManyToManyField(ElixirPlatform, blank=True)
    # elixir_node = models.ManyToManyField(ElixirNode, blank=True)
    # accessibility = models.ManyToManyField(Accessibility, blank=True)

    # link = models.ManyToManyField(Link, blank=True)

    # added fields
    # language = models.CharField(max_length=1000, null=True, blank=True)
    # otherID = models.CharField(max_length=1000, null=True, blank=True)
    maturity = models.CharField(max_length=1000, null=True, blank=True)

    # collectionID = models.CharField(max_length=1000, null=True, blank=True)
    # credit = models.TextField(null=True, blank=True)
    # elixirNode = models.CharField(max_length=1000, null=True, blank=True)
    # elixirPlatform = models.CharField(max_length=1000, null=True, blank=True)
    cost = models.CharField(max_length=1000, null=True, blank=True)
    # accessibility = models.CharField(max_length=1000, null=True, blank=True)
    # function = models.TextField(null=True, blank=True)
    # relation = models.CharField(max_length=1000, null=True, blank=True)

    # to remove ?
    input_data = models.CharField(max_length=1000, blank=True, null=True)
    output_data = models.CharField(max_length=1000, blank=True, null=True)
    primary = models.CharField(max_length=1000, blank=True, null=True)

    # metadata
    addition_date = models.DateTimeField(blank=True, null=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
