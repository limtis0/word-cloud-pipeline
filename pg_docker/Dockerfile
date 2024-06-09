FROM postgres:latest

# Copy the initial.csv and init.sql to the /docker-entrypoint-initdb.d/ directory
COPY init.csv /docker-entrypoint-initdb.d/
COPY init.sql /docker-entrypoint-initdb.d/
