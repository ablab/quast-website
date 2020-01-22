FROM ubuntu:16.04

# Setup a base system
RUN apt-get update && \
    apt-get install -y curl wget g++ make libboost-all-dev git \
        tar gzip bzip2 build-essential \
        python2.7-dev python-setuptools python-pip python-virtualenv \
        zlib1g-dev default-jdk perl mysql-server && \
    apt-get upgrade -y libstdc++6

### Install conda
RUN wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh \
    && chmod +x miniconda.sh
RUN /miniconda.sh -b -p /miniconda && rm miniconda.sh
ENV PATH=/miniconda/bin:$PATH
RUN conda config --set always_yes yes --set changeps1 no
RUN conda config --add channels anaconda --add channels bioconda --add channels conda-forge
RUN conda update conda

# Create an environment
RUN conda create -n quast -c bioconda -c anaconda -c conda-forge \
    quast matplotlib sqlite django mysql-python sqlalchemy celery \
    django-celery django-autoslug
ENV PATH=/miniconda/envs/quast/bin:$PATH

# Clone command line quast application:
RUN git clone --recursive https://github.com/ablab/quast-website.git source
WORKDIR source
RUN git submodule init
RUN git submodule update

# Initialize database
RUN ./manage.py migrate

# Start celery that will process tasks
RUN ./manage.py celeryd
