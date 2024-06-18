# Basic Python notebook
Notebook : [Basic pyhton](./Basic%20pyhton.ipynb)

# Python Website
Python offical website : [https://www.python.org](https://www.python.org)

# Pyenv Website (Python version manager)
Official git : [https://github.com/pyenv/pyenv](https://github.com/pyenv/pyenv)

Git for installation on windows  : [https://github.com/pyenv-win/pyenv-win](https://github.com/pyenv-win/pyenv-win)

Tutorial : [https://realpython.com/intro-to-pyenv](https://realpython.com/intro-to-pyenv)



# Online tool to test and run python
Google colab : [https://colab.research.google.com](https://colab.research.google.com)

# Some comman pyenv commands

### list all python versin that can be installed using pyenv
    pyenv install --list

### install specific python version using pyenv
    pyenv install -v 3.11.0

### un-install specific python version using pyenv
    pyenv uninstall 2.7.15

### check all python version installed using pyenv
    pyenv versions

### set specific python version as global in OS using pyenv 
    pyenv global 2.7.15

### set specific python version as local(for specific project/folder) in OS using pyenv 
    pyenv local 2.7.15

### check all pyenv commands present
    pyenv commands

# Some comman python commands

### check python version
    python --version

### to open python shell to run python command in terminal
    python

# FastAPI Documentation
Fast API : [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com)

## Some important commands for FastAPI

### install fastapi
    pip install fastapi

### install ASGI server to run fastapi
    pip install "uvicorn[standard]"

### to run fastapi application
    uvicorn main:app --reload

# Langchain (🔗) Documentation
Langchain : [https://www.langchain.com/](https://www.langchain.com/)

Langchain Introduction : [https://python.langchain.com/docs/get_started/introduction/](https://python.langchain.com/docs/get_started/introduction/)

Langchain coding guide : [https://python.langchain.com/docs/integrations/platforms/](https://python.langchain.com/docs/integrations/platforms/)

## Some important commands for langchain 

### install langchain
    pip install langchain

### install dependencies given in requirement.txt file to run the api
    pip install -r requirements.txt