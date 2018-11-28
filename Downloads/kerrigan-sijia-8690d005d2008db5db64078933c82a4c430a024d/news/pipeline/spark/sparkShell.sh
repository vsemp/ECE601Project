#!/bin/sh
source /home/xinyu.du/python/env/bin/activate
source /home/xinyu.du/.bashrc
kinit -kt /home/xinyu.du/xinyu.du.keytab xinyu.du
HADOOP_HOME=/usr/local/hadoop-2.6.3
SPARK_HOME=/home/xinyu.du/spark/spark-2.1.0-bin-hadoop2.6
spark-submit --master yarn --deploy-mode client --num-executors 80 --deploy-mode client --executor-cores 2 --executor-memory 6g  --queue pix --conf spark.dynamicAllocation.cachedExecutorIdleTimeout=10m  --conf spark.dynamicAllocation.maxExecutors=200 --conf spark.dynamicAllocation.minExecutors=2 --conf spark.port.maxRetries=128 /home/xinyu.du/git/kerrigan/news/pipeline/spark/mongo_backup.py