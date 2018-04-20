FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt;\
    ln -sf /usr/local/bin/pgcli /usr/local/bin/psql
ADD config /config/
ADD django /code/
RUN rm -rf wat_ui/static/ui/semantic/components;\
    ./manage.py collectstatic;\
    useradd -ms /bin/bash code;\
    chown code /code
USER code
EXPOSE 3000
CMD ["/config/entrypoint.sh"]