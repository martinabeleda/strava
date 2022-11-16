# Terraform

This folder contains terraform manifests for provisioning our infrastructure

## Components

### Elastic Kubernetes Service

Used the [Hashicorp EKS Tutorial](https://developer.hashicorp.com/terraform/tutorials/kubernetes/eks) as a template.

### Relational Database Service

## Deployment

At the moment, infrastructure is deployed manually through the terraform CLI.

First, Initialize:

```shell
terraform init
```

Then plan and check the results:

```shell
terraform plan
```

Now, apply the changes:

```shell
terraform apply
```
