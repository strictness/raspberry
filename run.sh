#!/bin/bash
export FLASK_APP=raspberry
export FLASK_ENV=development
export FLASK_RUN_HOST=0.0.0.0
export FLASK_RUN_PORT=8080
flask db-init
flask run