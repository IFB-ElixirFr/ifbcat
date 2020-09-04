FROM python:3.7

RUN apt-get update && \
    apt-get install -y \
        nano \
        wget \
        gettext \
        python3-dev \
        cron \
 && rm -rf /var/lib/apt/lists/* \
 && python -m pip install --upgrade pip

ENV PYTHONUNBUFFERED 1
EXPOSE 8000
RUN mkdir /code
WORKDIR /code
CMD ["gunicorn", "--reload", "--reload-engine", "inotify", "--chdir", "ifbcatsandbox", "--bind", ":8000", "ifbcatsandbox.wsgi:application"]

COPY requirements.txt /code/
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

COPY ./resources/*-entrypoint.sh /
RUN chmod a+x /*-entrypoint.sh

COPY . /code/

# expose the port 8000

# CMD ["python", "manage.py", "makemigrations"]
# CMD ["python", "manage.py", "collectstatic"]

# define the default command to run when starting the container
# For dev
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
