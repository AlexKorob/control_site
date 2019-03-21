## Control site (API)

#### Prepare project:

```bash
  git clone https://github.com/AlexKorob/control_site.git
  cd control_site
  python3 -m venv ./venv
  . venv/bin/activate
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

#### Run tests:

```bash
  ./manage.py test
```

#### Start site:

```bash
  ./manage.py migrate
  ./manage.py runserver
```
