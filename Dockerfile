# FROM continuumio/miniconda3:4.9.2

# COPY /app.py /botblox/
# COPY /vlan_config.py /botblox/
# COPY /portmirror_config.py /botblox/
# COPY /requirements.txt /botblox/

# RUN pip install -r /botblox/requirements.txt

# WORKDIR /botblox

# ENV PATH /opt/conda/envs/env/bin:$PATH

# CMD ["app.py"]
# ENTRYPOINT ["python"]
