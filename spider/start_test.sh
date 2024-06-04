clear
rm -r downloads/*
ps aux | grep firefox | grep -v grep | awk '{print $2}' | xargs kill
scrapy crawl advert2 -a urlsfile=data.json