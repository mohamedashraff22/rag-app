# rag-app

## Requirements

* Python 3.11 or above

### Install Dependencies

```bash
sudo apt update
sudo apt install libpq-dev gcc python3-dev
```

### Install Python using MiniConda

1. Download and install MiniConda from [here](https://www.google.com/search?q=%23)
2. Create a new environment using the following command:

```bash
conda create -n rag-app python=3.11
```

3. Activate the environment:

```bash
conda activate rag-app-env
```

### (Optional) Setup you command line interface for better readability

```bash
export PS1="\[\033[01;32m\]\u@\h:\w\n\[\033[00m\]\$ "
```


## Installation

### Install the required packages

```bash
pip install -r requirements.txt
```

### Setup the environment variables

```bash
cp .env.example .env
```

## Run the FastAPI server

```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

## Run the pgvector container (service)
```bash
$ sudo docker compose up pgvector -d
```

### Run Alembic Migration

```bash
$ alembic upgrade head
```

### Run

```
$ sudo docker compose up --build
```