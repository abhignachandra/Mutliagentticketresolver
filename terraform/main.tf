# ============================================================
# SupportX AI Assist — Terraform (simple version)
# Manages: Resource Group -> ACR -> App Service Plan -> Web App
# ============================================================

# 1) Tell Terraform we want to use Azure
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}


# 2) A Resource Group = a folder in Azure that holds everything
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location

  tags = {
    ManagedBy = "Terraform"
    Owner = "abhigna chandra"
  }
}


# 3) Azure Container Registry (ACR) = private Docker Hub
#    We push our Docker image here.
resource "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = false
}


# 4) Reference the existing User-Assigned Managed Identity
#    (a data block READS a resource without taking ownership)
data "azurerm_user_assigned_identity" "webapp_identity" {
  name                = var.user_assigned_identity_name
  resource_group_name = var.resource_group_name
}


# 5) App Service Plan = the "machine" our app runs on (Linux, B1)
resource "azurerm_service_plan" "plan" {
  name                = var.service_plan_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.app_location
  os_type             = "Linux"
  sku_name            = "B1"
}


# 6) The Web App itself — runs our Docker container from ACR
resource "azurerm_linux_web_app" "app" {
  name                = var.app_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = var.app_location
  service_plan_id     = azurerm_service_plan.plan.id
  https_only          = true

  # Keep FTP/WebDeploy basic auth disabled for security
  ftp_publish_basic_authentication_enabled       = false
  webdeploy_publish_basic_authentication_enabled = false

  # Use the existing User-Assigned identity to pull from ACR
  identity {
    type         = "UserAssigned"
    identity_ids = [data.azurerm_user_assigned_identity.webapp_identity.id]
  }

  site_config {
    always_on  = false
    ftps_state = "FtpsOnly"

    container_registry_use_managed_identity       = true
    container_registry_managed_identity_client_id = data.azurerm_user_assigned_identity.webapp_identity.client_id

    application_stack {
      docker_image_name   = "${var.image_name}:${var.image_tag}"
      docker_registry_url = "https://${azurerm_container_registry.acr.login_server}"
    }
  }

  # Environment variables the app reads (same as your .env)
  app_settings = {
    WEBSITES_ENABLE_APP_SERVICE_STORAGE = "false"

    AZURE_OPENAI_ENDPOINT             = var.azure_openai_endpoint
    AZURE_OPENAI_API_KEY              = var.azure_openai_api_key
    AZURE_OPENAI_API_VERSION          = var.azure_openai_api_version
    AZURE_OPENAI_DEPLOYMENT           = var.azure_openai_deployment
    AZURE_OPENAI_MODEL                = var.azure_openai_model
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT = var.azure_openai_embedding_deployment

    AZURE_SEARCH_ENDPOINT = var.azure_search_endpoint
    AZURE_SEARCH_KEY      = var.azure_search_key

    SMTP_SERVER     = var.smtp_server
    SMTP_PORT       = var.smtp_port
    SENDER_EMAIL    = var.sender_email
    SENDER_PASSWORD = var.sender_password
    SUPPORT_EMAIL   = var.support_email
  }
}


# 7) Let the Web App pull images from ACR (AcrPull role on the UAI)
resource "azurerm_role_assignment" "acr_pull" {
  scope                = azurerm_container_registry.acr.id
  role_definition_name = "AcrPull"
  principal_id         = data.azurerm_user_assigned_identity.webapp_identity.principal_id

  # Azure returns the scope in lowercase; ignore this cosmetic drift
  lifecycle {
    ignore_changes = [scope]
  }
}
