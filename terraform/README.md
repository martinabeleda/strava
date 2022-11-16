# Terraform

This folder contains terraform manifests for provisioning our infrastructure

## Components

### Elastic Kubernetes Service

Used the [Hashicorp EKS Tutorial](https://developer.hashicorp.com/terraform/tutorials/kubernetes/eks) as a template.

Configure `kubectl` with cluster credentials:

```shell
aws eks --region $(terraform output -raw region) update-kubeconfig \
    --name $(terraform output -raw cluster_name)
```

Verify the cluster:

```shell
kubectl cluster-info
```

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

## Destroy resources

Now, let's remove any of the resources we created:

```shell
terraform destroy
```
