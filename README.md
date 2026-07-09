# mmar-pm-service
This repo is a prototypical implementation of a process mining service for the mmar modeling platform.

The service uses the PM4Py library to handle process mining request coming from the modeling client and saves the results to the mmar database. The results can be visualised via the modeling client. 

## Installation
For a quick and easy setup, use the docker installation project at https://github.com/shuerzeler/mmar-docker-installation and follow the instructions in the README.

## API Endpoints
- `POST /run?algorithm={alpha|inductive|heuristic|bpmn_inductive}` — Upload an event log and run the selected algorithm. Accepts `.csv` or `.xes` files as multipart form data. For .csv a column mapping should be added (see supported inputs)
- `GET /health` — Health check endpoint.
- `GET /test-petrinet-uuids` — Test endpoint to verify Petri Net UUID resolution against the database.
- `GET /test-bpmn-uuids` — Test endpoint to verify BPMN UUID resolution against the database.

## Supported Inputs
The service can handle a .csv or .xes event log file.
For the .csv a column mapping with the following names in the REST call is required
- `case_id` — column name for the case identifier
- `activity_name` — column name for the activity
- `timestamp` — column name for the timestamp

## Supported Algorithms and Outputs
The following algorithms are implemented, to specify the algorithms the value has to be added to the call "algorithm" variable.

Alpha Miner (alpha) -> outputs Petri Net
Inductive Miner (inductive or bpmn_inductive) -> has Petri Net and BPMN versions
Heuristic Miner (heuristic) -> outputs Petri Net

## License
This repository is licensed under the GNU AFFERO GENERAL PUBLIC LICENSE Version 3.