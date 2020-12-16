FROM continuumio/miniconda3:4.9.2

COPY /app.py /botblox/
COPY /requirements.txt /botblox/

RUN conda create --name switchblox-env --file requirements.txt
RUN echo "source activate env" > ~/.bashrc

ENV PATH /opt/conda/envs/env/bin:$PATH
