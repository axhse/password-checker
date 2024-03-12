## About

The package implements dev-ops command line programs.

## Programs

Make sure the venv is activated.

An example of the activation from the command line (may differ in your case):
```commandline
source venv/Scripts/activate
```

To get detailed argument descriptions for the programs run them with flag `-h` or `--help`.

### update_storage

Updates the storage.  

Usage:
```commandline
py -m devops.update_storage "/tmp/pwned-storage" "password-checker" -c 64 -m -f 65536 -b 4
```
In this example:
1. Storage resources will be located in ***/tmp/pwned-storage***
2. 64 coroutines will be used for revision
3. The mocked requester will be used
4. The binary implementation of storage will be used
5. Password leak data will be stored in 65536 files
6. Leak occasions will be stored as 4-byte (integer) unsigned numbers
