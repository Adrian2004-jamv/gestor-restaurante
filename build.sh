#!/usr/bin/env bash

set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput

python manage.py migrate

if [ "${CARGAR_DATOS_INICIALES:-False}" = "True" ]; then
    python manage.py loaddata datos_pedidos.json
fi