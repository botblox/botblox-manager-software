FROM continuumio/miniconda3:4.9.2

COPY /app.py /botblox/
COPY /vlan_config.py /botblox/
COPY /requirements.txt /botblox/

RUN pip install -r /botblox/requirements.txt

WORKDIR /botblox

ENV PATH /opt/conda/envs/env/bin:$PATH

<<<<<<< HEAD
CMD ["app.py"]
ENTRYPOINT ["python"]
=======
# CMD ["app.py"]
# ENTRYPOINT ["python"]
>>>>>>> efb9f3b0fc737cd1bfb0887c1f72177317797803
