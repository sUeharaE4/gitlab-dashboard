[![Maintainability](https://api.codeclimate.com/v1/badges/09cde8ffb601f6c13bdf/maintainability)](https://codeclimate.com/github/sUeharaE4/gitlab-dashboard/maintainability)

# Gitlab-Dashboard

Create a dashboard to visualize the activities of the development team using gitlab.

Most of the features have not been created yet. I plan to implement them little by little over time. When the functions are ready, I'll introduce them with images.

## Dashboard sample image
Coming soon.

## Install poetry(if you haven't)
If you don't have poetry, you have to install(python is also required). See detail at poetry doc https://python-poetry.org/docs/ .

Linux:
```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

Windows:(use PowerShell)
```powershell
(Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python -
```

## Install python libs
for production:
```bash
poetry install --no-dev
```

for develop:
```bash
poetry install
```

## Set env
This application reference some environment variables. Please set these vars.

| var           | explain                                                                                                                            |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| APP_EXEC_MODE | mode is used to decide which environment file be read( .app_prop_${APP_EXEC_MODE}). set prod or something you like.                |
| GITLAB_HOME   | this var is used for only build gitlab container. if you don't have gitlab instance, you can use container. see docker-compose.yml |

```bash
export APP_EXEC_MODE=test
export GITLAB_HOME=/svr/gitlab
```

### For developer
make `.env` file and set like this to refer `PYTHONPATH` from VSCode.

```.env
PYTHONPATH=./src
```