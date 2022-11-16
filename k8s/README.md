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

## Deploy service

Deploy the service and the deployment:

```shell
kubectl apply -f deployment.yaml
```

Now, let's port forward the service and access the docs link:

```shell
kubectl port-forward service/strava 8080:8080
```

