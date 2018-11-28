#!/bin/bash
DATE=`date +%Y-%m-%d --date "3 days ago"`
echo $DATE
rm /pixdata/data/news/log/news_*_${DATE}_*
