import requests
from rdflib import Graph, Namespace
from rdflib.namespace import OWL
from sys import argv, exit


def get_link_to_data(resource):
    "Returns 'https://dbpedia.org/data/...'"

    return requests.get(resource, headers={"Accept": "text/turtle"}).text


def main():
    if len(argv) != 3:
        print(
            "Argumentos invalidos. Ingrese nombre del dataset-original y del archivo links.ttl"
        )
        exit(1)

    dbo = Namespace("http://dbpedia.org/ontology/")
    dbp = Namespace("http://dbpedia.org/property/")
    foaf = Namespace("http://xmlns.com/foaf/0.1/")

    links = Graph()
    links.parse(argv[2], format="turtle", encoding="utf-8")

    output = Graph()
    output.parse(argv[1], format="turtle", encoding="utf-8")
    output += links

    proprieties = [dbo.birthDate, dbp.occupation, foaf.isPrimaryTopicOf]

    for stmt in links:
        if stmt[1] != OWL["sameAs"]:
            continue

        actor = Graph()
        actor.parse(
            data=get_link_to_data(stmt[2].toPython()),
            format="turtle",
            encoding="utf-8",
        )

        for property in proprieties:
            for _, b, c in actor.triples((None, property, None)):
                if c.toPython() != "":
                    output.add((stmt[0], b, c))

    print(output.serialize(format="turtle").decode("utf-8"))


if __name__ == "__main__":
    main()
