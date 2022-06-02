from ifbcat_api import models, misc

OrganisationInlineSerializer = misc.inline_serializer_factory(models.Organisation, lookup_field='name')
CommunityInlineSerializer = misc.inline_serializer_factory(models.Community, lookup_field='name')
ElixirPlatformInlineSerializer = misc.inline_serializer_factory(models.ElixirPlatform, lookup_field='name')
EventInlineSerializer = misc.inline_serializer_factory(models.Event)
TeamInlineSerializer = misc.inline_serializer_factory(models.Team, lookup_field='name')
TrainingInlineSerializer = misc.inline_serializer_factory(models.Training)
TrainingMaterialInlineSerializer = misc.inline_serializer_factory(models.TrainingMaterial, lookup_field='name')
EventSponsorInlineSerializer = misc.inline_serializer_factory(models.EventSponsor, lookup_field='name')
