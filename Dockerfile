FROM ubuntu:16.04
MAINTAINER ahattimare@umass.edu

WORKDIR /usr/src/app

# Disable interactive input. This is needed to install mongodb.
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y \
    gnupg \
    wget \
    g++ \
    make \
    zlib1g-dev \
    software-properties-common \
    unzip \
    default-jre \
    git \
    apt-transport-https ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Download Indri search engine for document retrieval.
RUN wget --no-check-certificate https://sourceforge.net/projects/lemur/files/lemur/indri-5.11/indri-5.11.tar.gz \
    && tar -xvzf indri-5.11.tar.gz \
    && rm indri-5.11.tar.gz

# Install Indri.
RUN cd indri-5.11 \
    && ./configure CXX="g++ -D_GLIBCXX_USE_CXX11_ABI=0" \
    && make \
    && make install

# Install pip but not to the latest version as it does not support pyndri installation due to Python 2.7 incompatibility.
# https://stackoverflow.com/questions/65896334
RUN apt-get update && apt-get install -y python3-pip \
    && pip3 install --upgrade "pip < 21.0"

RUN pip3 install pyndri

RUN apt update && apt install -y ffmpeg

# Install all dependencies mentioned in the macaw requirements document.
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

RUN pip3 install torch

# Download Stanford core NLP data if user has not specified a local volume. This is a 400MB compressed file.
ARG download_stanford_corenlp=false
RUN if $download_stanford_corenlp ; then \
    wget -O "stanford-corenlp-full-2017-06-09.zip" "http://nlp.stanford.edu/software/stanford-corenlp-full-2017-06-09.zip" \
    && unzip "stanford-corenlp-full-2017-06-09.zip" \
    && rm "stanford-corenlp-full-2017-06-09.zip" ; fi

# Download and install FAIR DrQA module.
RUN git clone https://github.com/facebookresearch/DrQA.git
RUN cd DrQA \
    && pip3 install -r requirements.txt \
    && python3 setup.py develop

# Download a pre-trained DrQA model if user has not specified a local volume. This is a 7.5GB compressed file download
# and requires 25GB of uncompressed space. To save Docker image memory, it is recommended to use external file as volume.
ARG download_drqa_model=false
RUN if $download_drqa_model ; then cd DrQA && ./download.sh ; fi

# Install MongoDB server https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/
RUN wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | apt-key add -
RUN echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/4.4 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-4.4.list
RUN apt-get update && apt-get install -y mongodb-org

# Create the MongoDB data directory.
RUN mkdir -p /data/db

# Copy directory that contains trectext documents needed for Indri retriever.
COPY trec_documents trec_documents

# Build indri index in directory /usr/src/app/indri-5.11/buildindex/my_index. Not needed if running with Bing.
ARG use_indri_retriever=true
RUN if $use_indri_retriever ; then cd indri-5.11/buildindex \
    && ./IndriBuildIndex -memory=100M -corpus.class=trectext -index=my_index \
    -stemmer.name=Krovetz -corpus.path=/usr/src/app/trec_documents \
    ; fi

# Copy files and directories from workspace to Docker container.
COPY macaw macaw
COPY scripts scripts
COPY setup.py setup.py

ENV PYTHONPATH="$PYTHONPATH:/usr/src/app"

# Install Macaw.
RUN python3 setup.py install

# Run the script that will start MongoDB and run python application.
CMD ["/bin/bash", "scripts/start.sh"]
