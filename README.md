# rag-app

## Requirements

* Python 3.8 or above

### Install Dependencies

```bash
sudo apt update
sudo apt install libpq-dev gcc python3-dev
```

### Install Python using MiniConda

1. Download and install MiniConda from [here](https://www.google.com/search?q=%23)
2. Create a new environment using the following command:

```bash
conda create -n rag-app python=3.10
```

3. Activate the environment:

```bash
conda activate rag-app
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
