@echo off

cd /d C:\GitHub\carlentini-rss

echo ============================
echo Aggiornamento feed RSS
echo ============================

python generate_feed.py

git add .

git commit -m "Aggiornamento automatico feed RSS"

git push

echo ============================
echo Operazione completata
echo ============================

pause