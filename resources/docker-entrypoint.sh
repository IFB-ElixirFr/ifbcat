#!/usr/bin/env bash

function msg_info {
   echo -e "\033[1;32m$1\033[0m"
}

function msg_warning {
   echo -e "\033[1;33m$1\033[0m"
}

function msg_error {
   echo -e "\033[1;31m$1\033[0m"
}

cd /code

msg_info "Applying database migrations"
python manage.py migrate

#msg_info "Compilling localization (.po -> .mo)"
#python manage.py compilemessages

STATIC_ROOT_DIR=$(python manage.py shell -c "from django.conf import settings; print(settings.STATIC_ROOT)")
msg_info "Creating static root at $STATIC_ROOT_DIR"
if [ "$STATIC_ROOT_DIR" != "" ]; then
    mkdir -p $STATIC_ROOT_DIR
    chmod 777 $STATIC_ROOT_DIR
else
    msg_warning "settings.STATIC_ROOT missing, passed"
fi

msg_info "Collecting static files"
python manage.py collectstatic --noinput

#MEDIA_ROOT_DIR=$(python manage.py shell -c "from django.conf import settings; print(settings.MEDIA_ROOT)")
#msg_info "Creating media root at $MEDIA_ROOT_DIR"
#if [ "$MEDIA_ROOT_DIR" != "" ]; then
#    mkdir -p $MEDIA_ROOT_DIR
#    chmod 777 $MEDIA_ROOT_DIR
#else
#    msg_warning "settings.MEDIA_ROOT missing, passed"
#fi

#Setting up cron tasks
#msg_info "Registering cron tasks"
#if [ "$(pip freeze | grep django-crontab | wc -l )" == "1" ]; then
#    python manage.py crontab add
#    service cron start
#    grep = /code/resources/default.ini /code/resources/local.ini -h | sed "s/^\(.*\)$/export \1/g" > /root/env.sh
#else
#    msg_warning "django-crontab missing, passed"
#fi

if [ "$START_HUEY" == "False" ]
then
    msg_info "Do not start huey"
else
    msg_info "Start huey"
    python manage.py run_huey &
    msg_info "Start huey started"
fi

exec "$@"