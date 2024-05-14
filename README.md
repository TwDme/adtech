API for analytics queries

Fastapi + duckdb

Basically it started as a technical assignment:

There is an openapi specification, the task was to create a docker compose and API based on this specification for analytics

To start just run docker

docker-compose up --build


Then you can send requests to http://127.0.0.1:5000
for example http://127.0.0.1:5000/analytics/query?metrics=metric1, metric2&groupBy=attribute1&granularity=daily&filters=attribute1__in_=200,300|attribute2__gte=100


TODOs
SSL, auth, cache is broken, crud, Graphql(explore)
 

