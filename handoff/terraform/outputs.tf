# ============================================================
# Outputs — printed after `terraform apply` succeeds
# ============================================================

output "app_url" {
  description = "Public URL of the deployed web app"
  value       = "https://${azurerm_linux_web_app.app.default_hostname}"
}

output "acr_login_server" {
  description = "ACR login server (use this with `docker push`)"
  value       = azurerm_container_registry.acr.login_server
}

output "resource_group" {
  description = "Resource group name"
  value       = azurerm_resource_group.rg.name
}
