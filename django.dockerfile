FROM python:3.12

RUN apt-get update && \
    apt-get install -y \
        nano \
        wget \
        gettext \
        python3-dev \
        cron \
 && rm -rf /var/lib/apt/lists/* \
 && python -m pip install --upgrade pip

ENV PYTHONUNBUFFERED=1
EXPOSE 8000
RUN mkdir /code
WORKDIR /code
CMD ["gunicorn", "--bind", ":8000", "ifbcat.asgi:application", "-k", "uvicorn.workers.UvicornWorker"]

COPY requirements.txt /code/
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

COPY ./resources/*-entrypoint.sh /
RUN chmod a+x /*-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]

COPY . /code/

ARG CI_COMMIT_SHA
ARG CI_COMMIT_DATE

RUN echo "{\"commit_sha\":\"$CI_COMMIT_SHA\",\"commit_date\":\"$CI_COMMIT_DATE\"}">/code/source_info.json

#END OF FILE