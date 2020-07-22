# ifbcat-sandbox

Experimental code for the IFB Catalogue REST API.

This is a sandbox project for developing new features of the IFB Catalogue REST API. The code here will be moved to https://github.com/IFB-ElixirFr/IFB-resource-catalog once fully tested and evaluated.

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