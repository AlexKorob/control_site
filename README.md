## Control site (API)

#### Prepare project:

```bash
  git clone https://github.com/AlexKorob/control_site.git
  cd control_site
  python3 -m venv ./venv
  . venv/bin/activate
  cd place_for_ads
  pip3 install -r requirements.txt
```

#### Configuration Postgresql:

```bash
  sudo su - postgres
  psql
  CREATE DATABASE place_for_ads;
  CREATE USER alex WITH PASSWORD '123';
  GRANT ALL PRIVILEGES ON DATABASE place_for_ads TO alex;
  ALTER USER alex CREATEDB;
  \q
  logout
```

#### Migrate and load fixtures

```bash
  ./manage.py migrate
  ./manage.py loaddata ads.json
```

#### Run tests:

```bash
  ./manage.py test
```

#### Start Celery (in new terminal with activated virtual environment):

```bash
  celery -A ads worker --hostname="worker" -l info
```

#### Start site:

```bash
  ./manage.py runserver
```

#### Users:
<p><b>username:</b> alex; <b>password:</b> 123  <---- superuser </p>
<p><b>username:</b> alexandr; <b>password:</b> 1234567dD  <---- simple user </p>

#### Entry Point:

http://127.0.0.1:8000/swagger/


#### Possible improvement:
<p>To implement this improvement, you need add functionality "buy product with delivery".</p>

When you create ad, you can choose a "private person" or "business" (as well as on the OLX).\
If you created ad with the "business" option and activated the buy with delivery function,\
then all users who bought this product from the ad with using "buy product with delivery",\
can put rating on the ad from 1 to 5 stars.
