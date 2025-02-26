# execute after cloning
py -m venv venv # create new virtual environment
venv/Scripts/activate # activate virtual environment
pip install -r requirements.txt # install dependencies
python manage.py makemigrations # make migrations (to recreate the database)
python manage.py migrate # apply migrations

# to run the server: python manage.py runserver
# if new libraries are added: pip freeze > requirements.txt