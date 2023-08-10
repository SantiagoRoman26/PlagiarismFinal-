FROM python:3.11

ENV PYTHONNUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y sudo

RUN sudo apt update && sudo apt install -y --force-yes libblas-dev liblapack-dev libblas3 libgfortran5 liblapack3

RUN pip install --upgrade pip 

# Instala Java
RUN apt-get update && apt-get install -y default-jre

COPY ./requirements.txt ./

RUN pip3 install -r requirements.txt

RUN WGET http://search.maven.org/remotecontent?filepath=org/apache/tika/tika-server-standard/2.6.0/tika-server-standard-2.6.0.jar

RUN java -jar tika-server-2.6.0.jar

COPY ./ .

EXPOSE 8000

CMD ["sh", "entrypoint.sh"]