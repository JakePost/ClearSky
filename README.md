# Clearsky

This program provides information from Bluesky using ATProto.

## Table of contents

- [Installation](#installation)
- [Usage](#usage)
- [Codespaces](#codespaces)
- [Deployment](#deployment)

## Installation

## Usage

## Codespaces:

Modify config.ini to add: 

```
ip = 127.0.0.1

port = 5000 

PG_USER: postgres

PG_DB: clearskyprod

PG_PASSWORD: postgres

use_local = True
```
\
Set up data and deploy application:
```
python setup.py --start-test
```
\
\
Open browser from prompt or open URL from ports menu to navigate to site

Note: db connection not supported yet. Some things will not function properly.

## Deployment