# ============================================================
# Variables — values are filled in from terraform.tfvars
# ============================================================

variable "subscription_id" {
  description = "Your Azure subscription ID (run: az account show --query id -o tsv)"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "rg-intelligent-ticket"
}

variable "location" {
  description = "Azure region for the resource group and ACR"
  type        = string
  default     = "eastus"
}

variable "app_location" {
  description = "Azure region for the App Service Plan and Web App"
  type        = string
  default     = "eastasia"
}

variable "user_assigned_identity_name" {
  description = "Name of the User-Assigned Managed Identity used by the Web App"
  type        = string
}

variable "acr_name" {
  description = "Container Registry name (globally unique, lowercase, 5-50 chars)"
  type        = string
}

variable "app_name" {
  description = "Web App name (globally unique)"
  type        = string
}

variable "service_plan_name" {
  description = "App Service Plan name (match existing if importing)"
  type        = string
}

variable "image_name" {
  description = "Docker image name in ACR"
  type        = string
  default     = "intelligent-ticket-resolver"
}

variable "image_tag" {
  description = "Docker image tag"
  type        = string
  default     = "latest"
}

# -------- Azure OpenAI --------
variable "azure_openai_endpoint" {
  type = string
}

variable "azure_openai_api_key" {
  type      = string
  sensitive = true
}

variable "azure_openai_api_version" {
  type    = string
  default = "2024-12-01-preview"
}

variable "azure_openai_deployment" {
  type    = string
  default = "gpt-4o"
}

variable "azure_openai_model" {
  type    = string
  default = "gpt-4o-2024-11-20"
}

variable "azure_openai_embedding_deployment" {
  type    = string
  default = "text-embedding-3-small"
}

# -------- Azure AI Search --------
variable "azure_search_endpoint" {
  type = string
}

variable "azure_search_key" {
  type      = string
  sensitive = true
}

# -------- Email (SMTP) --------
variable "smtp_server" {
  type    = string
  default = "smtp.gmail.com"
}

variable "smtp_port" {
  type    = string
  default = "587"
}

variable "sender_email" {
  type = string
}

variable "sender_password" {
  type      = string
  sensitive = true
}

variable "support_email" {
  type = string
}
