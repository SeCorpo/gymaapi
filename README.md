### Rules

1. Models-classes don't directly interact with get_db
2. Always send the minimum and only if used personal data to client
3. never end on return True
4. Routers do not use db directly
5. Services perform query's to db
6. Every service / provider function has an explanatory description
7. Service modules manipulate database objects and are focussed on internal processes, 
they receive a database session from a router endpoint
8. Provider modules are service modules, with a more specified purpose
9. 