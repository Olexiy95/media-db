# MediaDB

### Overengineered media information keeper

    Using jinja templates, sqlite and FastAPI to serve tables from a locally hosted web app on my home ubuntu server.

    Currently built to pull data from some CSVs I constructed by pulling view history from netflix and adding more info/items to it.

    We then clean it up and create some relations like actors and genres.

    This is a natural evolution of an OCD burdened brain, from creating unnecessary CSV and Excel sheets for lists of things, to holding them in a database and serving via web apps for added potential functionality.

    In the future maybe add support to stream to smart TV and other devices on the network by pointing some protocol to a file location.

    At some point will also add optional support for a PSQL docker container since sqlite doesn't come with much functionality. Since it's hosted on an ubuntu server full of docker containers anyway, could be a neater approach and most importantly much more unnecessary.

### Model (Outdated need to update):

<img src="./media-db_model_old.png" alt="Description" width="350" height="500"/>

Seed resources to CSV directory:

```bash
cp resources/actors_list.csv.example csv/actors_list.csv
cp resources/genres_list.csv.example csv/genres_list.csv
cp resources/movies_list.csv.example csv/movies_list.csv
cp resources/shows_list.csv.example csv/shows_list.csv
```

Running the app:

```bash
python -m app.main
```
