# poetry-sample

This is a sample project for using poetry. It provides a template for using poetry to version control python libraries and to perform unit testing and code style checking for pytest, flake8, etc.
By using taskipy, it is possible to provide aliases defining commands for pytest and flake8. These settings can be edited in pyproject.toml.

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
