
from rdflib import Graph, Namespace, RDF, RDFS

# Charger le fichier Turtle
g = Graph()
g.parse("ontology/movie_schema.ttl", format="turtle")

# Définir notre vocabulaire
EX = Namespace("http://example.org/movie#")

# Compter les classes
classes = set(g.subjects(RDF.type, RDFS.Class))

# Compter les propriétés déclarées
properties = set(g.subjects(RDF.type, RDF.Property))

print("Nombre de triplets :", len(g))
print("Nombre de classes déclarées :", len(classes))
print("Nombre de propriétés déclarées :", len(properties))

print("\nClasses :")
for cls in sorted(classes, key=str):
    print("-", cls.split("#")[-1])

print("\nPropriétés :")
for prop in sorted(properties, key=str):
    print("-", prop.split("#")[-1])

# Vérifier les hiérarchies
print("\nHiérarchie de classes :")
for child, parent in g.subject_objects(RDFS.subClassOf):
    print(child.split("#")[-1], "->", parent.split("#")[-1])

print("\nHiérarchie de propriétés :")
for child, parent in g.subject_objects(RDFS.subPropertyOf):
    print(child.split("#")[-1], "->", parent.split("#")[-1])
