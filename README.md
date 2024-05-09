


pip3 install -r requirements.txt

uvicorn main:app --reload

docker-compose up --build

You will see that the table event is created with 0 rows.
Then we inserted some dummy data there.
Then you can send requests to http://127.0.0.1:5000
for example http://127.0.0.1:5000/analytics/query?metrics=metric1,metric2&groupBy=attribute1&granularity=hourly


Not quite sure what do you mean by huge dataset so some TODOs 
TODO pagination/caching?
Looks like limit offset pagination is alright with duckdb or something like
Select * From Events where id >= 101 Order By id ASC LIMIT 100

 
TODOs
Graphql?, SSL, auth, cache is broken

fix docker
 

