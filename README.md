
# Discrocs - Discogs Data Scraper and Analyzer

Discrocs est une application web développée en Python avec le framework Flask. Elle permet de récupérer et d'analyser des données sur des vinyles à partir de l'API de Discogs, puis de les classer en les notant à partir des champs scrapés. L'utilisateur peut soumettre une requête pour récupérer des informations sur des articles spécifiques, et l'application effectue une analyse en utilisant des techniques de machine learning pour évaluer et prédire des caractéristiques pertinentes.

## Fonctionnalités

- Scraper des données d'inventaire de Discogs chez un vendeur en utilisant un token d'authentification.
- Filtrer les résultats en fonction des styles de musique spécifiés par l'utilisateur.
- Analyser les données collectées pour calculer un "score final" pour chaque vinyle.
- Permettre le téléchargement des résultats sous forme de fichier Excel.

## Comment ça marche

1. L'utilisateur entre le nom d'utilisateur du vendeur chez lequel il souhaite analyser certaines releases sur Discogs, son token d'API, et les styles de musique qu'il souhaite filtrer.
2. L'application interroge l'API de Discogs et récupère les données correspondantes.
3. Ces données sont ensuite analysées pour calculer un score final basé sur le rating, le nombre de personnes voulant l'article (wantlist), le nombre de personnes possédant l'article (collection), le prix le plus bas et l'année de sortie avec une régression.
4. Les résultats sont sauvegardés dans un fichier Excel, que l'utilisateur peut télécharger directement depuis l'interface web.

## Installation

Pour installer et exécuter ce projet localement, suivez ces étapes :

```bash
git clone https://github.com/radss000/discrocs
cd discrocs
pip install -r requirements.txt
flask run


## Utilisation
Pour démarrer le processus de scraping et d'analyse, accédez à l'adresse suivante dans votre navigateur après avoir lancé l'application : (Pour l'instant, une URL dédiée sera bientôt disponible)

http://localhost:5000/
Entrez les informations requises dans le formulaire et cliquez sur le bouton pour commencer le processus. Vous serez notifié une fois que le fichier Excel sera prêt à être téléchargé.
