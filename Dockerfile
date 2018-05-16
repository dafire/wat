FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt;\
    ln -sf /usr/local/bin/pgcli /usr/local/bin/psql
ADD config /config/
ADD django /code/
COPY bin/* /usr/local/bin/
COPY tmp/artifacts/default.env /config/default.env
RUN rm -rf wat_ui/static/ui/semantic/components;\
    useradd -ms /bin/bash code;\
    mkdir /shared;\
    chown -R code /code /shared
USER code
RUN ./manage.py collectstatic

EXPOSE 3000
CMD ["/config/entrypoint.sh"]