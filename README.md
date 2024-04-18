
python3 -m venv ./venv

source venv/bin/activate

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

 or
 TODO Graphql

 TOOO fastAPI, SSL

 TODO

- почти полностью отсутствует валидация данных (можно было применить такие библиотеки, как pydantic)

- тесты не покрывают базовую функциональность и не соответствуют спецификации
- приложение подвержено SQL-инъекциям, можно выполнить произвольный код в базе, например, сформировав запрос: "/analytics/query?groupBy='*/--';DROP%20TABLE%20events;SELECT%201;/*&metrics=metric1&granularity=daily"
- форматирование кода не соответствует ни одному из известных принятых стандартов (например, PEP 8)

- корректно применена колоночная база данных, но ничего не сказано об ограничениях использования этой базы данных в реальных условиях (следовало описать это в документации)

- не приведены примеры использования сервиса, например, реализовать параметр filters в соответствии со спецификацией можно по-разному
 

