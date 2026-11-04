from pathlib import Path
import pandas as pd

from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD


# ============================================================
# 1. DEFINIR LES CHEMINS DU PROJET
# ============================================================

# Dossier racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Chemins des fichiers CSV
DATA_DIR = BASE_DIR / "data"
MOVIES_FILE = DATA_DIR / "movies.csv"
RATINGS_FILE = DATA_DIR / "ratings.csv"
TAGS_FILE = DATA_DIR / "tags.csv"

# Chemin du schema RDF
SCHEMA_FILE = BASE_DIR / "ontology" / "movie_schema.ttl"

# Fichier RDF qui sera genere
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_FILE = OUTPUT_DIR / "movie_graph.ttl"


# ============================================================
# 2. DEFINIR LE GRAPHE RDF ET LES NAMESPACES
# ============================================================

g = Graph()

# Namespace de notre projet
EX = Namespace("http://example.org/movie#")

# Namespace FOAF
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

# Enregistrer les prefixes pour rendre le fichier Turtle lisible
g.bind("", EX)
g.bind("rdf", RDF)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)
g.bind("foaf", FOAF)


# ============================================================
# 3. CHARGER LE SCHEMA RDF
# ============================================================

print("Chargement du schema RDF...")

g.parse(str(SCHEMA_FILE), format="turtle")

print(f"Schema charge : {len(g)} triplets")


# ============================================================
# 4. CHARGER LES FICHIERS CSV
# ============================================================

print("\nLecture des fichiers CSV...")

movies_df = pd.read_csv(MOVIES_FILE)
ratings_df = pd.read_csv(RATINGS_FILE)
tags_df = pd.read_csv(TAGS_FILE)

print(f"Nombre de films : {len(movies_df)}")
print(f"Nombre d'evaluations : {len(ratings_df)}")
print(f"Nombre de tags : {len(tags_df)}")


# ============================================================
# 5. TRANSFORMER LES FILMS EN TRIPLETS RDF
# ============================================================

print("\nTransformation des films...")

for _, row in movies_df.iterrows():

    # Identifiant RDF du film
    movie_id = int(row["movieId"])
    movie_uri = EX[f"movie_{movie_id}"]

    # Chaque film est une instance de la classe Movie
    g.add((movie_uri, RDF.type, EX.Movie))

    # Ajouter le titre du film
    g.add((
        movie_uri,
        EX.hasTitle,
        Literal(str(row["title"]), datatype=XSD.string)
    ))

    # Recuperer les genres du film
    genres = str(row["genres"]).split("|")

    for genre_name in genres:

        # Certains films ont le genre special "(no genres listed)"
        if genre_name == "(no genres listed)":
            continue

        # Creer une URI pour le genre
        genre_uri = EX["genre_" + genre_name.replace(" ", "_")]

        # Declarer la ressource comme une instance de Genre
        g.add((genre_uri, RDF.type, EX.Genre))

        # Relier le film au genre
        g.add((movie_uri, EX.hasGenre, genre_uri))

        # Si le genre est Animation, declarer aussi la propriete specifique.
        # RDFS permettra ensuite de deduire hasGenre a partir de celle-ci.
        if genre_name == "Animation":

            g.add((
                movie_uri,
                EX.hasAnimationGenre,
                genre_uri
            ))

            # Un film d'animation est une sous-classe de Movie.
            # On utilise donc AnimatedMovie pour ce film.
            g.add((
                movie_uri,
                RDF.type,
                EX.AnimatedMovie
            ))


# ============================================================
# 6. TRANSFORMER LES EVALUATIONS EN TRIPLETS RDF
# ============================================================

print("Transformation des evaluations...")

for _, row in ratings_df.iterrows():

    user_id = int(row["userId"])
    movie_id = int(row["movieId"])

    # URI de l'utilisateur
    user_uri = EX[f"user_{user_id}"]

    # URI du film
    movie_uri = EX[f"movie_{movie_id}"]

    # URI unique de l'evaluation
    rating_id = (
        f"rating_user_{user_id}_movie_{movie_id}"
        f"_timestamp_{int(row['timestamp'])}"
    )
    rating_uri = EX[rating_id]

    # Declarer l'utilisateur comme instance de User
    g.add((user_uri, RDF.type, EX.User))

    # Declarer l'evaluation comme instance de Rating
    g.add((rating_uri, RDF.type, EX.Rating))

    # Relier l'evaluation a l'utilisateur
    g.add((
        rating_uri,
        EX.ratedBy,
        user_uri
    ))

    # Relier l'evaluation au film
    g.add((
        rating_uri,
        EX.ratesMovie,
        movie_uri
    ))

    # Ajouter la note
    g.add((
        rating_uri,
        EX.hasScore,
        Literal(float(row["rating"]), datatype=XSD.decimal)
    ))

    # Ajouter le timestamp
    g.add((
        rating_uri,
        EX.hasTimestamp,
        Literal(int(row["timestamp"]), datatype=XSD.integer)
    ))

    # Relier le film a son evaluation
    g.add((
        movie_uri,
        EX.hasRating,
        rating_uri
    ))


# ============================================================
# 7. TRANSFORMER LES TAGS EN TRIPLETS RDF
# ============================================================

print("Transformation des tags...")

for index, row in tags_df.iterrows():

    user_id = int(row["userId"])
    movie_id = int(row["movieId"])

    user_uri = EX[f"user_{user_id}"]
    movie_uri = EX[f"movie_{movie_id}"]

    # Creer une ressource Tag unique pour cette ligne
    tag_uri = EX[f"tag_{index}"]

    # Declarer l'utilisateur
    g.add((user_uri, RDF.type, EX.User))

    # Declarer le tag
    g.add((tag_uri, RDF.type, EX.Tag))

    # Ajouter le texte du tag
    g.add((
    tag_uri,
    EX.hasTagText,
    Literal(str(row["tag"]), datatype=XSD.string)
))

    # Relier le film au tag
    g.add((
        movie_uri,
        EX.hasTag,
        tag_uri
    ))

    # Le timestamp des tags est disponible dans le CSV
    if pd.notna(row["timestamp"]):

        g.add((
            tag_uri,
            EX.hasTimestamp,
            Literal(int(row["timestamp"]), datatype=XSD.integer)
        ))


# ============================================================
# 8. ENREGISTRER LE GRAPHE RDF
# ============================================================

print("\nEnregistrement du graphe RDF...")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

g.serialize(
    destination=str(OUTPUT_FILE),
    format="turtle"
)

print("\nConstruction terminee !")
print(f"Nombre total de triplets RDF : {len(g)}")
print(f"Fichier genere : {OUTPUT_FILE}")