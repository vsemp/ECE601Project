#!/usr/bin/env bash
/home/zhongzhou.dai/spark/bin/spark-submit --master spark://matrix03:7077 --packages org.apache.spark:spark-streaming-kafka_2.10:1.6.1 --py-files /home/zhongzhou.dai/feeds/generator/generator-1.0-py2.7.egg /home/zhongzhou.dai/feeds/generator/execute.py
