from django.db import connection


def unaccent_if_available(s):
    for ender in [
        "__iexact",
        "__exact",
        "__icontains",
        "__contains",
        "__in",
    ]:
        if s.endswith(ender):
            return unaccent_if_available(s[:-len(ender)]) + ender
    return "%s__unaccent" % s if connection.vendor == "postgresql" else s
