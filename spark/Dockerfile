FROM apache/spark:3.5.1

WORKDIR /app

COPY spark_job.py /app/

CMD ["spark-submit", "/app/spark_job.py"]