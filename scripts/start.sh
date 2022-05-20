#!/bin/bash

echo "Inside the execution script."

# Start MongoDB as a daemon process https://docs.mongodb.com/manual/tutorial/manage-mongodb-processes/
mongod --fork --logpath /var/log/mongodb/mongod.log
echo "MongoDB started successfully."

echo "This is the python version: $(python3 --version)"

# Start the main application.
python3 macaw/live_main.py
