## About

The package contains dev-ops-related entities.

## Console programs

Make sure the venv is activated before running any program.

An example of the activation from the command line (may differ in your case):
```commandline
source venv/Scripts/activate
```

To get argument descriptions of any program run it with flag `-h` or `--help`.

### update_storage

Updates the storage.  

Usage:
```commandline
py -m devops.update_storage "/tmp/pwned-storage" "password-checker" -c 64 -f 65536 -b 4
```
In this example:
1. Storage resources will be located in ***/tmp/pwned-storage***
2. User agent for Pwned API is `"password-checker"`
3. 64 coroutines will be used during revision
4. The binary implementation of storage will be used
5. Password leak data will be stored in 65536 files
6. Leak occasions will be stored as 4-byte (integer) unsigned numbers

Important: This program must not be run when specified resource directory is already in use by other program or application.

## Environment variables

It's necessary to define environment variables when starting FastAPI application.  
The best way to do this is to create an .env file and then to specify it via command line argument when starting the application:  
```commandline
uvicorn main:app --reload --env-file devops/.env
```
The format of .env file content is demonstrated in ***example.env***

### Description

| Variable                          | Description                                                |
|-----------------------------------|------------------------------------------------------------|
| HTTPS_ONLY                        | Whether to forbid all unsecure connections                 |
| ADMIN_SESSION_LIFETIME_IN_MINUTES | Lifetime of admin session in minutes                       |
| ADMIN_PASSWORD                    | Password for administration                                |
| STORAGE_RESOURCE_DIR              | Directory to store data                                    |
| STORAGE_USER_AGENT                | User agent header value to be sent to Pwned API            |
| STORAGE_COROUTINES                | Number of coroutines for requesting hashes during revision |
| STORAGE_FILES                     | Number of files to store data                              |
| STORAGE_NUMERIC_BYTES             | Size of stored leak occasion unsigned number in bytes      |
| IS_STORAGE_MOCKED                 | Whether to use a mocked Pwned requester                    |
| IS_STORAGE_TEXT                   | Whether to use a text implementation of storage            |
