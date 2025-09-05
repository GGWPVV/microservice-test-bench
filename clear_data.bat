@echo off
echo Clearing all databases...
docker exec -it userdb psql -U userpostgres -d userdb -c "TRUNCATE users CASCADE;"
docker exec -it scoredb psql -U scorepostgres -d scoredb -c "TRUNCATE user_scores CASCADE;"
docker exec -it mongo mongo -u mongouser -p mongopass --authenticationDatabase admin analytics_db --eval "db.dropDatabase()"
docker exec -it redis redis-cli FLUSHALL
echo Done! All data cleared.