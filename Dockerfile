FROM ubuntu:14.04

# Get base dependencies
RUN apt-get update && apt-get install -q -y \
  python2.7 \
  python-pip \
  git \
  libpq-dev \
  python-dev

RUN pip install -U six

# Copy this git repo into the /dataflow directory of the container:
ADD . /app

# Install python dependencies
RUN cd /app && pip install -U -r requirements.txt

# This command will run when running the container:
#CMD python /app/cherrypy-server.py
CMD python /app/server.py ecfb7f4745 http://requestb.in/sqmxgzsq
