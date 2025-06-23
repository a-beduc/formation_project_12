# Epic Events CRM CLI - Project 12

twelfth project for the online course of python application development on 
OpenClassrooms.

<p align="center">
    <img    alt="Logo of the Softdesk company" 
            style="width:70%; height:auto;" 
            src="doc/logo.png" 
            title="Logo of Epic Events" />
</p>

## Description

Epic Events CRM is a Command Line Interface (CLI) created for an imaginary company "Epic Events". 
The application allows its users to communicate with a locally deployed 
database. It is configured to work with PostgreSQL but may be easily altered 
to accept any kinds of data storing systems.

## Features
* Secure authentication with JWT.
* Manage collaborators, clients, contracts and events with a single line of command.
* Strict permissions enforced by the combination of a Role Based Access Control (RBAC) and an Attribute Based Access Control (ABAC).
* Command Line Interface (CLI) implemented with Click.
* Local and Online (Sentry) logging available.

For a quick lookup for available commands go to [DOC.md](DOC.md)

## Architecture
do later

## Project Design
On a design level, this application is an attempt at using the principles of 
Domain Driven Development, where modularity and abstractions will ease 
maintainability and evolution of the code base. It was made shamelessly 
referencing and reusing the concepts of the part 1 of this online book : 
[Architecture Patterns with Python](https://www.cosmicpython.com/book/preface.html) 
by Harry Percival and Bob Gregory.

<p align="center">
    <img    alt="Logo of the Softdesk company" 
            style="width:60%; height:auto; border: black 3px dotted; border-radius: 15px" 
            src="doc/diagram.png" 
            title="Logo of Epic Events" />
</p>



## Installation & Launch
do later



Project 12 for the OC python developer course.

Goal is to create a CLI that can communicate with a DB using SQLAlchemy.



tempo notes:
idea : create different db users (one per role) and limit their 
action at the db level to add a layer of security
