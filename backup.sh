#!/bin/bash

echo $(date)

cd /home/django/shop/

# �������� ����������� ���������, ����� ���� ���� ������, ����������� ���������.
. ./venv/bin/activate

python manage.py dumpdata > db.json

#python manage.py dumpdata --exclude=contenttypes > db.json

deactivate



# ������ � �����, ������, ���. ��� �� ssh � ��������� ������.
git add .
set timeout 2

git commit -m "automatic copying"
set timeout 2

git push shopBit master
set timeout 2
