FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN python -m pip install --upgrade pip && pip install -r requirements.txt
COPY . /code/

# expose the port 8000
EXPOSE 8000

# CMD ["python", "manage.py", "makemigrations"]
# CMD ["python", "manage.py", "collectstatic"]

# define the default command to run when starting the container
CMD ["gunicorn", "--reload", "--reload-engine", "inotify", "--chdir", "catalogue", "--bind", ":8000", "catalogue.wsgi:application"]
# For dev
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
