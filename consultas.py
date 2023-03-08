# Libraries
import streamlit as st
import pandas as pd
import mysql.connector

# Data Sources
def get_data(query, date_init='CURDATE()', date_end='CURDATE()', host='10.0.2.1', user='jonas.salas', password='camaleon', database='hptal'):
    if query == 'estadisticas de ventas':
        sql_query = f'''SELECT
                            facturas_dat.fecha AS Fecha,
                            productos.tipoproducto AS Area,
                            COUNT(DISTINCT(facturas_dat.documento)) AS Clientes,
                            ROUND(SUM(facturas_dat.cantidad - devolucion)) AS 'Unidades Vendidas',
                            CONCAT(ROUND((((SUM(facturas_dat.cantidad - facturas_dat.devolucion))*100)/t3.cantidad), 2), '%') 'pUnidades',
                            ROUND(SUM(totalmasiva), 2) AS 'Ventas Bs',
                            ROUND(SUM(totalmasiva / tasa_primera_actualizacion), 2) AS 'Ventas $',
                            CONCAT(ROUND((((SUM(facturas_dat.totalmasiva))*100)/t2.ventas), 2), '%') 'pVentas',  
                            ROUND(SUM(totalmasiva / t1.cliente), 2) AS 'Ticket Promedio',
                            ROUND(SUM((facturas_dat.cantidad - devolucion) / t1.cliente), 2) AS UPT
                        FROM
                            facturas_dat,
                            productos,
                            facturas,
                            historial_dolar,
                            (SELECT facturas_dat.fecha, 
                                COUNT(DISTINCT(facturas_dat.documento)) AS cliente
                            FROM facturas_dat, 
                                facturas
                            WHERE facturas_dat.fecha BETWEEN '{date_init}' AND '{date_end}' 
                                AND facturas.documento = facturas_dat.documento 
                                AND facturas.credito = 0 
                            GROUP BY facturas_dat.fecha) AS t1,
                            (SELECT facturas_dat.fecha, 
                                SUM(facturas_dat.totalmasiva) AS ventas
                            FROM productos, 
                                facturas, 
                                facturas_dat 
                            WHERE facturas.documento = facturas_dat.documento 
                                AND facturas.credito = 0 
                                AND productos.codprod = facturas_dat.codprod 
                                AND (facturas_dat.fecha BETWEEN '{date_init}' AND '{date_end}') 
                                AND productos.codprod NOT IN(969437, 967836,928905,939572,940627,939573,939574,940769,948544,956358,963444,963440,963532,960510,963442,963620,963438,963616,963619,963617,963618,963437,963744,963434,963445,963446,963448,963950,963961,963963,963964,963965,964211,964456,964216,964504,964503,964217,964322,956262,960258,962082,962287,963321,963322,963869,964102,964112,964223,964229,964301,964303,964342,964356,963737,963615,963951,963962,964207,964740,964990,965099,965100,946779,963737,964558,965618,965620,965758) 
                            GROUP BY facturas_dat.fecha) AS t2,
                            (SELECT facturas_dat.fecha, 
                                SUM(facturas_dat.cantidad - facturas_dat.devolucion) AS cantidad 
                            FROM productos, 
                                facturas, 
                                facturas_dat 
                            WHERE facturas.documento = facturas_dat.documento 
                                AND facturas.credito = 0 
                                AND productos.codprod = facturas_dat.codprod 
                                AND (facturas_dat.fecha BETWEEN '{date_init}' AND '{date_end}') 
                                AND productos.codprod NOT IN(969437,928905, 967836,939572,940627,939573,939574,940769,948544,956358,963444,963440,963532,960510,963442,963620,963438,963616,963619,963617,963618,963437,963744,963434,963445,963446,963448,963950,963961,963963,963964,963965,964211,964456,964216,964504,964503,964217,964322,956262,960258,962082,962287,963321,963322,963869,964102,964112,964223,964229,964301,964303,964342,964356,963737,963615,963951,963962,964207,964740,964990,965099,965100,946779,963737,964558,965618,965620,965758) 
                            GROUP BY facturas_dat.fecha) AS t3
                        WHERE productos.codprod = facturas_dat.codprod
                            AND facturas_dat.fecha BETWEEN '{date_init}' AND '{date_end}'
                            AND facturas_dat.fecha = t1.fecha
                            AND facturas_dat.fecha = t2.fecha
                            AND facturas_dat.fecha = t3.fecha
                            AND facturas_dat.fecha = historial_dolar.fecha
                            AND facturas_dat.documento = facturas.documento
                            AND facturas.credito = 0
                            AND productos.codprod NOT IN(969437, 967836,928905,939572,940627,939573,939574,940769,948544,956358,963444,963440,963532,960510,963442,963620,963438,963616,963619,963617,963618,963437,963744,963434,963445,963446,963448,963950,963961,963963,963964,963965,964211,964456,964216,964504,964503,964217,964322,956262,960258,962082,962287,963321,963322,963869,964102,964112,964223,964229,964301,964303,964342,964356,963737,963615,963951,963962,964207,964740,964990,965099,965100,946779,963737,964558,965618,965620,965758)
                        GROUP BY facturas_dat.fecha, productos.tipoproducto'''
        return transform_query_to_pd_df(sql_query, host, user, password, database)
    
    elif query == 'estadisticas de compras':
        sql_query = f'''SELECT
                            compras.cierre AS Fecha,
                            productos.tipoproducto AS Area,
                            ROUND(SUM(compras.cantidad - compras.devolucion)) AS 'Unidades Ingresadas',
                            CONCAT(ROUND((((SUM(compras.cantidad - compras.devolucion))*100)/s2.tUnidadesIngresadas),2),'%') 'pUnidades',
                            ROUND((SUM(compras.exento+compras.baseimp+compras.montoiva)),2) 'Costo Totales',
                            CONCAT(ROUND((((SUM(compras.exento+compras.baseimp+compras.montoiva))*100)/s3.tCompras),2),'%') 'pCompras',
                            AVG(tasa_primera_actualizacion) AS 'Tasa Promedio',
                            ROUND((SUM(compras.exento+compras.baseimp+compras.montoiva))/tasa_promedio, 2) AS 'Costo Totales $'
                        FROM 
                            compras,
                            productos,
                            historial_dolar,
                            (SELECT compras.cierre AS fecha, SUM(cantidad-devolucion) tUnidadesIngresadas FROM compras WHERE (cierre BETWEEN '{date_init}' AND '{date_end}') AND codprod NOT IN(0, 969437,928905, 967836,939572,940627,939573,939574,940769,948544,956358,963444,963440,963532,960510,963442,963620,963438,963616,963619,963617,963618,963437,963744,963434,963445,963446,963448,963950,963961,963963,963964,963965,964211,964456,964216,964504,964503,964217,964322,956262,960258,962082,962287,963321,963322,963869,964102,964112,964223,964229,964301,964303,964342,964356,963737,963615,963951,963962,964207,964740,964990,965099,965100,946779,963737,964558,965618,965620,965758) GROUP BY compras.cierre) s2,
                            (SELECT compras.cierre AS fecha, codtipoproducto, SUM(exento+baseimp+montoiva) tCompras FROM compras WHERE (cierre BETWEEN '{date_init}' AND '{date_end}') AND codprod NOT IN(0, 969437,928905, 967836,939572,940627,939573,939574,940769,948544,956358,963444,963440,963532,960510,963442,963620,963438,963616,963619,963617,963618,963437,963744,963434,963445,963446,963448,963950,963961,963963,963964,963965,964211,964456,964216,964504,964503,964217,964322,956262,960258,962082,962287,963321,963322,963869,964102,964112,964223,964229,964301,964303,964342,964356,963737,963615,963951,963962,964207,964740,964990,965099,965100,946779,963737,964558,965618,965620,965758) GROUP BY compras.cierre) s3
                        WHERE
                            compras.codprod = productos.codprod
                            AND s2.fecha = compras.cierre
                            AND s3.fecha = compras.cierre
                            AND compras.fecha = historial_dolar.fecha
                            AND productos.codprod NOT IN(969437,928905, 967836,939572,940627,939573,939574,940769,948544,956358,963444,963440,963532,960510,963442,963620,963438,963616,963619,963617,963618,963437,963744,963434,963445,963446,963448,963950,963961,963963,963964,963965,964211,964456,964216,964504,964503,964217,964322,956262,960258,962082,962287,963321,963322,963869,964102,964112,964223,964229,964301,964303,964342,964356,963737,963615,963951,963962,964207,964740,964990,965099,965100,946779,963737,964558,965618,965620,965758) 
                            AND compras.codprod <> 0
                        GROUP BY compras.cierre, compras.codtipoproducto'''
        return transform_query_to_pd_df(sql_query, host, user, password, database)

    elif query == 'estadisticas por areas':
        sql_query = f'''SELECT
                            facturas_dat.fecha AS Fecha,
                            COUNT(DISTINCT(facturas_dat.documento)) AS Clientes,
                            ROUND(SUM(facturas_dat.cantidad - devolucion)) AS 'Unidades',
                            ROUND(SUM(totalmasiva), 2) AS 'Ventas Bs',
                            ROUND(SUM(totalmasiva / tasa_primera_actualizacion), 2) AS 'Ventas $',
                            ROUND(SUM(totalmasiva / t1.cliente), 2) AS 'Ticket Promedio',
                            ROUND(SUM((facturas_dat.cantidad - devolucion) / t1.cliente), 2) AS UPT,
                            t1.areas As Areas
                        FROM
                            facturas_dat,
                            historial_dolar,
                            productos,
                            facturas,
                            (SELECT facturas_dat.fecha, COUNT(DISTINCT(facturas_dat.documento)) AS cliente, CASE WHEN facturas_dat.equipo IN ('Atencion-Preferencia', 'CAJA1-PC', 'CAJA_0102', 'CAJA_03', 'CAJA_07', 'CAJA_08', 'CAJA_09', 'CAJA_10') THEN 'AREA INTERNA' WHEN facturas_dat.equipo IN ('FH-TAQ-01', 'FH-TAQ-02', 'FH-TAQ-03', 'FH-TAQ-04') THEN 'TAQUILLA EXPRESS' WHEN facturas_dat.equipo IN ('MTAQ-01', 'MTAQ-02', 'MTAQ-03', 'MTAQ-04') THEN 'MOTO TAQUILLAS' ELSE 'OTROS' END AS areas, SUM(totalmasiva) AS ventas FROM facturas_dat, facturas WHERE (facturas_dat.fecha BETWEEN '{date_init}' AND '{date_end}') AND facturas.documento = facturas_dat.documento AND facturas.credito = 0 GROUP BY facturas_dat.fecha, CASE WHEN facturas_dat.equipo IN ('Atencion-Preferencia', 'CAJA1-PC', 'CAJA_0102', 'CAJA_03', 'CAJA_07', 'CAJA_08', 'CAJA_09', 'CAJA_10') THEN 'AREA INTERNA' WHEN facturas_dat.equipo IN ('FH-TAQ-01', 'FH-TAQ-02', 'FH-TAQ-03', 'FH-TAQ-04') THEN 'TAQUILLA EXPRESS' WHEN facturas_dat.equipo IN ('MTAQ-01', 'MTAQ-02', 'MTAQ-03', 'MTAQ-04') THEN 'MOTO TAQUILLAS' ELSE 'OTROS' END) AS t1
                        WHERE facturas_dat.fecha = historial_dolar.fecha
                            AND productos.codprod = facturas_dat.codprod
                            AND facturas_dat.fecha = t1.fecha
                            AND CASE WHEN facturas_dat.equipo IN ('Atencion-Preferencia', 'CAJA1-PC', 'CAJA_0102', 'CAJA_03', 'CAJA_07', 'CAJA_08', 'CAJA_09', 'CAJA_10') THEN 'AREA INTERNA' WHEN facturas_dat.equipo IN ('FH-TAQ-01', 'FH-TAQ-02', 'FH-TAQ-03', 'FH-TAQ-04') THEN 'TAQUILLA EXPRESS' WHEN facturas_dat.equipo IN ('MTAQ-01', 'MTAQ-02', 'MTAQ-03', 'MTAQ-04') THEN 'MOTO TAQUILLAS' ELSE 'OTROS' END = t1.areas
                            AND facturas_dat.documento = facturas.documento
                            AND facturas.credito = 0
                            AND productos.codprod NOT IN(969437, 967836,928905,939572,940627,939573,939574,940769,948544,956358,963444,963440,963532,960510,963442,963620,963438,963616,963619,963617,963618,963437,963744,963434,963445,963446,963448,963950,963961,963963,963964,963965,964211,964456,964216,964504,964503,964217,964322,956262,960258,962082,962287,963321,963322,963869,964102,964112,964223,964229,964301,964303,964342,964356,963737,963615,963951,963962,964207,964740,964990,965099,965100,946779,963737,964558,965618,965620,965758)
                        GROUP BY facturas_dat.fecha, t1.areas'''
        return transform_query_to_pd_df(sql_query, host, user, password, database)
    
    elif query == 'estadisticas por lineas':
        sql_query = f'''SELECT
                            facturas_dat.fecha AS Fecha,
                            ROUND(SUM(cantidad)) AS Unidades,
                            ROUND(SUM(totalmasiva), 2) AS 'Ventas Bs',
                            ROUND(SUM(totalmasiva)/tasa_primera_actualizacion, 2) AS 'Ventas $',
                            Linea
                        FROM
                            facturas_dat,
                            historial_dolar
                        WHERE facturas_dat.fecha BETWEEN '{date_init}' AND '{date_end}'
                            AND facturas_dat.fecha = historial_dolar.fecha
                            AND codprod NOT IN(969437, 967836,928905,939572,940627,939573,939574,940769,948544,956358,963444,963440,963532,960510,963442,963620,963438,963616,963619,963617,963618,963437,963744,963434,963445,963446,963448,963950,963961,963963,963964,963965,964211,964456,964216,964504,964503,964217,964322,956262,960258,962082,962287,963321,963322,963869,964102,964112,964223,964229,964301,964303,964342,964356,963737,963615,963951,963962,964207,964740,964990,965099,965100,946779,963737,964558,965618,965620,965758)
                        GROUP BY facturas_dat.fecha, linea'''
        return transform_query_to_pd_df(sql_query, host, user, password, database)
    
    elif query == 'estadisticas de devoluciones tipo':
        sql_query = f'''SELECT
                            facturas_dat.fecha AS Fecha,
                            ROUND(SUM(devolucion)) AS 'Unidades Devueltas',
                            IF(SUM(devolucion) > 0, ROUND(SUM(CASE WHEN poriva > 0 THEN devolucion*facturas_dat.precio*1.16 ELSE 0 END) +  SUM(CASE WHEN poriva = 0 THEN devolucion*facturas_dat.precio ELSE 0 END), 2), 0) AS 'Monto Devolucion Bs',
                            IF(SUM(devolucion) > 0, ROUND(SUM(CASE WHEN poriva > 0 THEN (devolucion*facturas_dat.precio*1.16)/tasa_primera_actualizacion ELSE 0 END) +  SUM(CASE WHEN poriva = 0 THEN (devolucion*facturas_dat.precio)/tasa_primera_actualizacion ELSE 0 END), 2), 0) AS 'Monto Devolucion $',
                            productos.tipoproducto AS Areas
                        FROM
                            facturas_dat,
                            productos,
                            historial_dolar
                        WHERE facturas_dat.fecha BETWEEN '{date_init}' AND '{date_end}'
                            AND productos.codprod = facturas_dat.codprod
                            AND historial_dolar.fecha = facturas_dat.fecha
                        GROUP BY facturas_dat.fecha, productos.tipoproducto'''
        return transform_query_to_pd_df(sql_query, host, user, password, database)

    elif query == 'estadisticas de devoluciones areas':
        sql_query = f'''SELECT
                            facturas_dat.fecha AS Fecha,
                            ROUND(SUM(devolucion)) AS 'Unidades Devueltas',
                            IF(SUM(devolucion) > 0, ROUND(SUM(CASE WHEN poriva > 0 THEN devolucion*precio*1.16 ELSE 0 END) +  SUM(CASE WHEN poriva = 0 THEN devolucion*precio ELSE 0 END), 2), 0) AS 'Monto Devolucion Bs',
                            IF(SUM(devolucion) > 0, ROUND(SUM(CASE WHEN poriva>0 THEN (devolucion*precio*1.16)/tasa_primera_actualizacion ELSE 0 END) +  SUM(CASE WHEN poriva = 0 THEN (devolucion*precio)/tasa_primera_actualizacion ELSE 0 END), 2), 0) AS 'Monto Devolucion $',
                            CASE 
                                WHEN facturas_dat.equipo IN ('Atencion-Preferencia', 'CAJA1-PC', 'CAJA_0102', 'CAJA_03', 'CAJA_07', 'CAJA_08', 'CAJA_09', 'CAJA_10') THEN 'AREA INTERNA' 
                                WHEN facturas_dat.equipo IN ('FH-TAQ-01', 'FH-TAQ-02', 'FH-TAQ-03', 'FH-TAQ-04') THEN 'TAQUILLA EXPRESS' 
                                WHEN facturas_dat.equipo IN ('MTAQ-01', 'MTAQ-02', 'MTAQ-03', 'MTAQ-04') THEN 'MOTO TAQUILLAS' ELSE 'OTROS' END AS Areas
                        FROM
                            facturas_dat,
                            historial_dolar
                        WHERE facturas_dat.fecha BETWEEN '{date_init}' AND '{date_end}'
                            AND facturas_dat.fecha = historial_dolar.fecha
                        GROUP BY facturas_dat.fecha, 
                            CASE WHEN facturas_dat.equipo IN ('Atencion-Preferencia', 'CAJA1-PC', 'CAJA_0102', 'CAJA_03', 'CAJA_07', 'CAJA_08', 'CAJA_09', 'CAJA_10') THEN 'AREA INTERNA' 
                                WHEN facturas_dat.equipo IN ('FH-TAQ-01', 'FH-TAQ-02', 'FH-TAQ-03', 'FH-TAQ-04') THEN 'TAQUILLA EXPRESS' 
                                WHEN facturas_dat.equipo IN ('MTAQ-01', 'MTAQ-02', 'MTAQ-03', 'MTAQ-04') THEN 'MOTO TAQUILLAS' ELSE 'OTROS' END'''
        return transform_query_to_pd_df(sql_query, host, user, password, database)
    
    elif query == 'estadisticas de devoluciones lineas':
        sql_query = f'''SELECT
                            facturas_dat.fecha AS Fecha,
                            ROUND(SUM(devolucion)) AS 'Unidades Devueltas',
                            IF(SUM(devolucion) > 0, ROUND(SUM(CASE WHEN poriva > 0 THEN devolucion*precio*1.16 ELSE 0 END) +  SUM(CASE WHEN poriva = 0 THEN devolucion*precio ELSE 0 END), 2), 0) AS 'Monto Devolucion Bs',
                            IF(SUM(devolucion) > 0, ROUND(SUM(CASE WHEN poriva>0 THEN (devolucion*precio*1.16)/tasa_primera_actualizacion ELSE 0 END) +  SUM(CASE WHEN poriva = 0 THEN (devolucion*precio)/tasa_primera_actualizacion ELSE 0 END), 2), 0) AS 'Monto Devolucion $',
                            Linea
                        FROM
                            facturas_dat,
                            historial_dolar
                        WHERE facturas_dat.fecha BETWEEN '{date_init}' AND '{date_end}' 
                            AND facturas_dat.fecha = historial_dolar.fecha
                        GROUP BY facturas_dat.fecha, linea'''
        return transform_query_to_pd_df(sql_query, host, user, password, database)
    
    elif query == 'estadisticas productos con mayor utilidad':
        sql_query = f'''SELECT
                            compras.codprod AS Codigo,
                            productos.nombre AS Producto,
                            productos.tipoproducto AS Tipo,
                            ROUND(productos.stock) AS Stock,
                            ROUND(f1.cant) AS 'Cantidad Vendida',
                            ROUND(compras.costo,2) AS 'Costo Ingreso',
                            ROUND(((productos.precio - compras.costo)/compras.costo)*100,2) AS 'Util Ultimo Ingreso',
                            ROUND(productos.costo,2) AS 'Costo Actual',
                            ROUND(((productos.precio - productos.costo)/productos.costo)*100,2) AS 'Util Costo Actual'    
                        FROM
                            compras,
                            productos,
                            (SELECT MAX(keycodigo) keycodigo, codprod FROM compras GROUP BY codprod) s1,
                            (SELECT s2.codprod, SUM(s2.cant) cant FROM (SELECT facturas_dat.fecha fecha, facturas_dat.codprod codprod, SUM(facturas_dat.cantidad - facturas_dat.devolucion) cant FROM facturas_dat, productos WHERE facturas_dat.codprod = productos.codprod AND facturas_dat.fecha >= '2022-09-01' AND facturas_dat.fecha < CURDATE() GROUP BY facturas_dat.fecha, facturas_dat.codprod) AS s2 GROUP BY s2.codprod) AS f1
                        WHERE
                            compras.keycodigo = s1.keycodigo
                            AND productos.codprod = compras.codprod    
                            AND f1.codprod = productos.codprod
                            AND compras.cierre >= '2022-09-01'
                            AND compras.cierre < CURDATE()
                            AND productos.desactivar = 0'''
        return transform_query_to_pd_df(sql_query, host, user, password, database)
    
    elif query == 'estadisticas productos mas vendidos':
        sql_query = f'''SELECT
                            productos.codprod AS Codigo,
                            productos.nombre AS Producto,
                            productos.tipoproducto AS 'Area',
                            ROUND(productos.stock) AS Stock,
                            ROUND(SUM(facturas_dat.cantidad - facturas_dat.devolucion)) AS 'Unidades Vendidas',
                            CASE
                                WHEN facturas_dat.poriva > 0 THEN facturas_dat.precio*1.16
                                WHEN facturas_dat.poriva <=0 THEN facturas_dat.precio
                                ELSE 0
                            END AS 'Precio Unitario Bs',
                            ROUND(SUM(facturas_dat.totalmasiva), 2) AS 'Ventas Totales Bs'
                        FROM
                            facturas_dat,
                            productos
                        WHERE
                            facturas_dat.codprod = productos.codprod
                            AND (facturas_dat.fecha BETWEEN '{date_init}' AND '{date_end}')
                            AND productos.codprod NOT IN(970199, 12073, 970200, 964342, 967837, 967954, 966749, 967836, 972997, 967954, 973040, 972213, 973065, 972726, 969437, 958192)
                        GROUP BY facturas_dat.codprod, productos.codtipoproducto'''
        return transform_query_to_pd_df(sql_query, host, user, password, database)

    elif query == 'estadisticas de asesor':
        sql_query = f'''SELECT
                            facturas_dat.fecha AS Fecha,
                            COUNT(DISTINCT(facturas_dat.documento)) AS Clientes,
                            ROUND(SUM(facturas_dat.cantidad - devolucion)) AS 'Unidades',
                            ROUND(SUM(totalmasiva), 2) AS 'Ventas Bs',
                            ROUND(SUM(totalmasiva / tasa_primera_actualizacion), 2) AS 'Ventas $',
                            ROUND(SUM(totalmasiva / t1.cliente), 2) AS 'Ticket Promedio',
                            ROUND(SUM((facturas_dat.cantidad - devolucion) / t1.cliente), 2) AS UPT,
                            t1.usuario AS Usuario
                        FROM
                            facturas_dat,
                            historial_dolar,
                            productos,
                            facturas,
                            (SELECT facturas_dat.fecha, COUNT(DISTINCT(facturas_dat.documento)) AS cliente, facturas_dat.usuario, SUM(totalmasiva) AS ventas FROM facturas_dat, facturas WHERE (facturas_dat.fecha BETWEEN '{date_init}' AND '{date_end}') AND facturas.documento = facturas_dat.documento AND facturas.credito = 0 GROUP BY facturas_dat.fecha, facturas_dat.usuario) AS t1
                        WHERE facturas_dat.fecha = historial_dolar.fecha
                            AND productos.codprod = facturas_dat.codprod
                            AND facturas_dat.fecha = t1.fecha
                            AND facturas_dat.usuario = t1.usuario
                            AND facturas_dat.documento = facturas.documento
                            AND facturas.credito = 0
                            AND productos.codprod NOT IN(969437, 967836,928905,939572,940627,939573,939574,940769,948544,956358,963444,963440,963532,960510,963442,963620,963438,963616,963619,963617,963618,963437,963744,963434,963445,963446,963448,963950,963961,963963,963964,963965,964211,964456,964216,964504,964503,964217,964322,956262,960258,962082,962287,963321,963322,963869,964102,964112,964223,964229,964301,964303,964342,964356,963737,963615,963951,963962,964207,964740,964990,965099,965100,946779,963737,964558,965618,965620,965758)
                        GROUP BY facturas_dat.fecha, t1.usuario'''
        return transform_query_to_pd_df(sql_query, host, user, password, database)
    
    elif query == 'estadisticas de devoluciones asesores':
        sql_query = f'''SELECT
                            facturas_dat.fecha AS Fecha,
                            ROUND(SUM(devolucion)) AS 'Unidades Devueltas',
                            IF(SUM(devolucion) > 0, ROUND(SUM(CASE WHEN poriva > 0 THEN devolucion*precio*1.16 ELSE 0 END) +  SUM(CASE WHEN poriva = 0 THEN devolucion*precio ELSE 0 END), 2), 0) AS 'Monto Devolucion Bs',
                            IF(SUM(devolucion) > 0, ROUND(SUM(CASE WHEN poriva > 0 THEN (devolucion*precio*1.16)/tasa_primera_actualizacion ELSE 0 END) +  SUM(CASE WHEN poriva = 0 THEN (devolucion*precio)/tasa_primera_actualizacion ELSE 0 END), 2), 0) AS 'Monto Devolucion $',
                            facturas_dat.usuario AS Usuario
                        FROM
                            facturas_dat,
                            facturas,
                            historial_dolar
                        WHERE facturas_dat.fecha BETWEEN '{date_init}' AND '{date_end}'
                            AND facturas_dat.fecha = historial_dolar.fecha
                            AND facturas_dat.documento = facturas.documento
                            AND facturas.credito = 0
                        GROUP BY facturas_dat.fecha, facturas_dat.usuario'''
        return transform_query_to_pd_df(sql_query, host, user, password, database)
    
    elif query == 'estadisticas de maquinas fiscales':
        sql_query = f'''SELECT
                            Fecha,
                            SUM(CASE WHEN fiscalserial = 'NENTREGA' THEN 0 ELSE (debitos-creditos) END) AS 'Maquina Fiscal',
                            SUM(CASE WHEN fiscalserial = 'NENTREGA' THEN (debitos-creditos) ELSE 0 END) AS Tickera
                        FROM
                            facturas
                        WHERE fecha BETWEEN '2023-02-15' AND '2023-03-08'
                            AND credito = 0
                        GROUP BY fecha'''
        return transform_query_to_pd_df(sql_query, host, user, password, database)
    
    elif query == 'estadisticas monto real divisas':
        sql_query = f'''SELECT 
                            Fecha, 
                            SUM(monto_moneda) AS 'Monto Divisa'
                            FROM mov_pagos 
                        WHERE fecha BETWEEN '{date_init}' AND '{date_end}' 
                        AND tipo = 'EFECTIVO' 
                        AND codtipomoneda = 3 
                        GROUP BY fecha'''
        return transform_query_to_pd_df(sql_query, host, user, password, database)

    elif query == 'Usuarios':
        sql_query = f'''SELECT 
                            nombre
                        FROM 
                            usuarios 
                        WHERE 
                            is_activo = 1'''
        return transform_query_to_pd_df(sql_query, host, user, password, database)

    elif query == 'Conexiones':
        sql_query = f'''SELECT 
                            SUBSTRING_INDEX(nombre, ',', 1) AS nombre, grupo, servidor, puerto, nomusua, clave, nom_corto, basedata
                        FROM 
                            farmacias'''
        return transform_query_to_pd_df(sql_query, host, user, password, database)
    
    return None

def autentificador(password):
    conn, cursor = get_connection(host='10.0.2.1', user='jonas.salas', password='camaleon', database='hptal')
    if cursor:
        try:
            cursor.execute(f"SELECT nombre FROM usuarios WHERE clave = '{password.upper()}' AND is_nivel_cuadre = 11")
            user = cursor.fetchone()
            if user:
                user = user[0]
            else:
                user = None
        finally:
            conn.close()
        
        if user:
            return user
    return False

def transform_query_to_pd_df(sql_query, host, user, password, database):
    conn, cursor = get_connection(host=host, user=user, password=password, database=database)
    if cursor:
        try:
            cursor.execute(sql_query)
            data = cursor.fetchall()
        finally:
            conn.close()
        
        if data:
            results = list()
            columns = list()
            for col in cursor.description:
                columns.append(col[0])
            results.append(columns)
            for row in data:
                results.append(row)
            
            df = pd.DataFrame(data=data, columns=columns)

            return df
        return None
    else:
        raise Exception('Conexion Fallida')

def get_connection(host, user, password, database):
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        cursor = conn.cursor()
        return conn, cursor
    except:
        raise Exception('Conexion Fallida')