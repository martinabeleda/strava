# Kubernetes resources

This folder contains kubernetes resource files for our service

## Create secrets

Create a secret to store dockerhub creds:

```shell
kubectl create secret docker-registry regcred --docker-server=docker.io --docker-username=martinabeleda --docker-password=<DOCKER_PASSWORD>
```

Verify:

```shell
kubectl get secret regcred --output=yaml
```

## Build a new version

For now, I'm building the service locally using:

```shell
docker build -t martinabeleda/strava:v0.0.4 .
```

Push this to dockerhub

```shell
docker push martinabeleda/strava:v0.0.4
```

## Deploy service

Deploy the service and the deployment:

```shell
kubectl apply -f deployment.yaml
```

Now, let's port forward the service and access the docs link:

```shell
kubectl port-forward service/strava 8080:8080
```

## Running migrations

For now, migrations are also manual. First, exec into one of the service pods:

```shell
kubectl exec -it deploy/strava -- bash
```

Then, run the migration from inside the pod:

```shell
$ alembic upgrade head
```
