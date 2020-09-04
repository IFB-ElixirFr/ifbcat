# ifbcat-sandbox

ifbcat is the database hosting and serving the IFB Catalogue through a REST API.

# How to contribute
Code is formatted using https://github.com/psf/black. Please use pre-commit along with black to commit only well formatted code:
```
#install dependencies
pip install -r requirements-dev.txt
#enable black as a pre-commit hook which will prevent committing not formated source 
pre-commit install
#run black as it will be before each commit
pre-commit run black
```
