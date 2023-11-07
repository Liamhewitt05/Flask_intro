## Prerequisites

Before starting, install the following tools:

- Python 3.10 or later
- Pip package manager

For more information on these tools, see the public documentation on
[Python](https://www.python.org/downloads/) or
[Pip](https://pip.pypa.io/en/stable/installing/)

## Initial Setup
```bash
docker build -t
docker run -p "5000:5000" 
```

### Setup development PC
From the root of your cloned repo, generate a virtual environment with a
specific version of python.

Windows
```bash
python -m venv .venv
.venv\Scripts\activate.bat
```

Linux / MacOS
```bash
python3 -m venv .venv
. ./.venv/bin/activate
```

Next install any necessary packages.

```bash
pip install -r requirements.txt
```

## Running Locally

From the root of your cloned repo run the following:

### To run the web server

```bash
flask run --debug
```