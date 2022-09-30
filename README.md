# Careers
Careers Game Editions - game model and engine.

## Development Guide
Running the server locally requires mongodb and a Python Virtual Environment.

Assuming Python 3.9 is installed globally. Create a virtual environment:
```
python -m virtualenv venv
```

This will create a virtual environment called venv. Visual Studio Code (when restarted) will automatically find (and bind all python commands) to this virtual environment:

![Visual Studio Code](docs/venv.PNG)

## Installing Required Packages
Run pip from a command prompt (presumably bound to the new virtual directory)
```
pip install -r requirements.txt
```

## Installing and Running Docker
Docker is used for testing the containerized version of the app. It's also used for running mongodb locally.

```
https://docs.docker.com/desktop/install/windows-install/
```
Once Docker is installed, install the following plugins for Visual Studio Code:
* Docker
* Mongodb

## Running the Containerized Version
It's easy to build the image directly from Visual Studio Code...assuming the Docker plugin is installed. Right-click on the `Dockerfile` and select `Build Image`. It will build the image `careers`, which can be launched from the command line:

```
docker run -it -p 9000:9000 careers
```
This will run the app listening on port 9000. 

## Running Mongodb
Assuming the Docker plugin is installed, right click the `docker-compose.yml` file and choose `Compose Up`.
Once it's running, you can connect to it locally using the Mongodb plugin (by connecting to `localhost`).