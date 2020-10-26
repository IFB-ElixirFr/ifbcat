import os
import csv
import re
from django.core.management import BaseCommand
from ifbcat_api.models import Credit
from ifbcat_api.models import Service
from ifbcat_api.models import ElixirCommunities
from ifbcat_api.models import Publication
from ifbcat.settings import BASE_DIR


class Command(BaseCommand):
    def import_service_from_csv_file(self):
        data_folder = os.path.join(BASE_DIR, '../ifbcat-importdata')
        Service.objects.all().delete()
        Credit.objects.all().delete()
        ElixirCommunities.objects.all().delete()
        Publication.objects.all().delete()
        print(data_folder, 'data_folder')
        for data_file in os.listdir(data_folder):
            # name of the correct csv file
            if data_file == "services.csv":
                with open(os.path.join(data_folder, data_file), encoding='utf-8') as data_file:
                    data = csv.reader(data_file)
                    # skip first line as there is always a header
                    next(data)
                    # do the work
                    for data_object in data:
                        if data_object == []:
                            continue  # Check for empty lines
                        credit_list = []
                        service_name = data_object[0]
                        credit_name = data_object[1]

                        credit_laboratory = data_object[2]
                        credit_institute = data_object[3]
                        credit_adress = data_object[4]
                        credit_email = data_object[5]
                        try:

                            credit1, created = Credit.objects.get_or_create(
                                name=credit_name,
                                laboratory=credit_laboratory,
                                institute=credit_institute,
                                adress=credit_adress,
                                email=credit_email,
                            )

                            credit1.save()
                            credit_list.append(credit1)
                            display_format = "\nCredit, {}, has been saved."
                            print(display_format.format(credit1))
                        except Exception as ex:
                            print(str(ex))
                            msg = "\n\nSomething went wrong saving this credit: {}\n{}".format(credit1, str(ex))
                            print(msg)

                        credit_name2 = data_object[6]
                        credit_laboratory2 = data_object[7]
                        credit_institute2 = data_object[8]
                        credit_adress2 = data_object[9]
                        credit_email2 = data_object[10]
                        if data_object[6] != " ":

                            try:
                                credit2, created = Credit.objects.get_or_create(
                                    name=credit_name2,
                                    laboratory=credit_laboratory2,
                                    institute=credit_institute2,
                                    adress=credit_adress2,
                                    email=credit_email2,
                                )

                                credit2.save()
                                credit_list.append(credit2)
                                display_format = "\nCredit, {}, has been saved."
                                print(display_format.format(credit2))
                            except Exception as ex:
                                print(str(ex))
                                msg = "\n\nSomething went wrong saving this credit: {}\n{}".format(credit2, str(ex))
                                print(msg)

                        service_scope = data_object[11]

                        category = data_object[12]
                        category2 = category.split("\n")
                        service_is_tool = False
                        service_is_data = False
                        service_is_training = False
                        service_is_compute = False
                        service_is_interoperability = False
                        for category3 in category2:
                            if category3 == "Tool":
                                service_is_tool = True
                            elif category3 == "Data":
                                service_is_data = True
                            elif category3 == "Training":
                                service_is_training = True
                            elif category3 == "Compute":
                                service_is_compute = True
                            elif category3 == "Interoperability":
                                service_is_interoperability = True
                        service_description = data_object[13]
                        service_communities = data_object[14]
                        elixir_communities_name_bis = data_object[15]
                        elixir_communities_name = elixir_communities_name_bis.split("\n")
                        elixir_communities_list = []
                        elixir_community = ""
                        for community in elixir_communities_name:
                            if len(community) > 4:

                                try:

                                    elixir_community, created = ElixirCommunities.objects.get_or_create(
                                        name=community,
                                    )
                                    elixir_community.save()
                                    elixir_communities_list.append(elixir_community)
                                    display_format = "\nElixirCommunities, {}, has been saved."
                                    print(display_format.format(elixir_community))
                                except Exception as ex:
                                    print(str(ex))
                                    msg = "\n\nSomething went wrong saving this Elixir_communities: {}\n{}".format(
                                        elixir_community, str(ex)
                                    )
                                    print(msg)

                        service_year_created = data_object[16]
                        service_maturity = data_object[17].upper()
                        service_access = data_object[18]
                        service_quality = data_object[19]
                        service_usage = data_object[20]
                        service_publication_citations_nb = data_object[21]
                        service_publication_coauthor_nb = data_object[22]
                        publications_doi = []
                        doi = data_object[23]
                        doi_split = doi.split("\n")
                        for line in doi_split:
                            match = re.findall(r'(10.[0-9]{4,9}[A-Za-z0-9:;\)\(_/.-]+)', line)
                            if str(match) != '[]':
                                try:

                                    publication, created = Publication.objects.get_or_create(
                                        doi=str(match).strip('[]').strip('\'\''),
                                    )

                                    publication.save()
                                    publications_doi.append(publication)
                                except Exception as ex:
                                    print(str(ex))
                                    msg = "\n\nSomething went wrong saving this publication: {}\n{}".format(
                                        publication, str(ex)
                                    )
                                    print(msg)
                            else:
                                continue

                        service_sab_user_comittee = data_object[25]
                        service_term_of_use = data_object[26]
                        service_ethics_policy = data_object[27]
                        service_funding = data_object[28]
                        motivation = data_object[29]
                        motivation_split = motivation.split("\n")
                        for motivations in motivation_split:
                            if motivations == "be registered in the IFB catalogue of tools":
                                service_motivation_catalog = True
                            if motivations == "be registered as an ELIXIR service (in its SDP)":
                                service_motivation_sdp = True
                        service_motivation_support_ifb_it = False
                        service_motivation_support_ifb_curation = False
                        service_motivation_support_ifb_core_resource = False
                        support = data_object[30]
                        support_split = support.split("\n")
                        for supports in support_split:
                            if supports == "IT support (computation/storage)":
                                service_motivation_support_ifb_it = True
                            elif supports == "curation (tools and network of experts)":
                                service_motivation_support_ifb_curation = True
                            elif supports == "support for the application to become an ELIXIR core resource":
                                service_motivation_support_ifb_core_resource = True

                        service = ""
                        try:

                            service, created = Service.objects.get_or_create(
                                name=service_name,
                                scope=service_scope,
                                is_tool=service_is_tool,
                                is_data=service_is_data,
                                is_training=service_is_training,
                                is_compute=service_is_compute,
                                is_interoperability=service_is_interoperability,
                                description=service_description,
                                communities=service_communities,
                                year_created=service_year_created,
                                maturity=service_maturity,
                                access=service_access,
                                quality=service_quality,
                                usage=service_usage,
                                publication_citations_nb=service_publication_citations_nb.replace(",", ""),
                                publication_coauthor_nb=service_publication_coauthor_nb.replace(",", ""),
                                sab_user_comittee=service_sab_user_comittee,
                                term_of_use=service_term_of_use,
                                ethics_policy=service_ethics_policy,
                                funding=service_funding,
                                motivation_catalog=service_motivation_catalog,
                                motivation_sdp=service_motivation_sdp,
                                motivation_support_ifb_it=service_motivation_support_ifb_it,
                                motivation_support_ifb_curation=service_motivation_support_ifb_curation,
                                motivation_support_ifb_core_resource=service_motivation_support_ifb_core_resource,
                            )

                            if created:
                                service.save()

                                display_format = "\nService, {}, has been saved."
                                print(display_format.format(service))
                                for credit_service in credit_list:
                                    service.credit.add(credit_service)
                                    print(credit_service)
                                for service_elixir_community in elixir_communities_list:
                                    service.elixir_communities.add(service_elixir_community)
                                for service_pub in publications_doi:
                                    service.key_pub.add(service_pub)

                                service.save()

                        except Exception as ex:
                            print(str(ex))
                            msg = "\n\nSomething went wrong saving this service: {}\n{}".format(service, str(ex))
                            print(msg)

    def handle(self, *args, **options):
        """
        Call the function to import data
        """
        self.import_service_from_csv_file()
