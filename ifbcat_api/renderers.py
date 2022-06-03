import logging
from collections import OrderedDict

from django.db.models import CharField, TextField, DateField, URLField, IntegerField, ManyToManyField, ManyToManyRel
from django.urls import reverse
from rdflib import ConjunctiveGraph, URIRef, Namespace, Literal
from rdflib.namespace import RDF, XSD
from rest_framework import renderers
from rest_framework.relations import Hyperlink
from rest_framework.serializers import ListSerializer


# Proof of concept on tools before using it on training
class JsonLDSchemaRenderer(renderers.BaseRenderer):
    # media_type = 'text/rdf+txt'
    media_type = 'application/ld+json'
    format = 'json-ld'
    render_style = 'text'

    def render(self, data, media_type=None, renderer_context=None):
        if type(data) == OrderedDict:  # ie paginated
            serializer = data["results"].serializer
            actual_data = data["results"]
        elif 'detail' in data:
            return
        else:  # not paginated
            try:
                serializer = data.serializer
            except AttributeError:
                # no serializer, we won't be able to do anything
                return
            actual_data = data

        if type(serializer) == ListSerializer:  # List view
            serializer = serializer.child  # get the child serializer, not the list one
        else:
            actual_data = [actual_data]  # put the only instance dict in an array to have the same behavior after

        # RDFlib graph object
        G = ConjunctiveGraph()
        SCHEMA = Namespace("https://schema.org/")

        schema_mapping = getattr(serializer.Meta, 'schema_mapping', dict())

        # get the type of the object, if not provided the items are not rendered
        model = serializer.Meta.model
        try:
            klass_types = [schema_mapping['_type']]
        except KeyError:
            try:
                klass_types = schema_mapping['_types']
            except KeyError:
                logging.warning(
                    f"To serialize {model} to json-ld, "
                    "you must provide a type in _type or many types in _types, always as String"
                )
                yield []
                return
        try:
            slug_name = schema_mapping['_slug_name']
        except KeyError:
            slug_name = 'id'

        # we iterate over each result in the results set
        for item in actual_data:
            if not item.get("id"):
                continue
            object_uri = URIRef(
                "https://catalogue.france-bioinformatique.fr"
                + reverse(f'{model.__name__.lower()}-detail', args=[item[slug_name]])
                + "?format="
                + self.format
            )
            # print(reverse(f'{serializer.Meta.model.__name__.lower()}-detail', args=[getattr(obj, self.slug_name)]))
            # provide the type of the item
            for klass_type in klass_types:
                G.add((object_uri, RDF.type, getattr(SCHEMA, klass_type)))

            for attr_name, mapping in schema_mapping.items():
                # attr_name starting with a _ are not instance attribute, and out of the scope of this loop
                if attr_name[0] == '_':
                    continue
                try:
                    # get the value from the serialized object
                    value = item[attr_name]
                except KeyError:
                    # attribute not found, assuming it's a methods decorated with @property
                    value = getattr(model.objects.get(id=item['id']), attr_name)
                    if type(value) != str:
                        try:
                            value = value()
                        except TypeError:
                            pass

                # We do not render not provided value(s)
                if value is None or isinstance(value, list) and len(value) == 0:
                    continue
                # we can both have single value, or multiple, so we are resilient
                if isinstance(value, list):
                    values = value
                else:
                    values = [value]

                # get the type for the attribute
                datatype = None
                is_related_object = False
                # first, try to get the explicitly set type
                if type(mapping) == dict:
                    try:
                        datatype = getattr(SCHEMA, mapping["_type"])
                    except KeyError:
                        pass
                # second, try to guess the type
                if datatype is None:
                    attr_type = type(model._meta.get_field(attr_name))
                    if attr_type == ManyToManyField or attr_type == ManyToManyRel:
                        is_related_object = True
                    elif isinstance(attr_type(), URLField):
                        datatype = SCHEMA.URL
                    elif isinstance(attr_type(), CharField) or isinstance(attr_type(), TextField):
                        datatype = SCHEMA.Text
                    elif isinstance(attr_type(), DateField):
                        datatype = SCHEMA.Date
                    elif isinstance(attr_type(), IntegerField):
                        datatype = SCHEMA.Integer
                # finally, we scream as we were not able to find its type
                if datatype is None and not is_related_object:
                    # type(mapping) == dict and 'xsd_type' in mapping\
                    assert False, (
                        "type not guessed nor provided, you must provide it as "
                        f"{attr_name}=dict(schema_attr='{mapping}', _type='Todo')"
                    )

                # In schema_mapping, for an attr_name dev can provide the schema_attr and optionally its type.
                # To simplify the writing of schema_mapping, we allow dev to provide a string which is
                # considered as a schema_attr, and the type is guessed.
                if isinstance(mapping, str):
                    schema_attr = mapping
                else:
                    schema_attr = mapping["schema_attr"]

                # add all values to the graph
                for v in values:
                    rdf_subject = object_uri
                    rdf_predicate = getattr(SCHEMA, schema_attr)
                    if is_related_object:
                        if type(v) == Hyperlink or type(v) == str:
                            rdf_object = URIRef(v)
                        else:
                            try:
                                # try to handle value serialized with misc.inline_serializer_factory
                                rdf_object = URIRef(v['url'])
                            except Exception:
                                rdf_object = None
                    else:
                        rdf_object = Literal(v, datatype=datatype)
                    G.add((rdf_subject, rdf_predicate, rdf_object))

        # render the graph in json-ld
        yield G.serialize(format="json-ld")
