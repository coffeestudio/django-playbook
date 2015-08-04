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
settings_re = re.compile('\s*settings\s*=.*$')
with open(manage_script) as f:
    for line in f:
        if settings_re.match(line):
            exec(line.strip())
            break

if not settings:
    raise RuntimeError

sys.path.append(args['app_dir'])
s = importlib.import_module(settings)

print json.dumps({'wsgi_application': s.WSGI_APPLICATION, 'static_url': s.STATIC_URL, 'media_url': s.MEDIA_URL})
