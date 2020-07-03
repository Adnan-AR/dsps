# DSPS

## Plan

### Core
First step is to create the Core. It contains these modules:

 1. String Match module that match patterns in a text :heavy_check_mark:   
 2. Fuzzy Match module that correct unfound patterns after strign matching operation :heavy_check_mark: |  
 3. Value Mapper that maps values from a database to there respective keys that are found patterns in this case :heavy_check_mark: |  
 4. Emotional Analyzer that computes emotions of a verbatim (text as string) :warning: Need to be refactored :warning:

### Connectors 
Second step is to create the connectors. Some of these connectors:

 1. Redis Connector that Get and Set data from and to in memory database (Redis obviously) using the needed format :heavy_check_mark:
 2. Redis-Elasticsearch Connector that download and upload emotional dictionary from and to Elasticsearch :heavy_check_mark:
 
 
### Data Transformers
Third step is to create transformers because some data need to be transformed, e.g. while loading data from Elasicsearch patterns requires some transformation such as white space padding at both ends of the word. Some of this transformers are:

 1. Vebratim transformers: it pre-processes input data before emotional (and other type of) analysis. :warning: TODO :warning:
 2. Dictionary transformer: it pre-processes data between Elasticsearch and Redis in-memory database (basically the emotional dictionary) :warning: Under progress :warning:

:warning:

### Upcoming
The preceding section covers the realtime processing, architecture to includes more entity for the batch processing such as Queueing and Multiprocessing

:warning: