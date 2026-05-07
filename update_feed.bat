@echo off

cd /d C:\GitHub\carlentini-rss

echo ============================ >> log.txt
echo AVVIO %date% %time% >> log.txt

python generate_feed.py >> log.txt 2>&1

git add . >> log.txt 2>&1

git commit -m "Aggiornamento automatico feed RSS" >> log.txt 2>&1

git push >> log.txt 2>&1

echo COMPLETATO %date% %time% >> log.txt
echo ============================ >> log.txt