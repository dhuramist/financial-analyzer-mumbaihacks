#!/usr/bin/env bash
service nginx start
chown -R www-data:www-data /srv/flask_app/logs
chmod -R 775 logs
uwsgi --ini uwsgi.ini

