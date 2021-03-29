from collections import OrderedDict

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

            if item.get("id") and item.get("type") and (item["type"] == "Formation"):
                training_uri = URIRef("https://catalogue.france-bioinformatique.fr/api/event/" + str(item['id']))

                # <https://schema.org/CourseInstance>
                G.add((training_uri, RDF.type, SCHEMA.CourseInstance))

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

        yield G.serialize(format="json-ld").decode()
