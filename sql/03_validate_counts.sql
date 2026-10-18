SELECT 'geo_zonas' AS tabla, COUNT(*) AS registros
FROM geo_zonas

UNION ALL

SELECT 'ope_conductores', COUNT(*)
FROM ope_conductores

UNION ALL

SELECT 'cli_remitentes', COUNT(*)
FROM cli_remitentes

UNION ALL

SELECT 'tms_envios', COUNT(*)
FROM tms_envios

UNION ALL

SELECT 'gps_rutas', COUNT(*)
FROM gps_rutas

UNION ALL

SELECT 'cal_destinatarios', COUNT(*)
FROM cal_destinatarios

UNION ALL

SELECT 'dir_novedades', COUNT(*)
FROM dir_novedades;