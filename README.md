# products
[![Build Status](https://travis-ci.org/DevOps-Charlie/products.svg?branch=master)](https://travis-ci.org/DevOps-Charlie/products)

This is the repository for DevOps project at NYU Fall 2017. We will develop a REST API for products service as a part of this project.

**To execute the files and run nosetests and code coverage:**
* vagrant up
* vagrant ssh
* cd /vagrant
* nosetests

**For BDD testing:**
* python server.py & behave

**Paths:**
* GET /ui - Displays a UI for Selenium testing
* GET /products - Returns a list all of the Products
* GET /products/{id} - Returns the Product with a given id number
* POST /products - creates a new Product record in the database
* PUT /products/{id} - updates a Product record in the database
* DELETE /products/{id} - deletes a Product record in the database
