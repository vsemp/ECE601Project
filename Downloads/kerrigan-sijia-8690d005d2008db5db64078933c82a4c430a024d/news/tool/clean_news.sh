BEGIN_DATE=`date +%Y-%m-%d --date "100 days ago"`
END_DATE=`date +%Y-%m-%d --date "14 days ago"`
echo date range $BEGIN_DATE to $END_DATE
start=$(date -d$BEGIN_DATE +%s)
end=$(date -d$END_DATE +%s)
cur=$start
while [ $cur -le $end ];
    do
        RM_DATE=`date -d@$cur +%Y-%m-%d`
        rm -f /pixdata/data/news/uploader_$RM_DATE
        rm -f /pixdata/data/news/checker_$RM_DATE
        rm -f /pixdata/data/news/publisher_$RM_DATE
        rm -f /pixdata/data/news/newsfeeds_$RM_DATE
        rm -f /pixdata/data/news/usage/$RM_DATE
        rm -f /pixdata/data/news/share/$RM_DATE
        rm -f /pixdata/data/news/storage/newsfeeds_$RM_DATE
        let cur+=24*60*60
done
echo `date`
echo remove expired /pixdata/data/news data done
