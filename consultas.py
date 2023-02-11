# Libraries
import streamlit as st
import pandas as pd
import mysql.connector

# Data Sources
# @st.cache(ttl=1000, allow_output_mutation=True)
def get_data(query, date_init=None, date_end=None):
    if query == 'Estadistica de Ventas':
        sql_query = f'''SELECT
                            facturas_dat.fecha,
                            productos.tipoproducto,
                            COUNT(DISTINCT(facturas_dat.documento)) AS clientes,
                            ROUND(SUM(facturas_dat.cantidad - devolucion)) AS unidades_vendidas,
                            CONCAT(ROUND((((SUM(facturas_dat.cantidad - facturas_dat.devolucion))*100)/t3.cantidad), 2), '%') 'pUnidades',
                            ROUND(SUM(totalmasiva), 2) AS ventas_bs,
                            ROUND(SUM(totalmasiva / tasa_primera_actualizacion), 2) AS ventas_dolar,
                            CONCAT(ROUND((((SUM(facturas_dat.totalmasiva))*100)/t2.ventas), 2), '%') 'pVentas',  
                            ROUND(SUM(totalmasiva / t1.cliente), 2) AS ticket_promedio,
                            ROUND(SUM((facturas_dat.cantidad - devolucion) / t1.cliente), 2) AS UPT
                        FROM
                            facturas_dat,
                            historial_dolar,
                            productos,
                            facturas,
                            (SELECT facturas_dat.fecha, COUNT(DISTINCT(facturas_dat.documento)) AS cliente FROM facturas_dat, facturas WHERE facturas_dat.fecha BETWEEN '{date_init}' AND '{date_end}' AND facturas.documento = facturas_dat.documento AND facturas.credito = 0 GROUP BY facturas_dat.fecha) AS t1,
                            (SELECT facturas_dat.fecha, SUM(facturas_dat.totalmasiva) AS ventas FROM productos, facturas, facturas_dat WHERE facturas.documento = facturas_dat.documento AND facturas.credito = 0 AND productos.codprod = facturas_dat.codprod AND (facturas_dat.fecha BETWEEN '{date_init}' AND '{date_end}') AND productos.codprod NOT IN(969437, 967836,928905,939572,940627,939573,939574,940769,948544,956358,963444,963440,963532,960510,963442,963620,963438,963616,963619,963617,963618,963437,963744,963434,963445,963446,963448,963950,963961,963963,963964,963965,964211,964456,964216,964504,964503,964217,964322,956262,960258,962082,962287,963321,963322,963869,964102,964112,964223,964229,964301,964303,964342,964356,963737,963615,963951,963962,964207,964740,964990,965099,965100,946779,963737,964558,965618,965620,965758) GROUP BY facturas_dat.fecha) AS t2,
                            (SELECT facturas_dat.fecha, SUM(facturas_dat.cantidad - facturas_dat.devolucion) AS cantidad FROM productos, facturas, facturas_dat WHERE facturas.documento = facturas_dat.documento AND facturas.credito = 0 AND productos.codprod = facturas_dat.codprod AND (facturas_dat.fecha BETWEEN '{date_init}' AND '{date_end}') AND productos.codprod NOT IN(969437,928905, 967836,939572,940627,939573,939574,940769,948544,956358,963444,963440,963532,960510,963442,963620,963438,963616,963619,963617,963618,963437,963744,963434,963445,963446,963448,963950,963961,963963,963964,963965,964211,964456,964216,964504,964503,964217,964322,956262,960258,962082,962287,963321,963322,963869,964102,964112,964223,964229,964301,964303,964342,964356,963737,963615,963951,963962,964207,964740,964990,965099,965100,946779,963737,964558,965618,965620,965758) GROUP BY facturas_dat.fecha) AS t3
                        WHERE facturas_dat.fecha = historial_dolar.fecha
                            AND productos.codprod = facturas_dat.codprod
                            AND facturas_dat.fecha = t1.fecha
                            AND facturas_dat.fecha = t2.fecha
                            AND facturas_dat.fecha = t3.fecha
                            AND facturas_dat.documento = facturas.documento
                            AND facturas.credito = 0
                            AND productos.codprod NOT IN(969437, 967836,928905,939572,940627,939573,939574,940769,948544,956358,963444,963440,963532,960510,963442,963620,963438,963616,963619,963617,963618,963437,963744,963434,963445,963446,963448,963950,963961,963963,963964,963965,964211,964456,964216,964504,964503,964217,964322,956262,960258,962082,962287,963321,963322,963869,964102,964112,964223,964229,964301,964303,964342,964356,963737,963615,963951,963962,964207,964740,964990,965099,965100,946779,963737,964558,965618,965620,965758)
                        GROUP BY facturas_dat.fecha, productos.tipoproducto'''
        return transform_query_to_pd_df(sql_query)

    elif query == 'Estadisticas por area':
        sql_query = f'''SELECT
                            facturas_dat.fecha,
                            COUNT(DISTINCT(facturas_dat.documento)) AS clientes,
                            ROUND(SUM(facturas_dat.cantidad - devolucion)) AS unidades_vendidas,
                            ROUND(SUM(totalmasiva), 2) AS ventas_bs,
                            ROUND(SUM(totalmasiva / tasa_primera_actualizacion), 2) AS ventas_dolar,
                            ROUND(SUM(totalmasiva / t1.cliente), 2) AS ticket_promedio,
                            ROUND(SUM((facturas_dat.cantidad - devolucion) / t1.cliente), 2) AS UPT,
                            t1.areas
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
        return transform_query_to_pd_df(sql_query)
    
    elif query == 'Estadisticas por linea':
        sql_query = f'''SELECT
                            facturas_dat.fecha,
                            ROUND(SUM(cantidad)) AS Unidades,
                            ROUND(SUM(totalmasiva), 2) AS Ventas,
                            Linea
                        FROM
                            facturas_dat
                        WHERE facturas_dat.fecha BETWEEN '{date_init}' AND '{date_end}'
                            AND codprod NOT IN(969437, 967836,928905,939572,940627,939573,939574,940769,948544,956358,963444,963440,963532,960510,963442,963620,963438,963616,963619,963617,963618,963437,963744,963434,963445,963446,963448,963950,963961,963963,963964,963965,964211,964456,964216,964504,964503,964217,964322,956262,960258,962082,962287,963321,963322,963869,964102,964112,964223,964229,964301,964303,964342,964356,963737,963615,963951,963962,964207,964740,964990,965099,965100,946779,963737,964558,965618,965620,965758)
                        GROUP BY facturas_dat.fecha, linea'''
        return transform_query_to_pd_df(sql_query)
    
    elif query == 'Conexiones':
        sql_query = f'''SELECT 
                            nombre, grupo, servidor, puerto, nomusua, clave, nom_corto, basedata
                        FROM 
                            farmacias'''
        return transform_query_to_pd_df(sql_query)
    
    return None

def autentificador(password):
    conn, cursor = get_connection()
    if cursor:
        try:
            cursor.execute(f"SELECT nombre FROM usuarios WHERE clave = '{password.upper()}'")
            user = cursor.fetchone()[0]
        finally:
            conn.close()
        
        if user:
            return user
    return False

def transform_query_to_pd_df(sql_query):
    conn, cursor = get_connection()
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
        raise Exception('Conexion Fallida')
    else:
        raise Exception('Conexion Fallida')

def get_connection():
    host = '10.0.2.1'
    user = 'jonas.salas'
    password = 'camaleon'
    database = 'hptal'

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
    
print(autentificador('vx77ff'))