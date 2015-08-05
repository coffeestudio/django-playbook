#!/usr/bin/python
# coding=utf-8
import importlib

import json
import re
import shlex
import os
import sys

args_file = sys.argv[1]
args_data = file(args_file).read()
args = dict(map(lambda x: tuple(x.split('=')), shlex.split(args_data)))
manage_script = args['app_dir'] + '/manage.py'

change_uid = None
if hasattr(args, 'owner'):
    change_uid = args['owner']
else:
    change_uid = os.stat(manage_script).st_uid
os.setuid(change_uid)

settings = None
with open(manage_script) as f:
    settings_start_re = re.compile('^\s*if\s+__name__\s+==\s+[\'"]__main__[\'"]\s*:\s*')
    settings_end_re = re.compile('^\s*execute_from_command_line(sys.argv)\s*')
    run_line = False
    for line in f:
        if not line:
            continue
        if not run_line and settings_start_re.match(line):
            run_line = True
            continue
        elif 'DJANGO_SETTINGS_MODULE' in os.environ or settings_end_re.match(line):
            break
        if run_line:
            exec(line.strip())
    settings = os.environ.get('DJANGO_SETTINGS_MODULE', None)

if not settings:
    raise RuntimeError

sys.path.append(args['app_dir'])
s = importlib.import_module(settings)

print json.dumps({'wsgi_application': s.WSGI_APPLICATION, 'static_url': s.STATIC_URL, 'media_url': s.MEDIA_URL})
