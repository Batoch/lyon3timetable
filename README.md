# lyon3timetable

A Python script exposing lyon 3 university's timetable to an iCAL URL

## Deployment

-------------

### 1. Using Docker

First, build the docker image:

```console
docker build -t lyon3timetable .
```

Then run it:

```console
docker run -d --restart=on-failure --name lyon3timetable -p 5000:5000 -e USERNAME=<YOURUSERNAME eg.358...> -e PASSWORD='<YOURPASSWORD>' lyon3timetable
```

### 2. Using Python Flask

After configuring the two environment variables USERNAME and PASSWORD :

```console
pip install -r requirements.txt
flask run --host 0.0.0.0
```
