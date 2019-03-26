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

#### Start Celery:

```bash
  celery -A ads worker --hostname="worker" -l info
```

#### Start site:

```bash
  ./manage.py runserver
```

Users:
  superuser:
    * alex | 123
  simple user:
    * alexandr | 1234567dD
