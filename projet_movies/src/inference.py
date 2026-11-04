from rdflib import Graph, Namespace, RDF, RDFS, OWL

# Espaces de noms
EX = Namespace("http://example.org/movie#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

# Chargement du graphe de données
g = Graph()
g.parse("output/movie_graph.ttl", format="turtle")

# Chargement de l'ontologie modifiée
g.parse("ontology/movie_schema.ttl", format="turtle")

initial_count = len(g)
print(f"Nombre de triplets avant inférence : {initial_count}")

# =========================================================
# RÈGLE 1 : User rdfs:subClassOf foaf:Agent
# =========================================================

new_agent_triples = 0

for user in g.subjects(RDF.type, EX.User):
    triple = (user, RDF.type, FOAF.Agent)

    if triple not in g:
        g.add(triple)
        new_agent_triples += 1

print(f"Règle 1 - Nouveaux agents FOAF : {new_agent_triples}")

# =========================================================
# RÈGLE 2 : Propriétés inverses
# hasGivenRating owl:inverseOf ratedBy
# =========================================================

new_inverse_triples = 0

for rating, user in g.subject_objects(EX.ratedBy):
    triple = (user, EX.hasGivenRating, rating)

    if triple not in g:
        g.add(triple)
        new_inverse_triples += 1

print(f"Règle 2 - Nouvelles relations inverses : {new_inverse_triples}")

# =========================================================
# Sauvegarde du graphe enrichi
# =========================================================

output_file = "output/movie_graph_inferred.ttl"
g.serialize(destination=output_file, format="turtle")

print(f"Nombre de triplets après inférence : {len(g)}")
print(f"Total de nouveaux triplets : {len(g) - initial_count}")
print(f"Graphe enrichi enregistré dans : {output_file}")