# EECRM CLI - Commands Documentation

This document list the available commands for the CLI app 'eecrm'

Every command follow this structure : 

```bash 
eecrm [resource] [action] [options]
```

## Content table
* [Authentication](#authentication)
  * [login](#login)
  * [logout](#logout)
  * [whoami](#whoami)
* [Users](#users)
  * [read](#read)
  * [change-username](#change-username)
  * [change-password](#change-password)
* [Collaborators](#collaborators)
  * [create](#create)
  * [read](#read-1)
  * [update](#update)
  * [delete](#delete)
  * [assign](#assign)
* [Clients](#clients)
  * [create](#create-1)
  * [read](#read-2)
  * [update](#update-1)
  * [delete](#delete-1)
* [Contracts](#contracts)
  * [create](#create-2)
  * [read](#read-3)
  * [delete](#delete-2)
* [Events](#events)
  * [create](#create-3)
  * [read](#read-4)
  * [update](#update-2)
  * [delete](#delete-3)


## Authentication

### login
```bash 
eecrm login
```
Start a prompt to ask the user for its credentials. Create a temporary 
JWT token in a local file to serve as authentication for following 
commands. 

### logout
```bash 
eecrm logout
```
Erase the content of the directory used for storing the JWT token.

### whoami
```bash 
eecrm whoami
```
Display information about the logged-in user to the terminal.

## Users

### read
```bash 
eecrm user read [OPTIONS] 
```
Display a list of user or a specific one using its unique ID with the -pk option.

| Option                   | Args      | Description                                | Repeatable | Example         |
|--------------------------|-----------|--------------------------------------------|------------|-----------------|
| `-pk`, `-PK`,            | `int`     | Display a specific user based on its ID    | No         | `-pk 3`         |
| `-f`, `--filter`         | `str str` | Filter with one or more field              | Yes        | `-f un user_10` |
| `-s`, `--sort`           | `str`     | Sort by one or more field                  | Yes        | `-s un`         |
| `-rc`, `--remove-column` | `str`     | Remove one or more columns from the result | Yes        | `-rc id`        |

#### --- Keywords for options using fields
* id
* username, us, un, "user name"

### change-username
Start a prompt to ask the user about its credentials to confirm identity and the new username it wants to use.

### change-password
Start a prompt to ask the user about its credentials to confirm identity and the new password it wants to use.

## Collaborators

### create
```bash 
eecrm collaborator create [OPTIONS] 
```
Create a new user and its associated collaborator. Start a prompt to ask for at least the ``username`` and the ``password`` of the new account. Unless specified, the role of any new user is ``DEACTIVATED``.

| Option                      | Args      | Description                                                                  | Repeatable | Example         |
|-----------------------------|-----------|------------------------------------------------------------------------------|------------|-----------------|
| `-d`, `--data-collaborator` | `str str` | Data given to fill in the fields of the new collaborator                     | Yes        | `-d ln Daniels` |
| `-np`, `--no-prompt`        | `None`    | Block the prompt used to complete missing information about the collaborator | No         | `-np`           |

#### --- Keywords for options using fields
* last_name, ln, "last name"
* first_name, fn, "first name"
* email, at, e_mail
* phone_number, ph, "phone number",
* role, ro

### read
```bash 
eecrm collaborator read [OPTIONS] 
```
Display a list of collaborators or a specific one using its unique ID with the -pk option.

| Option                   | Args      | Description                                     | Repeatable | Example         |
|--------------------------|-----------|-------------------------------------------------|------------|-----------------|
| `-pk`, `-PK`,            | `int`     | Display a specific collaborator based on its ID | No         | `-pk 3`         |
| `-f`, `--filter`         | `str str` | Filter with one or more field                   | Yes        | `-f ln Daniels` |
| `-s`, `--sort`           | `str`     | Sort by one or more field                       | Yes        | `-s fn`         |
| `-rc`, `--remove-column` | `str`     | Remove one or more columns from the result      | Yes        | `-rc ro`        |

#### --- Keywords for options using fields
* id
* last_name, ln, "last name"
* first_name, fn, "first name"
* email, at, e_mail
* phone_number, ph, "phone number",
* role, ro
* user_id, ui, uid, "user id"

### update
```bash 
eecrm collaborator update [OPTIONS] 
```
Update a collaborator data fields. Start a prompt to ask for data field. The ``-pk`` "option" is really a required parameter, it is needed to select the resource to update. Start a prompt to confirm before execution.

| Option                         | Args      | Description                                                                  | Repeatable | Example         |
|--------------------------------|-----------|------------------------------------------------------------------------------|------------|-----------------|
| **[ REQUIRED ]** `-pk`, `-PK`, | `int`     | **[ REQUIRED ]** Select a specific collaborator based on its ID              | No         | `-pk 3`         |
| `-d`, `--data-collaborator`    | `str str` | Data given to fill in the fields of the new collaborator                     | Yes        | `-d ln Daniels` |
| `-np`, `--no-prompt`           | `None`    | Block the prompt used to complete missing information about the collaborator | No         | `-np`           |

#### --- Keywords for options using fields
* last_name, ln, "last name"
* first_name, fn, "first name"
* email, at, e_mail
* phone_number, ph, "phone number"

### delete
```bash 
eecrm collaborator delete [OPTIONS] 
```
Delete a collaborator. The ``-pk`` "option" is really a required parameter, it is needed to select the resource to delete. Start a prompt to confirm before execution.

| Option                         | Args      | Description                                                                  | Repeatable | Example         |
|--------------------------------|-----------|------------------------------------------------------------------------------|------------|-----------------|
| **[ REQUIRED ]** `-pk`, `-PK`, | `int`     | **[ REQUIRED ]** Select a specific collaborator based on its ID              | No         | `-pk 3`         |

### assign
```bash 
eecrm collaborator assign [OPTIONS] 
```
Delete a collaborator. The ``-pk`` "option" is really a required parameter, it is needed to select the resource to delete.

| Option                            | Args  | Description                                                     | Repeatable | Example           |
|-----------------------------------|-------|-----------------------------------------------------------------|------------|-------------------|
| **[ REQUIRED ]** `-pk`, `-PK`,    | `int` | **[ REQUIRED ]** Select a specific collaborator based on its ID | No         | `-pk 3`           |
| **[ REQUIRED ]** `-ro`, `--role`, | `str` | **[ REQUIRED ]** Specify the role name                          | No         | `-ro DEACTIVATED` |

#### --- Available values for roles in the application
* DEACTIVATED, deactivated, 1
* MANAGEMENT, management, 3
* SALES, sales, 4
* SUPPORT, support, 5

## Clients

### create
```bash 
eecrm client create [OPTIONS] 
```
Create a new client. Start a prompt to ask for missing fields.

| Option                | Args      | Description                                                            | Repeatable | Example         |
|-----------------------|-----------|------------------------------------------------------------------------|------------|-----------------|
| `-d`, `--data-client` | `str str` | Data given to fill in the fields of the new client                     | Yes        | `-d ln Daniels` |
| `-np`, `--no-prompt`  | `None`    | Block the prompt used to complete missing information about the client | No         | `-np`           |

#### --- Keywords for options using fields
* last_name, ln, "last name"
* first_name, fn, "first name"
* email, at, e_mail
* phone_number, ph, "phone number"
* company, co

### read
```bash 
eecrm client read [OPTIONS] 
```
Display a list of clients or a specific one using its unique ID with the -pk option.

| Option                   | Args      | Description                                | Repeatable | Example         |
|--------------------------|-----------|--------------------------------------------|------------|-----------------|
| `-pk`, `-PK`,            | `int`     | Display a specific client based on its ID  | No         | `-pk 3`         |
| `-f`, `--filter`         | `str str` | Filter with one or more field              | Yes        | `-f ln Daniels` |
| `-s`, `--sort`           | `str`     | Sort by one or more field                  | Yes        | `-s at`         |
| `-rc`, `--remove-column` | `str`     | Remove one or more columns from the result | Yes        | `-rc ca`        |

#### --- Keywords for options using fields
* id
* last_name, ln, "last name"
* first_name, fn, "first name"
* email, at, e_mail
* phone_number, ph, "phone number"
* company, co
* created_at, ca, "create at"
* updated_at, ua, "updated at"
* salesman_id, sa, si, "salesman id", salesman

### update
```bash 
eecrm client update [OPTIONS] 
```
Update a client data fields. Start a prompt to ask for data field. The ``-pk`` "option" is really a required parameter, it is needed to select the resource to update.

| Option                         | Args      | Description                                                            | Repeatable | Example         |
|--------------------------------|-----------|------------------------------------------------------------------------|------------|-----------------|
| **[ REQUIRED ]** `-pk`, `-PK`, | `int`     | **[ REQUIRED ]** Select a specific client based on its ID              | No         | `-pk 3`         |
| `-d`, `--data-client`          | `str str` | Data given to fill in the fields of the new client                     | Yes        | `-d ln Daniels` |
| `-np`, `--no-prompt`           | `None`    | Block the prompt used to complete missing information about the client | No         | `-np`           |

#### --- Keywords for options using fields
* last_name, ln, "last name"
* first_name, fn, "first name"
* email, at, e_mail
* phone_number, ph, "phone number"
* company, co

### delete
```bash 
eecrm client delete [OPTIONS] 
```
Delete a client. The ``-pk`` "option" is really a required parameter, it is needed to select the resource to delete.

| Option                         | Args      | Description                                               | Repeatable | Example         |
|--------------------------------|-----------|-----------------------------------------------------------|------------|-----------------|
| **[ REQUIRED ]** `-pk`, `-PK`, | `int`     | **[ REQUIRED ]** Select a specific client based on its ID | No         | `-pk 3`         |

## Contracts

### create
```bash 
eecrm contract create [OPTIONS] 
```
Create a new contract. Start a prompt to ask for missing fields.

| Option                  | Args      | Description                                                              | Repeatable | Example      |
|-------------------------|-----------|--------------------------------------------------------------------------|------------|--------------|
| `-d`, `--data-contract` | `str str` | Data given to fill in the fields of the new contract                     | Yes        | `-d ta 2500` |
| `-np`, `--no-prompt`    | `None`    | Block the prompt used to complete missing information about the contract | No         | `-np`        |

#### --- Keywords for options using fields
* total_amount, ta, "total amount"
* client_id, cl, ci, "client id"


### read
```bash 
eecrm contract read [OPTIONS] 
```
Display a list of contracts or a specific one using its unique ID with the -pk option.

| Option                   | Args      | Description                                 | Repeatable | Example   |
|--------------------------|-----------|---------------------------------------------|------------|-----------|
| `-pk`, `-PK`,            | `int`     | Display a specific contract based on its ID | No         | `-pk 3`   |
| `-f`, `--filter`         | `str str` | Filter with one or more field               | Yes        | `-f ci 5` |
| `-s`, `--sort`           | `str`     | Sort by one or more field                   | Yes        | `-s ca`   |
| `-rc`, `--remove-column` | `str`     | Remove one or more columns from the result  | Yes        | `-rc si`  |

#### --- Keywords for options using fields
* id
* total_amount, ta, "total amount"
* due_amount, da, "due amount"
* signed, si
* client_id, cl, ci, "client id"
* created_at, ca, "created at"

### delete
```bash 
eecrm contract delete [OPTIONS] 
```
Delete a contract. The ``-pk`` "option" is really a required parameter, it is needed to select the resource to delete.

| Option                         | Args      | Description                                                 | Repeatable | Example         |
|--------------------------------|-----------|-------------------------------------------------------------|------------|-----------------|
| **[ REQUIRED ]** `-pk`, `-PK`, | `int`     | **[ REQUIRED ]** Select a specific contract based on its ID | No         | `-pk 3`         |


## Events

### create
```bash 
eecrm event create [OPTIONS] 
```
Create a new event. Start a prompt to ask for missing fields.

| Option               | Args      | Description                                                           | Repeatable | Example             |
|----------------------|-----------|-----------------------------------------------------------------------|------------|---------------------|
| `-d`, `--data-event` | `str str` | Data given to fill in the fields of the new event                     | Yes        | `-d ti "Tea party"` |
| `-np`, `--no-prompt` | `None`    | Block the prompt used to complete missing information about the event | No         | `-np`               |

#### --- Keywords for options using fields
* title, ti
* start_time, st, "start time"
* end_time, et, "end time"
* location, lo
* attendee, at
* notes, no
* contract_id, co, ci, contract, "contract id"

### read
```bash 
eecrm event read [OPTIONS] 
```
Display a list of events or a specific one using its unique ID with the -pk option.

| Option                   | Args      | Description                                | Repeatable | Example             |
|--------------------------|-----------|--------------------------------------------|------------|---------------------|
| `-pk`, `-PK`,            | `int`     | Display a specific event based on its ID   | No         | `-pk 3`             |
| `-f`, `--filter`         | `str str` | Filter with one or more field              | Yes        | `-f ti "Tea party"` |
| `-s`, `--sort`           | `str`     | Sort by one or more field                  | Yes        | `-s at`             |
| `-rc`, `--remove-column` | `str`     | Remove one or more columns from the result | Yes        | `-rc ca`            |

#### --- Keywords for options using fields
* id
* title, ti
* start_time, st, "start time"
* end_time, et, "end time"
* location, lo
* attendee, at
* notes, no
* supporter_id, su, si, supporter, "supporter id", support_id, "support id"
* contract_id, co, ci, contract, "contract id"

### update
```bash 
eecrm event update [OPTIONS] 
```
Update an event data fields. Start a prompt to ask for data field. The ``-pk`` "option" is really a required parameter, it is needed to select the resource to update.

| Option                         | Args      | Description                                                           | Repeatable | Example             |
|--------------------------------|-----------|-----------------------------------------------------------------------|------------|---------------------|
| **[ REQUIRED ]** `-pk`, `-PK`, | `int`     | **[ REQUIRED ]** Select a specific event based on its ID              | No         | `-pk 3`             |
| `-d`, `--data-event`           | `str str` | Data given to fill in the fields of the new event                     | Yes        | `-d ti "Tea party"` |
| `-np`, `--no-prompt`           | `None`    | Block the prompt used to complete missing information about the event | No         | `-np`               |

#### --- Keywords for options using fields
* title, ti
* start_time, st, "start time"
* end_time, et, "end time"
* location, lo
* attendee, at
* notes, no

### delete
```bash 
eecrm event delete [OPTIONS] 
```
Delete an event. The ``-pk`` "option" is really a required parameter, it is needed to select the resource to delete.

| Option                         | Args      | Description                                              | Repeatable | Example         |
|--------------------------------|-----------|----------------------------------------------------------|------------|-----------------|
| **[ REQUIRED ]** `-pk`, `-PK`, | `int`     | **[ REQUIRED ]** Select a specific event based on its ID | No         | `-pk 3`         |
