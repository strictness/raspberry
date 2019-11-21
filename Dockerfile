FROM python:3.7
ADD . /raspberry
WORKDIR /raspberry
RUN pip install -r requirements.txt
RUN chmod +x run.sh
EXPOSE 8080
ENTRYPOINT ["./run.sh"]