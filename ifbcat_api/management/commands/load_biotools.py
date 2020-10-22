import logging

from django.core.management import BaseCommand
from django.core.management import call_command

from ifbcat_api.model.tool.tool import *

from ifbcat_api.model.tool.toolType import ToolType
from ifbcat_api.model.tool.operatingSystem import OperatingSystem

# from database.models import Language
# from database.models import Topic
# from database.models import OperatingSystem
# from ifbcat_api.model.tool_model.publication import *
# from ifbcat_api.model.tool_model.link import *
from ifbcat_api.model.tool.toolCredit import *

# from ifbcat_api.model.tool_model.function import *
# from ifbcat_api.model.tool_model.documentation import *

# from database.models import Download
# from database.models import Relation

# from database.models import Collection
# from database.models import OtherID
# from database.models import Version

# from database.models import ElixirPlatform
# from database.models import ElixirNode
# from database.models import Accessibility
# from database.models import ToolCredit

from ifbcat_api.model.misc import Topic


import urllib3
import json

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def crawl_tools(self, limit):

        # clean tool table
        Tool.objects.all().delete()
        ToolType.objects.all().delete()
        OperatingSystem.objects.all().delete()
        ToolCredit.objects.all().delete()

        http = urllib3.PoolManager()
        try:
            req = http.request('GET', 'https://bio.tools/api/tool/?page=1&format=json')
            countJson = json.loads(req.data.decode('utf-8'))
            count = int(countJson['count'])
            print(str(count) + " available BioTools entries")

            i = 1
            nbTools = 1
            hasNextPage = True
            while hasNextPage:
                req = http.request('GET', 'https://bio.tools/api/tool/?page=' + str(i) + '&format=json')
                try:
                    entry = json.loads(req.data.decode('utf-8'))
                except JSONDecodeError as e:
                    print("Json decode error for " + str(req.data.decode('utf-8')))
                    break

                hasNextPage = entry['next'] != None
                # print("Processing page "+str(i)+ " hasNext="+str(hasNextPage
                for tool in entry['list']:
                    # print(json.dumps(tool, indent=4))

                    # if 'FR' in tool['collectionID']:
                    if 'elixir-fr-sdp-2019' in tool['collectionID']:
                        # if True:

                        # insert in DB tool table here
                        tool_entry, created = Tool.objects.get_or_create(
                            name=tool['name'],
                            description=tool['description'],
                            homepage=tool['homepage'],
                            biotoolsID=tool['biotoolsID'],
                            # publication=tool['publication'],
                            # operating_system = tool['operatingSystem'],
                            # topic = tool['topic'],
                            # link = tool['link'],
                            biotoolsCURIE=tool['biotoolsCURIE'],
                            # software_version = tool['version'],
                            # downloads = tool['download'],
                            tool_license=tool['license'],
                            # language = tool['language'],
                            # otherID = tool['otherID'],
                            maturity=tool['maturity'],
                            # collectionID = tool['collectionID'],
                            # credit = tool['credit'],
                            # elixirPlatform = tool['elixirPlatform'],
                            # elixirNode = tool['elixirNode'],
                            cost=tool['cost'],
                            # accessibility = tool['accessibility'],
                            # function = tool['function'],
                            # relation = tool['relation'],
                        )

                        # insert or get DB tooltype table here
                        self.add_many_to_many_entry_array(tool_entry, tool_entry.tool_type, tool['toolType'], ToolType)

                        # insert accessibility entry
                        self.add_many_to_many_entry_array(
                            tool_entry, tool_entry.operating_system, tool['operatingSystem'], OperatingSystem
                        )

                        # # insert or get doi
                        # self.add_many_to_many_entry_array(tool_entry, tool_entry.tool_type, tool['toolType'], ToolType)

                        # entry for publications
                        for publication in tool['publication']:
                            print(tool['name'])
                            print(publication)
                            if 'Primary' in publication['type']:
                                doi_entry, created = Doi.objects.get_or_create(doi=publication['doi'])
                                doi_entry.save()
                                tool_entry.primary_publication.add(doi_entry.id)

                        # insert or get DB topic entry table here
                        for topic in tool['topic']:
                            topic_entry, created = Topic.objects.get_or_create(topic=topic['uri'])
                            topic_entry.save()
                            tool_entry.scientific_topics.add(topic_entry.id)

                        tool_entry.save()

                        # entry for toolCredit
                        for credit in tool['credit']:
                            toolCredit_entry, created = ToolCredit.objects.get_or_create(
                                name=credit['name'],
                                email=credit['email'],
                                url=credit['url'],
                                orcidid=credit['orcidid'],
                                gridid=credit['gridid'],
                                typeEntity=credit['typeEntity'],
                                note=credit['note'],
                            )
                            toolCredit_entry.save()
                            tool_entry.tool_credit.add(toolCredit_entry.id)

                            # add typerole entry
                            for type_role in credit['typeRole']:
                                typeRole_entry, created = TypeRole.objects.get_or_create(name=type_role)
                                typeRole_entry.save()
                                toolCredit_entry.type_role.add(typeRole_entry.id)

                        nbTools += 1
                        progress = nbTools * 100 / count
                        if nbTools % 500 == 0:
                            print(str(round(progress)) + " % done")
                        if (limit != -1) and (nbTools >= limit + 1):
                            return
                i += 1
        except urllib3.exceptions.HTTPError as e:
            print("Connection error")
            print(e)
            return None

    def crawl_tools_old(self, limit):
        """
        transforms a biotool entry in RDF using common vocabularies.
        :param connection: credentials, possibly proxy, and URL to connect to
        :param limit: an integer value specifying the number of entries to transform, -1 means no limit.
        :return: a string representation of the corresponding JSON-LD document
        """
        Tool.objects.all().delete()
        ToolType.objects.all().delete()
        Language.objects.all().delete()
        Topic.objects.all().delete()
        OperatingSystem.objects.all().delete()
        Documentation.objects.all().delete()
        Publication.objects.all().delete()
        PublicationMetadata.objects.all().delete()
        PublicationAuthor.objects.all().delete()
        Link.objects.all().delete()
        Download.objects.all().delete()
        Relation.objects.all().delete()
        Collection.objects.all().delete()
        OtherID.objects.all().delete()
        Version.objects.all().delete()
        ElixirPlatform.objects.all().delete()
        ElixirNode.objects.all().delete()
        Accessibility.objects.all().delete()
        ToolCredit.objects.all().delete()
        TypeRole.objects.all().delete()
        Function.objects.all().delete()
        Operation.objects.all().delete()
        Input.objects.all().delete()
        Output.objects.all().delete()
        Data.objects.all().delete()
        Format.objects.all().delete()

        http = urllib3.PoolManager()
        try:
            req = http.request('GET', 'https://bio.tools/api/tool/?page=1&format=json')
            countJson = json.loads(req.data.decode('utf-8'))
            count = int(countJson['count'])
            print(str(count) + " available BioTools entries")

            i = 1
            nbTools = 1
            hasNextPage = True
            while hasNextPage:
                req = http.request('GET', 'https://bio.tools/api/tool/?page=' + str(i) + '&format=json')
                try:
                    entry = json.loads(req.data.decode('utf-8'))
                except JSONDecodeError as e:
                    print("Json decode error for " + str(req.data.decode('utf-8')))
                    break

                hasNextPage = entry['next'] != None
                # print("Processing page "+str(i)+ " hasNext="+str(hasNextPage
                for tool in entry['list']:
                    # if 'FR' in tool['collectionID']:
                    # if 'elixir-fr-sdp-2019' in tool['collectionID']:

                    # print(tool['name'])
                    # print(tool['link'])
                    # print(tool['credit'])
                    # print(tool[''])

                    # insert in DB tool table here
                    tool_entry, created = Tool.objects.get_or_create(
                        name=tool['name'],
                        # description = tool['description'],
                        # operating_system = tool['operatingSystem'],
                        # topic = tool['topic'],
                        # link = tool['link'],
                        biotoolsID=tool['biotoolsID'],
                        biotoolsCURIE=tool['biotoolsCURIE'],
                        # software_version = tool['version'],
                        # downloads = tool['download'],
                        tool_license=tool['license'],
                        # language = tool['language'],
                        # otherID = tool['otherID'],
                        maturity=tool['maturity'],
                        homepage=tool['homepage'],
                        # collectionID = tool['collectionID'],
                        # credit = tool['credit'],
                        # elixirPlatform = tool['elixirPlatform'],
                        # elixirNode = tool['elixirNode'],
                        cost=tool['cost'],
                        # accessibility = tool['accessibility'],
                        # function = tool['function'],
                        # relation = tool['relation'],
                    )
                    tool_entry.save()

                    # insert or get DB tooltype table here
                    self.add_many_to_many_entry_array(tool_entry, tool_entry.tool_type, tool['toolType'], ToolType)
                    # for tooltype in tool['toolType']:
                    #     tool_type_entry, created = ToolType.objects.get_or_create(
                    #         name=tooltype
                    #     )
                    #     tool_type_entry.save()
                    #     tool_entry.tool_type.add(tool_type_entry.id)

                    # insert or get DB language_entry table here
                    self.add_many_to_many_entry_array(tool_entry, tool_entry.language, tool['language'], Language)

                    # insert collectionID entry
                    self.add_many_to_many_entry_array(
                        tool_entry, tool_entry.collection, tool['collectionID'], Collection
                    )

                    # insert ElixirPlatform entry
                    self.add_many_to_many_entry_array(
                        tool_entry, tool_entry.elixir_platform, tool['elixirPlatform'], ElixirPlatform
                    )

                    # insert ElixirNode entry
                    self.add_many_to_many_entry_array(
                        tool_entry, tool_entry.elixir_node, tool['elixirNode'], ElixirNode
                    )

                    # insert accessibility entry
                    self.add_many_to_many_entry_array(
                        tool_entry, tool_entry.accessibility, tool['accessibility'], Accessibility
                    )

                    # insert accessibility entry
                    self.add_many_to_many_entry_array(
                        tool_entry, tool_entry.operatingSystem, tool['operatingSystem'], OperatingSystem
                    )

                    # insert or get DB topic entry table here
                    for topic in tool['topic']:
                        topic_entry, created = Topic.objects.get_or_create(term=topic['term'], uri=topic['uri'])
                        topic_entry.save()
                        tool_entry.topic.add(topic_entry.id)

                    # # insert os entry
                    # for os in tool['operatingSystem']:
                    #     OperatingSystem.objects.create(
                    #         name = os,
                    #         tool = tool_entry
                    #     )
                    # entry for publications
                    for publication in tool['publication']:
                        # print(json.dumps(publication['metadata']))
                        if publication['metadata']:
                            # print(publication['metadata'].keys())
                            if "updated" in publication['metadata'].keys():
                                print("test")
                                print(json.dumps(publication['metadata']['updated']))
                        Publication.objects.create(
                            doi=publication['doi'],
                            pmid=publication['pmid'],
                            pmcid=publication['pmcid'],
                            note=publication['note'],
                            version=publication['version'],
                            type=publication['type'],
                            tool=tool_entry,
                        )
                        if publication['metadata']:
                            publicationMetadata_entry, created = PublicationMetadata.objects.get_or_create(
                                date=publication['metadata']['date'],
                                title=publication['metadata']['title'],
                                journal=publication['metadata']['journal'],
                                abstract=publication['metadata']['abstract'],
                                citationCount=publication['metadata']['citationCount'],
                            )

                            if publication['metadata']['authors']:
                                for author in publication['metadata']['authors']:
                                    publicationAuthor_entry, created = PublicationAuthor.objects.get_or_create(
                                        name=author['name'],
                                    )
                                    publicationMetadata_entry.publicationAuthor.add(publicationAuthor_entry.id)
                        # publication_entry.save()
                        # tool_entry.publication.add(publication_entry.id)

                    # entry for toolCredit
                    for credit in tool['credit']:
                        toolCredit_entry, created = ToolCredit.objects.get_or_create(
                            name=credit['name'],
                            email=credit['email'],
                            url=credit['url'],
                            orcidid=credit['orcidid'],
                            gridid=credit['gridid'],
                            typeEntity=credit['typeEntity'],
                            note=credit['note'],
                        )
                        toolCredit_entry.save()
                        tool_entry.toolCredit.add(toolCredit_entry.id)

                        # add typerole entry
                        for type_role in credit['typeRole']:
                            typeRole_entry, created = TypeRole.objects.get_or_create(name=type_role)
                            typeRole_entry.save()
                            toolCredit_entry.typeRole.add(typeRole_entry.id)

                    # entry for link
                    for link in tool['link']:
                        Link.objects.create(url=link['url'], type=link['type'], note=link['note'], tool=tool_entry)

                    # entry for download
                    for download in tool['download']:
                        Download.objects.create(
                            url=download['url'],
                            type=download['type'],
                            version=download['version'],
                            note=download['note'],
                            tool=tool_entry,
                        )

                    # entry for relation
                    for relation in tool['relation']:
                        Relation.objects.create(
                            biotoolsID=relation['biotoolsID'], type=relation['type'], tool=tool_entry
                        )

                    # entry for otherID
                    for otherID in tool['otherID']:
                        OtherID.objects.create(
                            value=otherID['value'], type=otherID['type'], version=otherID['version'], tool=tool_entry
                        )

                    # entry for version
                    for version in tool['version']:
                        Version.objects.create(version=version, tool=tool_entry)

                    # entry for Documentation
                    for documentation in tool['documentation']:
                        Documentation.objects.create(
                            url=documentation['url'],
                            type=documentation['type'],
                            note=documentation['note'],
                            tool=tool_entry,
                        )

                    # entry for function
                    for function in tool['function']:
                        function_entry, created = Function.objects.get_or_create(
                            cmd=function['cmd'], note=function['note'], tool=tool_entry
                        )

                        # entry for operation (ntn)
                        for operation in function['operation']:
                            operation_entry, created = Operation.objects.get_or_create(
                                term=operation['term'],
                                uri=operation['uri'],
                            )
                            operation_entry.save()
                            function_entry.operation.add(operation_entry.id)

                        # entry for input
                        for input in function['input']:

                            # entry for data
                            data_entry, created = Data.objects.get_or_create(
                                term=input['data']['term'],
                                uri=input['data']['uri'],
                            )
                            data_entry.save()

                            input_entry, created = Input.objects.get_or_create(function=function_entry, data=data_entry)

                            # entry for format
                            for format in input['format']:
                                format_entry, created = Format.objects.get_or_create(
                                    term=format['term'],
                                    uri=format['uri'],
                                    # input = input_entry
                                )
                                format_entry.save()
                                input_entry.format.add(format_entry.id)
                            # print(input['data'])

                        # entry for input
                        for output in function['output']:

                            # entry for data
                            data_entry, created = Data.objects.get_or_create(
                                term=output['data']['term'],
                                uri=output['data']['uri'],
                            )
                            data_entry.save()

                            output_entry, created = Output.objects.get_or_create(
                                function=function_entry, data=data_entry
                            )

                            # entry for format
                            for format in output['format']:
                                format_entry, created = Format.objects.get_or_create(
                                    term=format['term'],
                                    uri=format['uri'],
                                    # output = output_entry
                                )
                                format_entry.save()
                                output_entry.format.add(format_entry.id)

                    nbTools += 1
                    progress = nbTools * 100 / count
                    if nbTools % 500 == 0:
                        print(str(round(progress)) + " % done")
                    if (limit != -1) and (nbTools >= limit + 1):
                        return
                i += 1
        except urllib3.exceptions.HTTPError as e:
            print("Connection error")
            print(e)
            return None

    def add_many_to_many_entry_array(self, tool_entry, tool_to_field, tool_field, field_class):
        for field_value in tool_field:
            field_entry, created = field_class.objects.get_or_create(name=field_value)
            field_entry.save()
            tool_to_field.add(field_entry.id)

    def add_arguments(self, parser):
        """
        Arguments for the command line load_biotools
        """
        parser.add_argument(
            '-l', '--limit', help='Number of tools to import (-1 to retrieve all)', type=int, default=-1
        )

    def handle(self, *args, **options):
        """
        Call the function to import data
        """
        self.crawl_tools(options['limit'])
