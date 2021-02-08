# Imports
# "re" is regular expression library

from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_str
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ifbcat_api import models


# This is just for testing serialization
class TestApiViewSerializer(serializers.Serializer):
    """Serializes a test input field."""

    testinput = serializers.CharField(max_length=10)


class UserProfileSerializerTiny(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfile
        fields = (
            'firstname',
            'lastname',
            'email',
            'orcidid',
            'homepage',
            'expertise',
            'homepage',
        )
        extra_kwargs = {
            'email': {'write_only': True},
        }
        read_only = True


# Model serializer for user profile
class UserProfileSerializer(serializers.ModelSerializer):
    """Serializes a user profile (UserProfile object)."""

    # Validation isn't specified for fields where basic validation defined in models.py is adequate
    # "allow_null" means None is considered a valid value (it defauls to False)
    # "required=False" means the field is not required to be present during (de)serialization (it defaults to True)
    # firstname, lastname and email are mandatory
    # NB. "allow_blank=False" means am empty string is considered invalid and will raise a validation error
    # (it is False by default, so no need to set it)

    # firstname (no further validation needed)
    # lastname (no further validation needed)
    # email (no further validation needed)
    # orcidid = serializers.CharField(
    #     allow_blank=False,
    #     allow_null=True,
    #     required=False,
    #     validators=[UniqueValidator(queryset = models.UserProfile.objects.all())])
    # homepage = serializers.URLField(allow_blank=False, allow_null=True, required=False)

    # Metaclass is used to configure the serializer to point to a specific object
    # and setup a list of fields in the model to manage with the serializer.
    class Meta:
        model = models.UserProfile
        fields = (
            'id',
            'password',
            'firstname',
            'lastname',
            'email',
            'orcidid',
            'homepage',
            'expertise',
            'homepage',
            'teamLeader',
            'teamsDeputies',
            'teamsScientificLeaders',
            'teamsTechnicalLeaders',
            'teamsMembers',
            'teamsMaintainers',
        )
        read_only = (
            'is_superuser',
            'is_staff',
            'id',
            'permissions',
        )

        # password field is set to be write-only - it should only be used when creating a new user profile
        # Would be security risk e.g. to allow password hash to be retrieved via API!
        # Also set the field style so that *** are given in the data entry field when the password is typed in
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}},
            'email': {'write_only': True},
        }

    # Override the defult "create" function of the object manager, with the "create_user" function (defined in models.py)
    # This will ensure the password gets created as a hash, rather than clear text
    def create(self, validated_data):
        """Create and return a new user."""

        user = models.UserProfile.objects.create_user(
            password=validated_data['password'],
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            email=validated_data['email'],
            orcidid=validated_data['orcidid'],
            homepage=validated_data['homepage'],
            expertise=validated_data['expertise'],
        )

        return user

    # Override the default "update" function to ensure the user password is hashed when updating
    # If this was not done, if a user updated their profile, the password field would be stored in cleartext,
    # and they'd be unable to login
    # NB.  we "pop" (assign the value and remove from the dictionary) the password from the validated data
    # and set is using "set_password" which saves the password as a hash
    # "super().update()" is used to pass the values to the Django REST update() method, to handle updating the remaining fields.
    def update(self, instance, validated_data):
        """Handle updating user account."""

        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)

        return super().update(instance, validated_data)


# Model serializer for event keyword
class KeywordSerializer(serializers.ModelSerializer):
    """Serializes a keyword (Keyword object)."""

    #     validators=[UniqueValidator(queryset = models.EventKeyword.objects.all())])
    class Meta:
        model = models.Keyword
        fields = ('keyword',)

    def validate(self, attrs):
        self.Meta.model(**attrs).clean_fields()
        self.Meta.model(**attrs).clean()
        return attrs


# Model serializer for event prerequisite
class EventPrerequisiteSerializer(serializers.ModelSerializer):
    """Serializes an event prerequisite (EventPrerequisite object)."""

    # prerequisite = serializers.CharField(
    #     allow_blank=False,
    #     required=False,
    #     validators=[UniqueValidator(queryset = models.EventPrerequisite.objects.all())])

    class Meta:
        model = models.EventPrerequisite
        fields = ('id', 'prerequisite')


# See  https://stackoverflow.com/questions/28009829/creating-and-saving-foreign-key-objects-using-a-slugrelatedfield/28011896
class CreatableSlugRelatedField(serializers.SlugRelatedField):
    """Custom SlugRelatedField that creates the new object when one doesn't exist."""

    def to_internal_value(self, data):
        try:
            return self.get_queryset().get(**{self.slug_field: data})
        except ObjectDoesNotExist:
            instance = self.get_queryset().model(**{self.slug_field: data})
            instance.clean_fields()
            instance.clean()
            instance.save()
            return instance
        except (TypeError, ValueError):
            self.fail('invalid')


class VerboseSlugRelatedField(serializers.SlugRelatedField):
    def to_internal_value(self, data):
        try:
            return self.get_queryset().get(**{self.slug_field: data})
        except ObjectDoesNotExist:
            try:
                self.fail('does_not_exist', slug_name=self.slug_field, value=smart_str(data))
            except ValidationError as e:
                detail = str(e)
                try:
                    detail = e.detail.pop()
                except IndexError:
                    pass
                detail += " Choices are :" + ", ".join(self.get_queryset().values_list(self.slug_field, flat=True))
                raise ValidationError(detail=detail)
        except (TypeError, ValueError):
            self.fail('invalid')


class EventDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EventDate
        exclude = ('id',)
        extra_kwargs = dict(
            dateStart=dict(format="%Y-%m-%d"),
            dateEnd=dict(format="%Y-%m-%d"),
            timeStart=dict(format="%H:%M"),
            timeEnd=dict(format="%H:%M"),
        )


# Model serializer for events.
class EventSerializer(serializers.HyperlinkedModelSerializer):
    """Serializes an event (Event object)."""

    # CharField in ModelSerializer corresponds to both CharField and TextField in Django models
    # IntegerField in ModelSerializer corresponds to PositiveSmallIntegerField etc. in Django models
    # For BooleanField, if an input value is omitted in HTML-encoded form, it
    # is treated as setting the value to False. However, the default of "required=True"
    # is not set for them, and "allow_blank" is not supported.
    # See https://www.django-rest-framework.org/api-guide/fields/#booleanfield
    #
    # max_value of maxParticipants set to 32767 corresponding to PositiveSmallIntegerField defined in models.py
    # See https://www.geeksforgeeks.org/positivesmallintegerfield-django-models/
    #
    #
    # "many=True" for keyword etc. instantiates a ListSerializer, see https://www.django-rest-framework.org/api-guide/serializers/#listserializer
    # "allow_empty=False" disallows empty lists as valid input.

    # name, description, homepage, accessibility, contactName and contactEmail are mandatory

    costs = VerboseSlugRelatedField(
        many=True,
        read_only=False,
        slug_field="cost",
        queryset=models.EventCost.objects,
        required=False,
    )

    topics = CreatableSlugRelatedField(
        many=True,
        read_only=False,
        slug_field="uri",
        queryset=models.Topic.objects,
        required=False,
    )
    keywords = CreatableSlugRelatedField(
        many=True,
        read_only=False,
        slug_field="keyword",
        queryset=models.Keyword.objects,
        required=False,
    )
    prerequisites = CreatableSlugRelatedField(
        many=True,
        read_only=False,
        slug_field="prerequisite",
        queryset=models.EventPrerequisite.objects,
        required=False,
    )
    dates = EventDateSerializer(
        many=True,
        read_only=False,
    )

    #    accessibility = serializers.ChoiceField(
    #         choices = ('Public', 'Private'),
    #         allow_blank=True,
    #         required=False)

    # To-add to "fields" below:  'organisedBy'
    class Meta:
        model = models.Event

        fields = (
            'id',
            'user_profile',
            'name',
            'shortName',
            'description',
            'homepage',
            'type',
            'dates',
            'venue',
            'city',
            'country',
            'onlineOnly',
            'costs',
            'topics',
            'keywords',
            'prerequisites',
            'accessibility',
            'accessibilityNote',
            'maxParticipants',
            'contactName',
            'contactEmail',
            'contactId',
            'market',
            'elixirPlatforms',
            'communities',
            'hostedBy',
            'sponsoredBy',
            'organisedByOrganisations',
            'organisedByTeams',
            'organisedByBioinformaticsTeams',
            'logo_url',
        )

        # "{'style': {'rows': 4, 'base_template': 'textarea.html'}}" sets the field style to an HTML textarea
        # See https://www.django-rest-framework.org/topics/html-and-forms/#field-styles
        # 'lookup_field' is used for relational fields (ForeignKey, ManyToManyField and OneToOneField) which are URLs.
        # 'lookup_field' sets the keyword in the URL as serialized in the JSON.
        # See https://www.django-rest-framework.org/api-guide/relations/
        extra_kwargs = {
            # 'id': {'read_only': True},
            'user_profile': {'read_only': True},
            'description': {'style': {'rows': 4, 'base_template': 'textarea.html'}},
            'venue': {'style': {'rows': 4, 'base_template': 'textarea.html'}},
            'elixirPlatforms': {'lookup_field': 'name'},
            'communities': {'lookup_field': 'name'},
            'hostedBy': {'lookup_field': 'name'},
            'sponsoredBy': {'lookup_field': 'name'},
            # 'organisedBy': {'lookup_field': 'name'},
            'organisedByOrganisations': {'lookup_field': 'name'},
            'organisedByTeams': {'lookup_field': 'name'},
            'organisedByBioinformaticsTeams': {'lookup_field': 'name'},
        }

    def update(self, instance, validated_data):
        sub_instances = dict()
        for nested_field in [
            'dates',
        ]:
            try:
                serialized_sub_instances = validated_data.pop(nested_field)
            except KeyError:
                continue
            # get the serializer, then the model, then the model manager
            qs = self.fields[nested_field].child.Meta.model.objects
            sub_instances_for_this_field = sub_instances.setdefault(nested_field, [])
            # iterate over each values (json dict) provided for the field, also remove them from validated_data
            for serialized_sub_instance in serialized_sub_instances:
                # get or create it
                sub_instance, _ = qs.get_or_create(**serialized_sub_instance)
                # append the instance the new new list of sub_instance the instance will be associated with
                sub_instances_for_this_field.append(sub_instance)
        # update this object minus the nested field(s)
        super().update(instance=instance, validated_data=validated_data)
        # for each fields, set the new sub instances list
        for k, v in sub_instances.items():
            getattr(instance, k).set(v)
        if len(sub_instances) > 0:
            instance.save()
        return instance


# Model serializer for training events
class TrainingEventSerializer(EventSerializer):
    """Serializes a training event (TrainingEvent object)."""

    audienceTypes = VerboseSlugRelatedField(
        many=True,
        read_only=False,
        slug_field="audienceType",
        queryset=models.AudienceType.objects,
        required=False,
    )
    audienceRoles = VerboseSlugRelatedField(
        many=True,
        read_only=False,
        slug_field="audienceRole",
        queryset=models.AudienceRole.objects,
        required=False,
    )

    class Meta(EventSerializer.Meta):
        model = models.TrainingEvent

        fields = EventSerializer.Meta.fields + (
            'audienceTypes',
            'audienceRoles',
            'difficultyLevel',
            'trainingMaterials',
            'learningOutcomes',
            'hoursPresentations',
            'hoursHandsOn',
            'hoursTotal',
            'trainers',
            'personalised',
            'computingFacilities',
            # 'databases',
            # 'tools',
        )

        # '**' syntax is Python 3.5 syntax for combining two dictionaries into one
        extra_kwargs = {
            **EventSerializer.Meta.extra_kwargs,
            **{
                'learningOutcomes': {'style': {'rows': 4, 'base_template': 'textarea.html'}},
                'computingFacilities': {'lookup_field': 'name'},
                'trainingMaterials': {'lookup_field': 'name'},
            },
        }


# Model serializer for trainer
class TrainerSerializer(serializers.HyperlinkedModelSerializer):
    """Serializes a trainer (Trainer object)."""

    class Meta:
        model = models.Trainer

        fields = (
            'id',
            'trainerName',
            'trainerEmail',
            'trainerId',
        )


# Model serializer for training event metrics
class TrainingEventMetricsSerializer(serializers.ModelSerializer):
    """Serializes training event metrics (TrainingEventMetrics object)."""

    class Meta:
        model = models.TrainingEventMetrics

        fields = (
            'id',
            'dateStart',
            'dateEnd',
            'numParticipants',
        )


# Model serializer for event sponsor
class EventSponsorSerializer(serializers.HyperlinkedModelSerializer):
    """Serializes an event sponsor (EventSponsor object)."""

    class Meta:
        model = models.EventSponsor

        fields = (
            'id',
            'name',
            'homepage',
            'logo_url',
            'organisationId',
        )

        extra_kwargs = {
            'organisationId': {'lookup_field': 'name'},
        }


# Organisation serializer
class OrganisationSerializer(serializers.ModelSerializer):
    """Serializes an organisation (Organisation object)."""

    fields = VerboseSlugRelatedField(
        many=True,
        read_only=False,
        slug_field="field",
        queryset=models.Field.objects.all(),
        required=False,
    )

    class Meta:
        model = models.Organisation
        fields = ('id', 'user_profile', 'name', 'description', 'homepage', 'orgid', 'fields', 'city', 'logo_url')
        read_only_fields = ['user_profile']


class CertificationSerializer(serializers.HyperlinkedModelSerializer):
    """Serializes an organisation (Organisation object)."""

    class Meta:
        model = models.Certification
        fields = ('id', 'name', 'description', 'homepage', 'teamsCertifications')

    teamsCertifications = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name",
        required=False,
    )

    ## Lead to unexpected keyword argument 'lookup_field'
    # extra_kwargs = {
    #    'teamsCertifications': {'lookup_field': 'name'},
    # }


# ElixirPlatform serializer
class ElixirPlatformSerializer(serializers.HyperlinkedModelSerializer):
    """Serializes an elixirPlatform (ElixirPlatform object)."""

    class Meta:
        model = models.ElixirPlatform
        fields = ('name', 'description', 'homepage', 'coordinator', 'deputies')
        # read_only_fields = ['id']


class CommunitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Community
        fields = (
            'name',
            'description',
            'homepage',
            'organisations',
        )
        # read_only_fields = ['id']
        extra_kwargs = {
            'organisations': {'lookup_field': 'name'},
        }


# Model serializer for projects
class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    """Serializes a project (Project object)."""

    # team  TO-DO
    # uses TO-DO

    topics = CreatableSlugRelatedField(
        many=True,
        read_only=False,
        slug_field="uri",
        queryset=models.Topic.objects.all(),
        required=False,
    )

    class Meta:
        model = models.Project

        fields = (
            'id',
            'user_profile',
            'name',
            'homepage',
            'description',
            'topics',
            'team',
            'hostedBy',
            'fundedBy',
            'communities',
            'elixirPlatforms',
            'uses',
        )

        extra_kwargs = {
            'user_profile': {'read_only': True},
            'description': {'style': {'rows': 4, 'base_template': 'textarea.html'}},
            'elixirPlatforms': {'lookup_field': 'name'},
            'communities': {'lookup_field': 'name'},
            'team': {'lookup_field': 'name'},
            'hostedBy': {'lookup_field': 'name'},
            'fundedBy': {'lookup_field': 'name'},
            'uses': {'lookup_field': 'name'},
        }


# Model serializer for resources
class ResourceSerializer(serializers.HyperlinkedModelSerializer):
    """Serializes a resource (Resource object)."""

    class Meta:
        model = models.Resource

        fields = (
            'id',
            'user_profile',
            'name',
            'description',
            'communities',
            'elixirPlatforms',
        )

        extra_kwargs = {
            'user_profile': {'read_only': True},
            'description': {'style': {'rows': 4, 'base_template': 'textarea.html'}},
            'communities': {'lookup_field': 'name'},
            'elixirPlatforms': {'lookup_field': 'name'},
        }


# Model serializer for computing facilities
class ComputingFacilitySerializer(ResourceSerializer):
    """Serializes a computing facility (ComputingFacility object)."""

    class Meta:
        model = models.ComputingFacility

        fields = ResourceSerializer.Meta.fields + (
            'homepage',
            'providedBy',
            'team',
            'accessibility',
            'requestAccount',
            'termsOfUse',
            'trainingMaterials',
            'serverDescription',
            'storageTb',
            'cpuCores',
            'ramGb',
            'ramPerCoreGb',
            'cpuHoursYearly',
            'usersYearly',
        )

        extra_kwargs = {
            **ResourceSerializer.Meta.extra_kwargs,
            **{
                'serverDescription': {'style': {'rows': 4, 'base_template': 'textarea.html'}},
                'providedBy': {'lookup_field': 'name'},
                'team': {'lookup_field': 'name'},
                'trainingMaterials': {'lookup_field': 'name'},
            },
        }


# Model serializer for training materials
class TrainingMaterialSerializer(ResourceSerializer):
    """Serializes a training material (TrainingMaterial object)."""

    topics = CreatableSlugRelatedField(
        many=True,
        read_only=False,
        slug_field="uri",
        queryset=models.Topic.objects,
        required=False,
    )
    keywords = CreatableSlugRelatedField(
        many=True,
        read_only=False,
        slug_field="keyword",
        queryset=models.Keyword.objects,
        required=False,
    )
    audienceTypes = VerboseSlugRelatedField(
        many=True,
        read_only=False,
        slug_field="audienceType",
        queryset=models.AudienceType.objects,
        required=False,
    )
    audienceRoles = VerboseSlugRelatedField(
        many=True,
        read_only=False,
        slug_field="audienceRole",
        queryset=models.AudienceRole.objects,
        required=False,
    )
    doi = CreatableSlugRelatedField(
        many=True,
        read_only=False,
        slug_field="doi",
        queryset=models.Doi.objects,
        required=False,
    )

    class Meta:
        model = models.TrainingMaterial

        fields = ResourceSerializer.Meta.fields + (
            'doi',
            'fileLocation',
            'fileName',
            'topics',
            'keywords',
            'audienceTypes',
            'audienceRoles',
            'difficultyLevel',
            'providedBy',
            'dateCreation',
            'dateUpdate',
            'license',
        )

        extra_kwargs = {
            **ResourceSerializer.Meta.extra_kwargs,
            **{
                'providedBy': {'lookup_field': 'name'},
            },
        }


# Model serializer for team
class TeamSerializer(serializers.HyperlinkedModelSerializer):
    """Serializes a team (Team object)."""

    publications = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        slug_field="doi",
        queryset=models.Doi.objects,
        required=False,
    )
    keywords = CreatableSlugRelatedField(
        many=True,
        read_only=False,
        slug_field="keyword",
        queryset=models.Keyword.objects,
        required=False,
    )
    fields = VerboseSlugRelatedField(
        many=True,
        read_only=False,
        slug_field="field",
        queryset=models.Field.objects.all(),
        required=False,
    )

    expertise = CreatableSlugRelatedField(
        many=True,
        read_only=False,
        slug_field="uri",
        queryset=models.Topic.objects,
        required=False,
    )
    certifications = CreatableSlugRelatedField(
        many=True,
        read_only=False,
        slug_field="name",
        queryset=models.Certification.objects,
        required=False,
    )

    class Meta:
        model = models.Team
        fields = (
            'id',
            'user_profile',
            'name',
            'logo_url',
            'description',
            'expertise',
            'linkCovid19',
            'homepage',
            'unitId',
            'address',
            'city',
            'country',
            'communities',
            'projects',
            'affiliatedWith',
            'publications',
            'certifications',
            'fundedBy',
            'keywords',
            'fields',
            'orgid',
            # fields below are legacy
            'leader',
            'deputies',
            'scientificLeaders',
            'technicalLeaders',
            'members',
            'maintainers',
        )
        read_only_fields = ['user_profile']

        # '**' syntax is Python 3.5 syntax for combining two dictionaries into one
        extra_kwargs = {
            **{
                'address': {'style': {'rows': 4, 'base_template': 'textarea.html'}},
                'keywords': {'lookup_field': 'keyword'},
                'affiliatedWith': {'lookup_field': 'name'},
                'certifications': {'lookup_field': 'name'},
                'communities': {'lookup_field': 'name'},
                'projects': {'lookup_field': 'name'},
                'fundedBy': {'lookup_field': 'name'},
            },
        }


# Model serializer for bioinformatics team
class BioinformaticsTeamSerializer(TeamSerializer):
    """Serializes a bioinformatics team (BioinformaticsTeam object)."""

    edamTopics = CreatableSlugRelatedField(
        many=True,
        read_only=False,
        slug_field="uri",
        queryset=models.Topic.objects,
        required=False,
    )

    class Meta(TeamSerializer.Meta):
        model = models.BioinformaticsTeam

        fields = TeamSerializer.Meta.fields + (
            'edamTopics',
            'ifbMembership',
            'platforms',
        )

        # '**' syntax is Python 3.5 syntax for combining two dictionaries into one
        extra_kwargs = {
            **TeamSerializer.Meta.extra_kwargs,
            **{
                'platforms': {'lookup_field': 'name'},
            },
        }


# Model serializer for service
class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    """Serializes a service (Service object)."""

    publications = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        slug_field="doi",
        queryset=models.Doi.objects,
        required=False,
    )

    class Meta:
        model = models.Service

        fields = (
            'id',
            'user_profile',
            'name',
            'description',
            'dateEstablished',
            'bioinformaticsTeams',
            'computingFacilities',
            'trainingEvents',
            'trainingMaterials',
            'publications',
            'governanceSab',
        )

        extra_kwargs = {
            'user_profile': {'read_only': True},
            'description': {'style': {'rows': 4, 'base_template': 'textarea.html'}},
            'bioinformaticsTeams': {'lookup_field': 'name'},
            'computingFacilities': {'lookup_field': 'name'},
            # 'trainingEvents': {'lookup_field': 'name'},
            'trainingMaterials': {'lookup_field': 'name'},
        }


# Model serializer for service submission
class ServiceSubmissionSerializer(serializers.HyperlinkedModelSerializer):
    """Serializes a service submission (ServiceSubmission object)."""

    class Meta:
        model = models.ServiceSubmission

        fields = (
            'id',
            'user_profile',
            'service',
            'authors',
            'submitters',
            'year',
            'motivation',
            'scope',
            'caseForSupport',
            'qaqc',
            'usage',
            'sustainability',
        )

        extra_kwargs = {
            'user_profile': {'read_only': True},
            'service': {'lookup_field': 'name'},
            'motivation': {'style': {'rows': 4, 'base_template': 'textarea.html'}},
            'scope': {'style': {'rows': 4, 'base_template': 'textarea.html'}},
            'caseForSupport': {'style': {'rows': 4, 'base_template': 'textarea.html'}},
            'qaqc': {'style': {'rows': 4, 'base_template': 'textarea.html'}},
            'usage': {'style': {'rows': 4, 'base_template': 'textarea.html'}},
            'sustainability': {'style': {'rows': 4, 'base_template': 'textarea.html'}},
        }


# Model serializer for tool credit
class ToolCreditSerializer(serializers.HyperlinkedModelSerializer):
    """Serializes a tool (Tool object)."""

    type_role = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        slug_field="name",
        queryset=models.TypeRole.objects,
        required=False,
    )

    class Meta:
        model = models.ToolCredit
        fields = (
            'type_role',
            'name',
            'email',
            'url',
            'orcidid',
            'gridid',
            'typeEntity',
            'note',
        )


# Model serializer for tools
_tool_fields = (
    'id',
    'name',
    'description',
    'homepage',
    'logo',
    'biotoolsID',
    'biotoolsCURIE',
    'tool_type',
    'collection',
    'scientific_topics',
    'primary_publication',
    'operating_system',
    # 'scientific_operations',
    'tool_credit',
    'tool_license',
    'maturity',
    'cost',
    'unique_visits',
    'access_condition',
    'citations',
    'annual_visits',
    'unique_visits',
    'last_update',
    # 'increase_last_update',
    # 'access_condition',
    'keywords',
    # 'platform',
    # 'language',
    # 'topic',
)


class ToolSerializer(serializers.HyperlinkedModelSerializer):
    """Serializes a tool (Tool object)."""

    tool_type = VerboseSlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name",
        required=False,
    )
    keywords = CreatableSlugRelatedField(
        many=True,
        read_only=True,
        slug_field="keyword",
        required=False,
    )
    collection = VerboseSlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name",
        required=False,
    )

    scientific_topics = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="uri",
        required=False,
    )

    primary_publication = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="doi",
        required=False,
    )

    operating_system = VerboseSlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name",
        required=False,
    )

    tool_credit = ToolCreditSerializer(read_only=True, many=True)

    class Meta:
        model = models.Tool
        fields = _tool_fields
        read_only_fields = tuple(f for f in _tool_fields if f != 'biotoolsID')
        # depth = 1
