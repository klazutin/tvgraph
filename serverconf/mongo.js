use tvgraph-test
db.createUser({user: 'tvgraph', pwd: 'tvgraph123', roles: ['readWrite']})
db.tvseries.createIndex({'created_at': 1}, {expireAfterSeconds: 43200})
db.tvseries.createIndex({show_title: 'text'})
