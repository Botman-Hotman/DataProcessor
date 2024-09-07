# Overview
On start up the basic database items are made, this would also be an opportunity to make any dimensions or base data the db needs to operate correctly for foreign/primary key relationships. 
Could be more efficient to replace strings with integer look up tables to give the data warehouse a star-schema if the data is large, 
it would require additional processes to be built to parse and create/update lookup tables. 
**Please note if dev is enabled in the .env it will drop and remake all tables on every re-run.**

The system is designed to watch a folder within a docker container and, on a new file being detected run async jobs to load into the database.
After running, the file is deleted regardless of success, could be changed and another watcher checks the age of files and if older than a target time period, error emails or alerts are raised. 

The code is left open for different pipelines to be made by editing the services for any target flat file created within the imports directory.
We make the assumption that an outside service is depositing the flat files on an external cron job / Http request.

## Core Systems
* **db** - contains all session, engines and mappers to interact with a database
* **config** - pydantic interface to .env file for environment vars

## Services
* **schema_init** - scripts to initialise the database, good place for dimension base data to be generated
* **directory_watcher** - async event loop that monitors a directory and can trigger jobs if the right flat files is detected/supported
* **import_data** - scripts to run flat files

## Models
* contains all sql alchemy ORM models that generate the foriegn/primary key relationships

## Sql

# Setup
The project requires pipenv as means to manage dependencies. A folder for logs and imports is needed as well. 

$ `
pip install pipenv &&
git pull && 
cd TrigifyTest &&
mkdir logs imports && 
touch .env
`

# Environment Vars
*  dev = True
*  debug_logs = False
*  db_string = 'postgresql//dev-user:password@localhost:5432/dev_db'
*  db_string_async = "postgresql+asyncpg://dev-user:password@localhost:5432/dev_db"
*  echo_sql = False
*  init_db = True
*  staging_schema = 'staging'
*  dw_schema = 'datawarehouse'
*  staging_schema = 'staging'
*  dw_schema = 'datawarehouse'

# Start Up
Spin up a docker instance of postgres and the directory watcher. 
There is an option to use volumes to persist the data. Check the commmented lines within the docker-compose.yamml. 
If this services is to interact with other docker containers they must all use the network created there too.
$ `docker-compose up -d`

### check that the images are up
$ `docker ps`

We make the assumption that a job will push the flat file into the import folder. The below command simulates a new file entering the directory.
Put the target file in the root of the project and run below. The container is named **'app'** as defined in the docker-compose file.

$ `docker cp 2019_free_title_data.csv app:app/imports`

And check the logs to see if the process ran successfully

$ `docker-compose logs`

To tear down everything successfully and remove the app image.

$ `docker-compose down && docker rmi trigifytest-app`

# Analysis
Most of the requested analysis wanted is sufficient in views. However, if this data was called regularly we could use materialised views.
If the system became extremely large the views could be pivoted into tables through the use of models and fixed schemas. 
I have provided somme examples of how you could make these types of tables in the models directory. Clustering could be applied on any categorical data. 




