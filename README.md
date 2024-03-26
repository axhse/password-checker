## About

The project implements an autonomous password check service based on data provided by [HaveIBeenPwned](https://haveibeenpwned.com/).  
Though, all data is stored by the service, and thus HaveIBeenPwned is needed only during data updates.  
The service performs data update in background fully automatic mode, so no pause or restart is needed.  

This app may be used with web interface or via API.  
Password leak data update may be performed with admin interface or via admin API.  

## Quick start

Create and activate virtual Python environment somehow like this:

```commandline
python -m venv venv
source venv/Scripts/activate
```

Install requirements:

```commandline
pip install -r requirements.txt
```

Create .env file (more info in `devops` package)  

Run the app somehow like this:

```commandline
uvicorn main:app --reload --env-file devops/.env
```

## Implementation details

The data from HaveIBeenPwned is stored with storage implemented in `storage` package (more info there).  
This storage is fully async, as well as the application made with FastAPI.  
