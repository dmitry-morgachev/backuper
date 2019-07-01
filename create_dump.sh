#!/bin/bash


docker exec -i $(docker ps | grep db | awk '{{ print $1 }}') pg_dump -h localhost -U ${POSTGRES_USER} ${POSTGRES_DB} > db.sql
7z a backup.7z db.sql ${MEDIA_ABSOLUTE_PATH}
python3 backuper.py

exit 0
