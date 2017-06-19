Dev environment
---

Dump the db schema to a timestamped file: `pg_dump -U postgres -s openlogistix > ol-dump-$(date +'%Y-%m-%d-%H-%M-%S').sql`

Dump the schema to be committed: `pg_dump -U postgres -s openlogistix > schema.psql`.

The database
---

Creating a password for the openlogistix postgresql user on mac. Install `pwgen` through brew if necessary.

```
mkdir conf
pwgen --secure 100 1 > conf/pw
```

Creating the user and db, and loading the schema:

```
# Technically not secure while creating the user, as the pw will appear in ps.
psql postgres -c "CREATE USER openlogistix PASSWORD '$(<conf/pw)';"
createdb openlogistix -O openlogistix
psql openlogistix < schema.psql
```

The app
---

Installing requirements

```
virtualenv env
. env/bin/activate
pip install -r requirements.txt
```

Running the app

```
python src/inventory_app.py
```
