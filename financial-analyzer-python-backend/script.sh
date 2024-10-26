#!/usr/bin/bash
uwsgi --socket 0.0.0.0:5000 --protocol=http -w /home/ec2-user/analysis_reports_server/wsgi:app

