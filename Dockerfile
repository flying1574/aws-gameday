FROM ubuntu:14.04

# Get base dependencies
RUN apt-get update && apt-get install -q -y \
  python2.7 \
  python-pip \
  git \
  libpq-dev \
  python-dev

# Copy this git repo into the /dataflow directory of the container:
ADD . /app

# Install python dependencies
RUN cd /app && pip install -r requirements.txt

# This command will run when running the container:
CMD python /app/cherrypy-server.py
