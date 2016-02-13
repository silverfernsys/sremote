# sremote
# commands
# Export virtualenv directory
$ export VENV=~/.virtualenvs
$ mkvirtualenv sremote
$ pip install -r requirements.txt

# Run tests
$ sudo $VENV/sremote/bin/python sremote/test/coverage_runner.py

# User administration
$ sudo $VENV/sremote/bin/python sremote/sremote.py createuser
$ sudo $VENV/sremote/bin/python sremote/sremote.py deleteuser
$ sudo $VENV/sremote/bin/python sremote/sremote.py listusers

# Token administration
$ sudo $VENV/sremote/bin/python sremote/sremote.py createtoken
$ sudo $VENV/sremote/bin/python sremote/sremote.py deletetoken
$ sudo $VENV/sremote/bin/python sremote/sremote.py listtokens

# Run server
$ sudo $VENV/sremote/bin/python sremote/sremote.py runserver