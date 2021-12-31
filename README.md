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
