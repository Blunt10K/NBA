# Data engineering

This branch is devoted to the data collection and exploratory analysis of box score and play-by-play data. We make use of Apache Airflow to schedule web scraping/data collection tasks and Apache Spark to process data for a personal database. The processed data goes into their respective tables in a MySQL table. The database has the following schema:

![Schema diagram](schema.svg?raw=true "NBA database schema")


## Organisation

The directories in this branch contain code for Airflow DAGs that can be used for the automated collection of their respective data. 

### Box scores

These contain traditional statistics collected by the NBA at the end of each game which include points, assists, personal fouls, etc.


### Play by play data

These contain data about events that occur over the course of an individual game. The data include shot locations and types, violations, rebounds and descriptions of the event. The events are timestamped with repsect to the periods they occur in and include players involved.