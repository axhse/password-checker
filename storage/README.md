## About

The package implements a file storage for password leak records provided by [HaveIBeenPwned](https://haveibeenpwned.com/).  
There are two implementations available:
1. `TextPwnedStorage` - stores ranges in 1048576 separated by prefix text files
2. `BinaryPwnedStorage` - stores records in optimized by memory binary format

`BinaryPwnedStorage` uses 40-50% less memory compared to `TextPwnedStorage`, but updates about 10-20% slower

## Usage

Binary storage creation:
```python
from storage.models.settings import (
    NumericType,
    BinaryPwnedStorageSettings,
    StorageFileQuantity,
)
from storage.implementations.binary_storage import BinaryPwnedStorage
from storage.implementations.requester import PwnedRequester

requester = PwnedRequester("password-checker")
settings = BinaryPwnedStorageSettings(StorageFileQuantity.N_65536, occasion_numeric_type=NumericType.INTEGER)
storage = BinaryPwnedStorage("/tmp/pwned-storage", requester, 64, settings=settings)
```
In this example:
1. Storage resources will be located in ***/tmp/pwned-storage***
2. User agent for Pwned API is `"password-checker"`
3. 64 coroutines will be used during revision
4. Password leak data will be stored in 65536 files
5. Leak occasions will be stored as 4-byte (integer) unsigned number (potential occasion values more than 4294967295 will be replaced with 4294967295)

Request asynchronous update in background:
```python
response = storage.request_update()
```

Request update cancellation:
```python
response = storage.request_update_cancellation()
```

Update asynchronously:
```python
async def update_storage(storage):
    return await storage.update()
```

Get information of the latest update:
```python
revision = storage.revision
```

Get password leak records:
```python
async def get_records(storage):
    return await storage.get_range("FADED")
```

For testing purposes mocked version of Pwned requester may be used. It returns fictive data but performs requests much faster.

## Package structure

Sub-packages:  
 - **`models`** - contains some common models.
 - **`implementations`** - contains various storage and range provider implementations.
 - **`auxiliary`** - contains only auxiliary components and is considered not to be used directly at all.
