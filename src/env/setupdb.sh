export PGPASSWORD='postgres';
psql --dbname=postgres --host=0.0.0.0 --port=5432 --username=postgres -a -q -f ./backup.sql;