EXPIRE_DATE=`date +%Y-%m-%d --date "14 days ago"`
EXPIRE_FILE=/pixdata/data/news/storage/newsfeeds_$EXPIRE_DATE
for i in {7,1,2,3}
    do
        DATE=`date +%Y-%m-%d --date "$i days ago"`
        echo begin handle newsfeeds_$DATE
        python storage_news.py $i
        echo store valid newsfeeds_$DATE done 
    done
rm $EXPIRE_FILE
echo delete expire file $EXPIRE_FILE done
