import re

from django.core.exceptions import ValidationError

__p_orcid_regexp = '^https?://orcid.org/[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$'
__p_orcid = re.compile(__p_orcid_regexp, re.IGNORECASE | re.UNICODE)
__p_topic_regexp = '^https?://edamontology.org/topic_[0-9]{4}$'
__p_topic = re.compile(__p_topic_regexp, re.IGNORECASE | re.UNICODE)
__p_grid_regexp = '^grid.[0-9]{4,}.[a-f0-9]{1,2}$'
__p_grid = re.compile(__p_grid_regexp, re.IGNORECASE | re.UNICODE)
__p_ror_regexp = '^0[0-9a-zA-Z]{6}[0-9]{2}$'
__p_ror = re.compile(__p_ror_regexp, re.IGNORECASE | re.UNICODE)
__p_doi_regexp = '^10.\d{4,9}/.+$'
__p_doi = re.compile(__p_doi_regexp, re.IGNORECASE | re.UNICODE)
__looked_up_regexp = "^[\w \\-_~\\']+$"  # could ba allowed ?;:(),
__looked_up = re.compile(__looked_up_regexp, re.IGNORECASE | re.UNICODE)


def validate_can_be_looked_up(value):
    if value is None:
        return value
    if not __looked_up.search(value):
        raise ValidationError(
            'This field can only contain a lookup-able name (%s is not).'
            'Should only contains char such as: %s' % (value, __looked_up_regexp)
        )
    return value


def validate_grid_or_ror_id(value):
    if value is None:
        return value
    if not __p_grid.search(value):
        if not __p_ror.search(value):
            raise ValidationError(
                'This field can only contain a valid GRID or ROR ID (%s is not).'
                'GRID ID Syntax: %s '
                'ROR ID Syntax: %s' % (value, __p_grid_regexp, __p_ror_regexp)
            )
    return value


def validate_edam_topic(value):
    if value is None:
        return value
    if not __p_topic.search(value.__str__()):
        raise ValidationError(
            'This field can only contain valid EDAM Topic URIs (%s is not). Syntax: %s' % (value, __p_topic_regexp)
        )
    return value


def validate_doi(value):
    if value is None:
        return value
    if not __p_doi.search(value.__str__()):
        raise ValidationError(
            'This field can only contain valid DOI URIs (%s is not). Syntax: %s' % (value, __p_doi_regexp)
        )
    return value


def validate_orcid(value):
    if value is None:
        return value
    if not __p_orcid.search(value):
        raise ValidationError(
            'This field can only contain a valid ORCID ID (%s is not). Syntax: %s' % (value, __p_orcid_regexp)
        )
    return value


def validate_email(value):
    if not value.islower():
        raise ValidationError("Only lowercase is allowed in email")
    return value
