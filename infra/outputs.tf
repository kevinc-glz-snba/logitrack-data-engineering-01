output "resource_group_name" {
  description = "Nombre del grupo de recursos de LogiTrack."
  value       = azurerm_resource_group.main.name
}

output "datalake_name" {
  description = "Nombre de la cuenta de almacenamiento ADLS Gen2."
  value       = azurerm_storage_account.datalake.name
}

output "bronze_container_name" {
  description = "Nombre del contenedor Bronze."
  value       = azurerm_storage_container.bronze.name
}

output "silver_container_name" {
  description = "Nombre del contenedor Silver."
  value       = azurerm_storage_container.silver.name
}

output "gold_container_name" {
  description = "Nombre del contenedor Gold."
  value       = azurerm_storage_container.gold.name
}

output "data_factory_name" {
  description = "Nombre de Azure Data Factory."
  value       = azurerm_data_factory.main.name
}

output "key_vault_name" {
  description = "Nombre de Azure Key Vault."
  value       = azurerm_key_vault.main.name
}

output "log_analytics_name" {
  description = "Nombre del workspace de Log Analytics."
  value       = azurerm_log_analytics_workspace.main.name
}

output "action_group_name" {
  description = "Nombre del grupo de acciones de Azure Monitor."
  value       = azurerm_monitor_action_group.main.name
}
