# SupportX AI Assist — Terraform Deployment

Simple Terraform script that builds the whole Azure setup for this app:
Resource Group → Container Registry → App Service Plan → Linux Web App (container) → Managed Identity with AcrPull.

## What each file does

| File | Purpose |
|------|---------|
| `main.tf` | The actual resources (RG, ACR, plan, web app, role) |
| `variables.tf` | Declares all the inputs Terraform needs |
| `terraform.tfvars.example` | Template — copy to `terraform.tfvars` and fill in |
| `outputs.tf` | Prints the app URL after apply |
| `.gitignore` | Keeps secrets and state out of git |

## Prerequisites (one-time)

1. Install Terraform: https://developer.hashicorp.com/terraform/install
2. Install Azure CLI: https://learn.microsoft.com/cli/azure/install-azure-cli
3. Log in: `az login`
4. Get your subscription ID: `az account show --query id -o tsv`

## Deploy in 4 commands

```bash
cd terraform

# 1. Copy the example vars file and fill in YOUR values
cp terraform.tfvars.example terraform.tfvars
# then edit terraform.tfvars with your secrets

# 2. Download the Azure provider
terraform init

# 3. See what will be created (no changes yet)
terraform plan

# 4. Create the resources in Azure
terraform apply
# type `yes` when prompted
```

After apply finishes, Terraform prints `app_url` and `acr_login_server`.

## Push your Docker image

Terraform creates the empty ACR. You still need to push the image:

```bash
# Log in to the new ACR (name from outputs)
az acr login --name <acr_name>

# Tag and push
docker tag intelligent-ticket-resolver:latest <acr_login_server>/intelligent-ticket-resolver:latest
docker push <acr_login_server>/intelligent-ticket-resolver:latest

# Restart the web app so it pulls the new image
az webapp restart --name <app_name> --resource-group <resource_group>
```

## Updating

- Change a variable or env var → `terraform apply` again
- Push a new image tag → update `image_tag` in tfvars → `terraform apply`
- Destroy everything → `terraform destroy`
