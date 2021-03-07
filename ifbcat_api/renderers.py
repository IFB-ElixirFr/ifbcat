from collections import OrderedDict

from rest_framework import renderers
from rest_framework.serializers import ListSerializer


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
