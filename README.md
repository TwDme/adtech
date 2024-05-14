API for analytics queries
Fastapi + duckdb

To start just run docker
docker-compose up --build

You will see that the table event is created with 0 rows.
Then we inserted some dummy data there.
Then you can send requests to http://127.0.0.1:5000
for example http://127.0.0.1:5000/analytics/query?metrics=metric1, metric2&groupBy=attribute1&granularity=daily&filters=attribute1__in_=200,300|attribute2__gte=100


TODOs
SSL, auth, cache is broken, crud, Graphql(explore)
 

