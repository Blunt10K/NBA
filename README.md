# Data engineering

This branch is devoted to the data collection and exploratory analysis of box score and play-by-play data. We make use of Apache Airflow to schedule web scraping/data collection tasks and Apache Spark to process data for a personal database. The processed data goes into their respective tables in a MySQL table. The database has the following schema:

![Schema diagram](schema.svg?raw=true "NBA database schema")


# Some basic analyses
Some exploratory analyses are included in the notebooks.
