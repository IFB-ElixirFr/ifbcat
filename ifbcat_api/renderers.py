import logging
from collections import OrderedDict

from django.db.models import CharField, TextField, DateField, URLField, IntegerField
from django.urls import reverse
from rest_framework import renderers
from rest_framework.serializers import ListSerializer

import requests
import json

from rdflib import ConjunctiveGraph, URIRef, Namespace, Literal
from rdflib.namespace import RDF, RDFS, FOAF, XSD


class NTriplesRdfRenderer(renderers.BaseRenderer):
    # media_type = 'text/rdf+txt'
    media_type = 'text/rdf'
    format = 'rdf'
    render_style = 'text'

    def render(self, data, media_type=None, renderer_context=None):
        if type(data) == OrderedDict:  # ie paginated
            serializer = data["results"].serializer
            actual_data = data["results"]
            yield f'<count> <int> "{data["count"]}"\n'
            yield f'<next> <url> "{data["next"]}"\n'
            yield f'<previous> <url> "{data["previous"]}"\n'
        elif 'detail' in data:
            return
        else:  # not paginated
            serializer = data.serializer
            actual_data = data

        if type(serializer) == ListSerializer:  # List view
            serializer = serializer.child  # get the child serializer, not the list one
        else:
            actual_data = [actual_data]  # put the only instance dict in an array to have the same behavior after

        rdf_mapping = getattr(serializer.Meta, 'rdf_mapping', dict())

        model_name = serializer.Meta.model._meta.verbose_name.title()
        base_uri = f'http://ifb/{model_name.lower()}'
        for r in actual_data:
            uri = f"{base_uri}/{r['id']}"
            yield f'<{uri}> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> "{model_name}"\n'
            for k, rdf_type in rdf_mapping.items():
                yield f'<{uri}> <{rdf_type}> "{r[k]}"\n'


# Proof of concept on tools before using it on training
class JsonLDSchemaEventRenderer(renderers.BaseRenderer):
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
            serializer = data.serializer
            actual_data = data

        if type(serializer) == ListSerializer:  # List view
            serializer = serializer.child  # get the child serializer, not the list one
        else:
            actual_data = [actual_data]  # put the only instance dict in an array to have the same behavior after

        # RDFlib graph object
        G = ConjunctiveGraph()
        SCHEMA = Namespace("https://schema.org/")

        count = 0

        # we iterate over each result in the results set
        for item in actual_data:
            if item.get("id"):
                # print(item["type"])
                event_uri = URIRef("https://catalogue.france-bioinformatique.fr/api/event/" + str(item['id']))

                # <https://schema.org/CourseInstance>
                G.add((event_uri, RDF.type, SCHEMA.CourseInstance))

                # print("((((((--------))))))")
                if item.get("name"):
                    # print(item["name"])
                    G.add((event_uri, SCHEMA.name, Literal(item["name"], datatype=XSD.string)))

                if item.get("city"):
                    G.add((event_uri, SCHEMA.location, Literal(item["city"], datatype=XSD.string)))

                if item.get("homepage"):
                    # print(item["homepage"])
                    # print(json.dumps(item, indent=True))
                    G.add((event_uri, SCHEMA.url, URIRef(item["homepage"])))

                if item.get("description"):
                    # print(item["description"])
                    G.add((event_uri, SCHEMA.description, Literal(item["description"], datatype=XSD.string)))

                # TODO check that dates are valid ISO-8601
                if item.get("dates"):
                    for date in item["dates"]:
                        if date.get("dateStart"):
                            G.add((event_uri, SCHEMA.startDate, Literal(date["dateStart"], datatype=XSD.date)))
                        #                            print(f"START {date['dateStart']}")
                        if date.get("dateEnd"):
                            G.add((event_uri, SCHEMA.endDate, Literal(date["dateEnd"], datatype=XSD.date)))
            #                            print(f"END {date['dateStart']}")
            count += 1
        yield G.serialize(format="json-ld")


# Proof of concept on tools before using it on training
class JsonLDSchemaTrainingRenderer(renderers.BaseRenderer):
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
            serializer = data.serializer
            actual_data = data

        if type(serializer) == ListSerializer:  # List view
            serializer = serializer.child  # get the child serializer, not the list one
        else:
            actual_data = [actual_data]  # put the only instance dict in an array to have the same behavior after

        # RDFlib graph object
        G = ConjunctiveGraph()
        SCHEMA = Namespace("https://schema.org/")

        count = 0

        # we iterate over each result in the results set
        for item in actual_data:
            if item.get("id"):
                # print(item["type"])
                training_uri = URIRef("https://catalogue.france-bioinformatique.fr/api/training/" + str(item['id']))

                # <https://schema.org/Course>
                G.add((training_uri, RDF.type, SCHEMA.Course))

                # print("((((((--------))))))")
                if item.get("name"):
                    # print(item["name"])
                    G.add((training_uri, SCHEMA.name, Literal(item["name"], datatype=XSD.string)))

                if item.get("city"):
                    G.add((training_uri, SCHEMA.location, Literal(item["city"], datatype=XSD.string)))

                if item.get("homepage"):
                    # print(item["homepage"])
                    # print(json.dumps(item, indent=True))
                    G.add((training_uri, SCHEMA.url, URIRef(item["homepage"])))

                if item.get("description"):
                    # print(item["description"])
                    G.add((training_uri, SCHEMA.description, Literal(item["description"], datatype=XSD.string)))

                # TODO check that dates are valid ISO-8601
                if item.get("dates"):
                    for date in item["dates"]:
                        if date.get("dateStart"):
                            G.add((training_uri, SCHEMA.startDate, Literal(date["dateStart"], datatype=XSD.date)))
                        #                            print(f"START {date['dateStart']}")
                        if date.get("dateEnd"):
                            G.add((training_uri, SCHEMA.endDate, Literal(date["dateEnd"], datatype=XSD.date)))
            #                            print(f"END {date['dateStart']}")
            count += 1
        yield G.serialize(format="json-ld")


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

                # We do not render not provided value(s)
                if value is None or isinstance(value, list) and len(value) == 0:
                    continue

                # get the type for the attribute
                datatype = None
                # first, try to get the explicitly set type
                if type(mapping) == dict:
                    # try:
                    #     datatype = getattr(XSD, mapping["xsd_type"])
                    # except KeyError:
                    #     pass
                    try:
                        datatype = getattr(SCHEMA, mapping["schema_type"])
                    except KeyError:
                        pass
                # second, try to guess the type
                if datatype is None:
                    attr_type = type(model._meta.get_field(attr_name))
                    if isinstance(attr_type(), CharField) or isinstance(attr_type(), TextField):
                        datatype = SCHEMA.Text
                    elif isinstance(attr_type(), DateField):
                        datatype = SCHEMA.Date
                    elif isinstance(attr_type(), IntegerField):
                        datatype = SCHEMA.Integer
                    elif isinstance(attr_type(), URLField):
                        datatype = SCHEMA.URL
                # finally, we scream as we were not able to find its type
                if datatype is None:
                    # type(mapping) == dict and 'xsd_type' in mapping\
                    assert False, (
                        "type not guessed nor provided, you must provide it as "
                        f"{attr_name}=dict(schema_attr='{mapping}', xsd_type='Todo') or "
                        f"{attr_name}=dict(schema_attr='{mapping}', schema_type='Todo') or "
                    )

                # In schema_mapping, for an attr_name dev can provide the schema_attr and optionally its type.
                # To simplify the writing of schema_mapping, we allow dev to provide a string which is
                # considered as a schema_attr, and the type is guessed.
                if isinstance(mapping, str):
                    schema_attr = mapping
                else:
                    schema_attr = mapping["schema_attr"]

                # we can both have single value, or multiple, so we are resilient
                if isinstance(value, list):
                    values = value
                else:
                    values = [value]
                # add all values to the graph
                for v in values:
                    G.add(
                        (
                            object_uri,
                            getattr(SCHEMA, schema_attr),
                            Literal(v, datatype=datatype),
                        )
                    )
        # render the graph in json-ld
        yield G.serialize(format="json-ld")
