EXPIRE_DATE=`date +%Y-%m-%d --date "14 days ago"`
STO_PRE=/pixdata/data/news/storage/newsfeeds_

for i in {7,1,2,3}
    do
        DATE=`date +%Y-%m-%d --date "$i days ago"`
        echo begin newsfeeds_$DATE
        TMP_FILE=/user/$USER/newsfeeds_$DATE
        RES_FILE=/user/pix/news/newsfeeds_$DATE\_20160603_3
        STORAGE_FILE=$STO_PRE$DATE
        echo begin scp from matrix03 $STORAGE_FILE
        scp $USER@matrix03:$STORAGE_FILE $STORAGE_FILE
        echo scp from matrix03 $STORAGE_FILE done
        /usr/local/hadoop-2.6.3/bin/hadoop fs -rm $TMP_FILE
        /usr/local/hadoop-2.6.3/bin/hadoop fs -rm -r $RES_FILE
        /usr/local/hadoop-2.6.3/bin/hadoop fs -put $STORAGE_FILE $TMP_FILE
        /usr/local/hadoop-2.6.3/bin/hadoop jar /usr/local/hadoop-2.6.3/share/hadoop/tools/lib/hadoop-streaming-2.6.3.jar \
            -Dstream.map.input.ignoreKey=true \
            -Dstream.non.zero.exit.is.failure=false \
            -Dmapred.map.tasks.speculative.execution=false \
            -Dmapred.reduce.tasks=10 \
            -Dmapred.job.name='compress data' -libjars "/usr/local/hadoop-2.6.3/share/hadoop/common/lib/hadoop-lzo-0.4.20-SNAPSHOT.jar" \
            -Dmapred.output.compress=true \
            -Dmapred.output.compression.codec=com.hadoop.compression.lzo.LzopCodec \
            -Dmapreduce.output.fileoutputformat.compress.type=BLOCK \
            -input $TMP_FILE \
            -output $RES_FILE \
            -mapper "/bin/cat" \
            -reducer "/bin/cat"
        # scp newsfeeds_$DATE hadoop-am:/home/hongjun/data/news/raw/
        /usr/local/hadoop-2.6.3/bin/hadoop fs -rm $TMP_FILE
        echo persist newsfeeds_$DATE done
    done
    rm $STO_PRE$EXPIRE_DATE
    echo remove expire file done
