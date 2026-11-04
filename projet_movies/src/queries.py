
from pathlib import Path
from rdflib import Graph, Namespace

# ============================================================
# 1. CHARGEMENT DU GRAPHE RDF
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

g = Graph()

print("Chargement du graphe RDF...")

g.parse(
    BASE_DIR / "output" / "movie_graph.ttl",
    format="turtle"
)

print(f"Graphe chargé : {len(g)} triplets RDF\n")

EX = Namespace("http://example.org/movie#")


# ============================================================
# REQUÊTE 1
# Question métier :
# Quels sont les 10 premiers films présents dans le graphe RDF ?
# ============================================================

query1 = """
PREFIX : <http://example.org/movie#>

SELECT ?movie ?title
WHERE {
    ?movie a :Movie ;
           :hasTitle ?title .
}
ORDER BY ?title
LIMIT 10
"""


# ============================================================
# REQUÊTE 2
# Question métier :
# Quels sont les films appartenant au genre Animation ?
# ============================================================

query2 = """
PREFIX : <http://example.org/movie#>

SELECT DISTINCT ?movie ?title
WHERE {
    ?movie a :Movie ;
           :hasTitle ?title ;
           :hasGenre :genre_Animation .
}
ORDER BY ?title
LIMIT 50
"""


# ============================================================
# REQUÊTE 3
# Question métier :
# Quelles sont les évaluations données par les utilisateurs
# au film dont l'identifiant MovieLens est 1 ?
# ============================================================

query3 = """
PREFIX : <http://example.org/movie#>

SELECT ?user ?score ?timestamp
WHERE {
    ?rating a :Rating ;
            :ratedBy ?user ;
            :ratesMovie :movie_1 ;
            :hasScore ?score ;
            :hasTimestamp ?timestamp .
}
ORDER BY DESC(?timestamp)
LIMIT 20
"""


# ============================================================
# REQUÊTE 4
# Question métier :
# Quels sont les 10 films les mieux notés, parmi ceux qui ont
# reçu au moins 50 évaluations ?
# ============================================================

query4 = """
PREFIX : <http://example.org/movie#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?movie ?title
       (AVG(xsd:decimal(?score)) AS ?averageRating)
       (COUNT(?rating) AS ?numberOfRatings)
WHERE {
    ?movie a :Movie ;
           :hasTitle ?title ;
           :hasRating ?rating .

    ?rating :hasScore ?score .
}
GROUP BY ?movie ?title
HAVING (COUNT(?rating) >= 50)
ORDER BY DESC(?averageRating)
LIMIT 10
"""


# ============================================================
# REQUÊTE 5
# Question métier :
# Quels films possèdent un tag contenant le mot "funny",
# sans tenir compte des majuscules et des minuscules ?
# ============================================================

query5 = """
PREFIX : <http://example.org/movie#>

SELECT DISTINCT ?movie ?title ?tagText
WHERE {
    ?movie a :Movie ;
           :hasTitle ?title ;
           :hasTag ?tag .

    ?tag :hasTagText ?tagText .

    FILTER(CONTAINS(LCASE(STR(?tagText)), "funny"))
}
ORDER BY ?title
LIMIT 50
"""


# ============================================================
# EXÉCUTION DES 5 REQUÊTES
# ============================================================

queries = [
    ("Requête 1 : Les 10 premiers films", query1),
    ("Requête 2 : Les films d'animation", query2),
    ("Requête 3 : Les évaluations du film MovieLens 1", query3),
    ("Requête 4 : Les 10 films les mieux notés (minimum 50 évaluations)", query4),
    ("Requête 5 : Les films associés à un tag contenant 'funny'", query5)
]


for title, query in queries:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

    results = g.query(query)

    if len(results) == 0:
        print("Aucun résultat trouvé.")
    else:
        for row in results:
            print(" | ".join(
                f"{variable} = {value}"
                for variable, value in zip(results.vars, row)
            ))

