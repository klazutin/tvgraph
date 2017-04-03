db = db.getSiblingDB("tvgraph");
sleep(1000);
db.createUser({user: "tvgraph", pwd: "tvgraph123", roles: ["readWrite"]});
sleep(1000);
db.tvseries.createIndex({show_title: "text"});
sleep(1000);
db.tvseries.createIndex({"created_at": 1}, {expireAfterSeconds: 43200});
sleep(1000);