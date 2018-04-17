FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD config /config/
ADD django /code/
RUN rm -rf wat_ui/static/ui/semantic/components;\
    ./manage.py collectstatic
RUN useradd -ms /bin/bash code
RUN chown code /code
USER code
CMD ["/config/entrypoint.sh"]