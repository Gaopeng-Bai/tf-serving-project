---
    Title: TF-serving on keras regression model
---

## Background

### [Model resources](https://www.tensorflow.org/tutorials/keras/regression)

### Steps to fulfill
- [x] Deploy a trained model in a containerized application(e.g. using TF Server)
- [x] Write a Python application that exposes one or several APIS, which consume and then serve predictions from the served model
   - [x] You can use the Python framework of your choice to build the Apl
   - [x] Your application should be fully tested with unit and integration tests. You can use the test framework of your choice o Your application should be containerized
- [x] To submit
   - [x] Public git repository with deployment instructions
### Bonus
- [x] You provide Kubernetes manifests which would cover the deployment of the entire applications.
- [ ] You write system tests which demonstrate the performance of your application under load

## Project Structure
```bash
|-- docker #directory that contains Dockerfiles to build docker images
|   |-- flask.dockerfile
|   |-- serving.dockerfile
|-- k8s # directory that contains Kubernetes manifests to deploy both tf_serving and flask_server
|   |-- flask_server.yaml
|   |-- tf_serving.yaml
|-- scripts # directory that contains python script to test the result
|   |-- test_with_requests.py
|-- src # project source code
|   |-- flask_server # flask_server source code
|   |   |-- __init__.py
|   |   |-- app.py # flask application main, which defines api
|   |   |-- utils.py # utils that helps to build the application
|   |-- tests # contains test cases for unit tests and integration tests 
|   |   |-- __init__.py
|   |   |-- test_api.py # unit tests
|   |   |-- test_integration.py # integration tests
|   |-- train # training scripts
|       |-- datasets # sample dataset used for prediction
|       |   |-- example_data.csv
|       |-- models # saved_model with model_name and version
|       |   |-- dnn_model
|       |   |   |-- 001
|       |   |-- export_model
|       |       |-- 2
|       |-- Keras_export.py # save model using TF1.x api which is not acceptable
|       |-- export_model.py # save model using TF2.x api
|       |-- regression_model.py # training model
|       |-- requirements.txt
|-- README.md
|-- requirements.txt
```
## Quick start unittest
1. [Run the tf-serving docker containers](#Docker-image-usage)
2. Run flask app to start the server
3. [Run unittest](#For-testing)

## Quick start in Kubernetes
1. [Build the docker containers](#Docker-image-building-instruction)
2. [Apply the k8s pods](#Kubernetes-usage)
3. Run python script to test.
    ```
    python test_with_requests.py
    ```

## Frameworks
### For serving Tensorflow models
I chose the official TensorFlow Serving. https://www.tensorflow.org/tfx/guide/serving

I found that TensorFlow serving will consume the feature data with 
```
POST http://host:port/v1/models/${MODEL_NAME}[/versions/${VERSION}|/labels/${LABEL}]:predict
```

I will use the exposed 8501 http port from the tf_serving image to make predictions.

### For exposing our own API
I chose Flask for building our own application, which consume and then serve predictions from the served model.

In ```src/flask_server/app.py```, I define some basic api for checking healthiness, several error handler, and 
api for predicting from json data and csv file which contains the features.

I set ```TF_SERVER``` as environment variable representing the TensorFlow serving host, default as ```http://127.0.0.1:5000```.

In our application,
I also want model_name from the requests to identify which model to use. If I have only one model, I can certainly
set the model_name in our code for convenience.

### For testing
I chose unittest as our testing framework.

I provide ```src/test/test_api.py``` for basic api test and some error handler tests. 
```bash
python -m unittest src/tests/test_api.py
```

I also provided ```src/test/test_integration.py``` for integrated test with Tensorflow Serving.
Please make sure you have started TensorFlow Serving by executing ```docker run --name="tf_serving" --rm -d -p 8501:8501 tf_serving:1.0```
and then 
```bash
python -m unittest src/tests/test_integration.py
```
After usage, stop the TensorFlow Serving container by executing ```docker stop tf_serving```

For more docker usage instruction, read below.

## Docker image building instruction
I assume executing the following shell scripts from source root, i.e. tf-serving-project.
### TF Serving
```bash
docker build -t tf_serving:1.0 --file ./docker/serving.dockerfile .
```
-t set the image name

--file specify the Dockerfile to use

In ```docker/serving.dockerfile```, I use the official ```tensorflow/serving:2.4.1``` docker image as the base image, 
and then add our exported model to ```/models```. I can then build our own serving docker image: ```tf_serving:1.0```. 

I defined ```src/train/models/models.config``` to tell the serving server which models to serve. If I have more models,
I can rebuild the docker image with the modified config file.

### API server
```bash
docker build -t flask_server:1.0 --file ./docker/flask.dockerfile .
```
I build our own flask docker image from ```python:3.6-slim```, copy the source code, and then installed the required 
python libraries. I call the image ```flask_server:1.0```

## Docker image usage
When using Docker-desktop from MacOS or Windows
```bash
docker run --name="tf_serving" --rm -d -p 8501:8501 tf_serving:1.0
docker run --name="flask_server" --rm -d -p 5000:5000 --env TF_SERVER=http://host.docker.internal:8501 flask_server:1.0
```
When using from Linux docker, I should probably set up a docker network to make the communication betIen two containers work.

Stop the containers by executing
```bash
docker stop tf_serving
docker stop flask_server
```
## Kubernetes usage
I assume executing the following shell scripts from source root, i.e. tf-serving-project.

I provide two manifests representing tf_serving and flask_serving. They both contain a Deployment for 
running the application, and a service for consuming the network visiting.

### Starting
``` bash
kubectl apply -f k8s/tf_serving.yaml
kubectl apply -f k8s/flask_server.yaml
```
I can see something like this
```bash
deployment.apps/tf-serving created
service/tf-serving-service created
deployment.apps/flask-server created
service/flask-server-service created
```

### Verifying
```bash
kubectl get po
```
I can see something like this
```
NAME                            READY   STATUS    RESTARTS   AGE
flask-server-5d69f4bcbf-jh8jm   1/1     Running   0          2m39s
tf-serving-6fd85d75b7-cxfg4     1/1     Running   0          2m39s
```

When the two STATUS both show 'Running', I can use them already. Here are some examples:
```bash
curl --location --request GET 'http://localhost:32000/health'
```
``` bash
curl --location --request POST 'http://localhost:32000/predict' --header 'Content-Type: application/json' --data-raw '{"model_name": "dnn_model", "version": "001", "instances": [[10, 8, 2, 1, 23, 3, 1, 3, 1]]}'
```
```bash
curl --location --request POST 'http://localhost:32000/predict_file' \
--form 'file=@"example_data.csv"' \
--form 'model_name="dnn_model"' \
--form 'version="001"'
```

### Stopping
Every time I start up our kubernetes cluster, the two will always start up themselves. So I should stop them after using.
```bash
kubectl delete -f k8s/tf_serving.yaml
kubectl delete -f k8s/flask_server.yaml
```