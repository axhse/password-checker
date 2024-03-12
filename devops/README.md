## About

This package contains entities related to dev ops.


## Environment Variables

It is necessary to define environment variables when starting the FastAPI application.

The recommended approach is to create a ***.env*** file and then specify it via a command line argument when starting the application:

```commandline
uvicorn main:app --env-file .env
```

The format of the ***.env*** file content is demonstrated in ***example.env***.

### Description

| Variable                          | Description                                                |
|-----------------------------------|------------------------------------------------------------|
| HTTPS_ONLY                        | Specifies whether to forbid all insecure connections       |
| ADMIN_SESSION_LIFETIME_IN_MINUTES | Lifetime of admin session in minutes                       |
| ADMIN_PASSWORD                    | Password for administration                                |
| STORAGE_RESOURCE_DIR              | Directory to store data                                    |
| STORAGE_USER_AGENT                | User agent header value to be sent to Pwned API            |
| STORAGE_COROUTINES                | Number of coroutines for requesting hashes during revision |
| STORAGE_FILES                     | Number of files to store data                              |
| STORAGE_NUMERIC_BYTES             | Size of stored leak occasion unsigned number in bytes      |
| IS_STORAGE_MOCKED                 | Specifies whether to use a mocked Pwned requester          |
| IS_STORAGE_TEXT                   | Specifies whether to use a text implementation of storage  |


## Deployment With SSL

Ubuntu 22.04 LTS was used for this instruction.

### Set Up Python Project

#### Install Python

```commandline
apt-get update
apt-get install -y python3.10 python3.10-venv

```

#### Clone Project

```commandline
mkdir -p /home/app
cd /home/app

git clone https://github.com/axhse/password-checker

cd password-checker

git pull origin release
git checkout release

```

#### Create Virtual Environment 

```commandline
python3.10 -m venv venv

```

#### Install Requirements

```commandline
source venv/bin/activate
pip install -r requirements.txt

```

#### Configure Application

Create ***.env*** file in project root directory (use ***example.env*** as an example).

### Configure Server

#### Place SSL Files In System

(If necessary)  
A commonly used location for SSL certificate and key files is ***/etc/ssl***.

#### Create Service

Modify one of services ***devops/deploy/http_password_checker.service*** or ***devops/deploy/https_password_checker.service*** if necessary:
1. Specify paths to SSL certificate and key files

Then, copy it to ***/etc/systemd/system/password_checker.service***.

```commandline
cp devops/deploy/http_password_checker.service /etc/systemd/system/password_checker.service

```

```commandline
cp devops/deploy/https_password_checker.service /etc/systemd/system/password_checker.service

```

### Run Server

#### Start Service

```commandline
systemctl daemon-reload
```

```commandline
systemctl restart password_checker

```

#### Stop Service

(When needed)

```commandline
systemctl stop password_checker

```


## Console Programs

Ensure that the virtual environment (venv) is activated before running any program.

To activate the venv from the command line (may vary depending on your system), use the following command:

```commandline
source venv/bin/activate
```

To get descriptions of arguments for any program, run it with the `-h` or `--help` flag.

### update_storage

This program updates the storage.

Usage:

```commandline
py -m devops.update_storage "/home/pwned-storage" "password-checker" -c 64 -f 65536 -b 4
```

In this example:
1. Storage resources will be located in ***/home/pwned-storage***.
2. The user agent for the Pwned API is set to `"password-checker"`.
3. 64 coroutines will be used during revision.
4. The binary implementation of storage will be used.
5. Password leak data will be stored in 65536 files.
6. Leak occasions will be stored as 4-byte (integer) unsigned numbers.

**Important**: Do not use this program if the specified resource directory is already in use by another program or application.
