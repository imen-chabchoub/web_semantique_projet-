
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from rdflib import Graph


# ============================================================
# 1. CONFIGURATION DU PROJET
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
GRAPH_FILE = BASE_DIR / "output" / "movie_graph.ttl"


# ============================================================
# 2. CRÉATION DE L'APPLICATION FASTAPI
# ============================================================

app = FastAPI(
    title="Movie Knowledge Graph API",
    description="API REST pour interroger le graphe RDF MovieLens",
    version="1.0.0"
)


# ============================================================
# 3. CHARGEMENT DU GRAPHE RDF
# ============================================================

g = Graph()

try:
    if not GRAPH_FILE.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {GRAPH_FILE}. "
            "Exécute d'abord python src/build_graph.py"
        )

    g.parse(str(GRAPH_FILE), format="turtle")
    print(f"Graphe RDF chargé : {len(g)} triplets")

except Exception as exc:
    raise RuntimeError(
        f"Impossible de charger le graphe RDF : {exc}"
    ) from exc


# ============================================================
# 4. FONCTION UTILITAIRE : RÉSULTATS SPARQL EN JSON
# ============================================================

def execute_query(query):
    try:
        results = g.query(query)

        return [
            {
                str(variable): str(value)
                for variable, value in zip(results.vars, row)
                if value is not None
            }
            for row in results
        ]

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur SPARQL : {exc}"
        ) from exc


# ============================================================
# PAGE D'ACCUEIL
# GET /
# ============================================================

@app.get("/")
def home():
    return {
        "message": "Bienvenue dans Movie Knowledge Graph API",
        "status": "OK",
        "description": "API REST pour les données de MovieLens",
        "total_triples": len(g),
        "endpoints": {
            "API 1 - Liste des films": "/movies",
            "API 2 - Films d'animation": "/movies/animation",
            "API 3 - Évaluations d'un film": "/movies/1/ratings",
            "API 4 - Films les mieux notés": "/movies/top-rated",
            "API 5 - Tags funny": "/movies/funny-tags",
            "Documentation interactive": "/docs",
            "État du service": "/health"
        }
    }


# ============================================================
# API 1 : LES 10 PREMIERS FILMS
# GET /movies
# ============================================================

@app.get("/movies")
def get_movies():
    query = """
    PREFIX : <http://example.org/movie#>

    SELECT ?movie ?title
    WHERE {
        ?movie a :Movie ;
               :hasTitle ?title .
    }
    ORDER BY ?title
    LIMIT 10
    """

    return execute_query(query)


# ============================================================
# API 2 : LES FILMS D'ANIMATION
# GET /movies/animation
# ============================================================

@app.get("/movies/animation")
def get_animation_movies(
    limit: int = Query(default=50, ge=1, le=200)
):
    query = f"""
    PREFIX : <http://example.org/movie#>

    SELECT DISTINCT ?movie ?title
    WHERE {{
        ?movie a :Movie ;
               :hasTitle ?title ;
               :hasGenre :genre_Animation .
    }}
    ORDER BY ?title
    LIMIT {limit}
    """

    return execute_query(query)


# ============================================================
# API 3 : LES ÉVALUATIONS D'UN FILM
# GET /movies/1/ratings
# ============================================================

@app.get("/movies/{movie_id}/ratings")
def get_movie_ratings(movie_id: int):
    query = f"""
    PREFIX : <http://example.org/movie#>

    SELECT ?user ?score ?timestamp
    WHERE {{
        ?rating a :Rating ;
                :ratedBy ?user ;
                :ratesMovie :movie_{movie_id} ;
                :hasScore ?score ;
                :hasTimestamp ?timestamp .
    }}
    ORDER BY DESC(?timestamp)
    LIMIT 20
    """

    return execute_query(query)


# ============================================================
# API 4 : LES 10 FILMS LES MIEUX NOTÉS
# MINIMUM 50 ÉVALUATIONS
# GET /movies/top-rated
# ============================================================

@app.get("/movies/top-rated")
def get_top_rated_movies():
    query = """
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

    return execute_query(query)


# ============================================================
# API 5 : FILMS AVEC UN TAG CONTENANT "FUNNY"
# GET /movies/funny-tags
# ============================================================

@app.get("/movies/funny-tags")
def get_funny_tagged_movies():
    query = """
    PREFIX : <http://example.org/movie#>

    SELECT DISTINCT ?movie ?title ?tagText
    WHERE {
        ?movie a :Movie ;
               :hasTitle ?title ;
               :hasTag ?tag .

        ?tag :hasTagText ?tagText .

        FILTER(
            CONTAINS(
                LCASE(STR(?tagText)),
                "funny"
            )
        )
    }
    ORDER BY ?title
    LIMIT 50
    """

    return execute_query(query)


# ============================================================
# API COMPLÉMENTAIRE : ÉTAT DU SERVICE
# GET /health
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "graph_loaded": True,
        "total_triples": len(g)
    }
