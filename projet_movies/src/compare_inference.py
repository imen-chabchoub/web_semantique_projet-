
from rdflib import Graph, Namespace, RDF

EX = Namespace("http://example.org/movie#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

# Chargement des deux graphes
g_original = Graph()
g_original.parse("output/movie_graph.ttl", format="turtle")

g_inferred = Graph()
g_inferred.parse("output/movie_graph_inferred.ttl", format="turtle")

print("=" * 60)
print("COMPARAISON AVEC ET SANS INFÉRENCE")
print("=" * 60)

print(f"\nTriplets sans inférence : {len(g_original)}")
print(f"Triplets avec inférence : {len(g_inferred)}")
print(f"Triplets supplémentaires : {len(g_inferred) - len(g_original)}")


# ---------------------------------------------------------
# REQUÊTE 1 : Rechercher les utilisateurs de type foaf:Agent
# ---------------------------------------------------------

query_agents = """
PREFIX ex: <http://example.org/movie#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT DISTINCT ?user
WHERE {
    ?user a foaf:Agent .
}
"""

agents_original = list(g_original.query(query_agents))
agents_inferred = list(g_inferred.query(query_agents))

print("\n" + "-" * 60)
print("REQUÊTE 1 : UTILISATEURS DE TYPE FOAF:AGENT")
print("-" * 60)

print(f"Sans inférence : {len(agents_original)} résultats")
print(f"Avec inférence : {len(agents_inferred)} résultats")


# ---------------------------------------------------------
# REQUÊTE 2 : Retrouver les évaluations d'un utilisateur
# ---------------------------------------------------------

query_ratings = """
PREFIX ex: <http://example.org/movie#>

SELECT DISTINCT ?user ?rating
WHERE {
    ?user ex:hasGivenRating ?rating .
}
"""

ratings_original = list(g_original.query(query_ratings))
ratings_inferred = list(g_inferred.query(query_ratings))

print("\n" + "-" * 60)
print("REQUÊTE 2 : ÉVALUATIONS ASSOCIÉES AUX UTILISATEURS")
print("-" * 60)

print(f"Sans inférence : {len(ratings_original)} résultats")
print(f"Avec inférence : {len(ratings_inferred)} résultats")


# ---------------------------------------------------------
# EXEMPLES DE TRIPLETS INFÉRÉS
# ---------------------------------------------------------

print("\n" + "-" * 60)
print("EXEMPLES DE TRIPLETS INFÉRÉS")
print("-" * 60)

print("\nQuelques utilisateurs reconnus comme agents FOAF :")

for user in list(g_inferred.subjects(RDF.type, FOAF.Agent))[:5]:
    print(f"{user} rdf:type foaf:Agent")

print("\nQuelques relations inverses :")

for user, rating in list(g_inferred.subject_objects(EX.hasGivenRating))[:5]:
    print(f"{user} ex:hasGivenRating {rating}")

print("\nComparaison terminée.")
