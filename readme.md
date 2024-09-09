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
The project requires pipenv as means to manage dependencies. 
A folder for **logs** and **imports** / **exports** is needed as well. 
Not included in the push as it would be bad dev practice as it could contain secrets!.

$ `
git clone git@github.com:Botman-Hotman/DataProcessor.git &&  
cd DataProcessor && 
mkdir logs imports exports &&  
touch .env
`

# Environment Vars
Add the following settings into the .env file created in the command above.
The following vars are designed to work for the docker container, adjust if you wish to use a local instance of postgres.
If **dev** is true it will drop and recreate all the tables within the database on every startup.

*  dev = True
*  debug_logs = False
*  db_string = 'postgresql//dev-user:password@postgres:5432/dev_db'
*  db_string_async = "postgresql+asyncpg://dev-user:password@postgres:5432/dev_db"
*  echo_sql = False
*  init_db = True
*  staging_schema = 'staging'
*  dw_schema = 'datawarehouse'

# Start Up
Spin up a docker instance of postgres and the directory watcher. 
There is an option to use volumes to persist the data. Check the commented lines within the docker-compose.yamml. 
If this services is to interact with other docker containers they must all use the network created there too.

$ `docker-compose up -d`

### check that the images are up
$ `docker ps`

We make the assumption that a job will push the flat file into the import folder. The below command simulates a new file entering the directory.
Put the target file in the root of the project and run below. The container is named **'app'** as defined in the docker-compose file.

**NOTES**: _I think the watcher is quicker than what the cp command of docker is. 
A few times it was only pick up some of the file and not the full 5000 rows. 
If this happens I recommend truncating the table in the db and trying it again._ 

$ `docker cp 2019_free_title_data.csv app:app/imports`

### check the logs to see if the process ran successfully

$ `docker-compose logs`



# ETL
Now we have imported data into the staging schema we can run the next command to generate the data warehouse 
and run the ETL pipelines. After this runs you will see the target tables in the database under datawarehouse schema. 

$ `docker exec -it app python main.py --pipeline`


# Analysis
This will run the correct scripts to create views in the data warehouse of the target questions.

$ `docker exec -it app python main.py --analysis`


# Tear down 
remove the container and remove the app image.

$ `docker-compose down && docker rmi trigifytest-app`



# Conclusion

* I would use views instead of making tables if the data is not large (< 1M rows).
* I opted to transform the data as it was being pulled into the staging table, 
this isn't very efficient if you want to make the functions reusable for any flat file, and it could be done in SQL as it is more efficent at this kind of operation. 
* If the tables became to large clustering and partitioning could be used to make indexing them more efficient.

## Challenges Faced
The files format was not obvious from the get go but after reading that the related titles were orginally a list made it easier to plan the pipeline. 
This system would face some issues if the table was updated with new and existing data. One work around would be to take a hash and converting to a UUID of the row data after cleaning it up and using this as primary key and using that to find existing data to update. 
