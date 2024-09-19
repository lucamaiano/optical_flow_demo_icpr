# Extend the official Python base
FROM python:3.11.10-slim-bullseye

# Set working directoory
WORKDIR .

# Copy the project requirements
COPY requirements.txt requirements.txt

RUN apt-get update 
RUN apt-get install -y python3-opencv
RUN apt-get install cmake g++ python3-dev -y 

# Install requirements.txt
RUN pip3 install --upgrade pip \
    && pip3 install -r requirements.txt

# Copia il codice dell'applicazione
COPY . .

# Launch the app
CMD ["python", "server.py"]