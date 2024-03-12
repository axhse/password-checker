## About

The package implements file storage for password leak records provided by [HaveIBeenPwned](https://haveibeenpwned.com/).  
There are two implementations available:

1. `TextPwnedStorage` - stores ranges in files separated by prefix text files (with each file containing ranges within a span of 1048576).
2. `BinaryPwnedStorage` - stores records in an optimized binary format, resulting in 40-50% less memory usage compared to `TextPwnedStorage`, albeit with updates about 10-20% slower.


## Usage In Code

Create a binary storage instance:

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
storage = BinaryPwnedStorage("/home/pwned-storage", requester, 64, settings=settings)
```

In this example:
1. Storage resources will be located in ***/home/pwned-storage***.
2. The user agent for the Pwned API is set to `"password-checker"`.
3. 64 coroutines will be used during revision.
4. Password leak data will be stored in 65536 files.
5. Leak occasions will be stored as 4-byte (integer) unsigned numbers (with potential occasion values greater than 4294967295 being replaced with 4294967295).

Request asynchronous update in the background:

```python
response = storage.request_update()
```

Request update cancellation:

```python
response = storage.request_update_cancellation()
```

Asynchronously update:

```python
async def update_storage(storage):
    return await storage.update()
```

Get information on the latest update:

```python
revision = storage.revision
```

Get password leak records:

```python
async def get_records(storage):
    return await storage.get_range("FADED")
```

For testing purposes, a mocked version of the Pwned requester may be used. It returns fictive data but performs requests much faster.


## Package Structure

Sub-packages:
- **`models`** - contains some common models.
- **`implementations`** - contains various storage and range provider implementations.
- **`auxiliary`** - contains only auxiliary components and is not intended to be used directly.
