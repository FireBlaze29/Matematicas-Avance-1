import pandas as pd
import matplotlib.pyplot as plt
import folium
from folium.plugins import MarkerCluster

df = pd.read_csv('TB_CENTRO_VACUNACION.csv', sep=';', encoding='utf-8-sig')

def convertir_coord(valor):
    if pd.isna(valor):
        return None
    valor_str = str(valor).strip().replace(',', '.')
    try:
        return float(valor_str)
    except ValueError:
        return None

df['lat'] = df['latitud'].apply(convertir_coord)
df['lon'] = df['longitud'].apply(convertir_coord)

df = df.dropna(subset=['lat', 'lon'])
df = df[(df['lat'] != 0) & (df['lon'] != 0)]

print(f"Total de centros válidos: {len(df)}")
print("\nDistribución por entidad:")
print(df['entidad_administra'].value_counts())

mapa_centro = [-9.19, -75.01]
mapa = folium.Map(location=mapa_centro, zoom_start=6, tiles='OpenStreetMap')
marker_cluster = MarkerCluster().add_to(mapa)

for _, row in df.iterrows():
    nombre = row['nombre'] if pd.notna(row['nombre']) else 'Sin nombre'
    entidad = row['entidad_administra'] if pd.notna(row['entidad_administra']) else 'No especificada'
    folium.Marker(
        location=[row['lat'], row['lon']],
        popup=f"<b>{nombre}</b><br>Entidad: {entidad}",
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(marker_cluster)

mapa.save('mapa_centros_vacunacion.html')
print("\n✅ Mapa guardado como 'mapa_centros_vacunacion.html'")

plt.style.use('ggplot')
conteo_entidades = df['entidad_administra'].value_counts().dropna()

plt.figure(figsize=(10, 6))
conteo_entidades.plot(kind='bar', color='skyblue', edgecolor='black')
plt.title('Número de centros de vacunación por entidad administradora', fontsize=14)
plt.xlabel('Entidad')
plt.ylabel('Cantidad')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('barras_entidades.png', dpi=150)
plt.close()
print("✅ Gráfico de barras guardado como 'barras_entidades.png'")

umbral_porcentaje = 2.
total = conteo_entidades.sum()
porcentajes = (conteo_entidades / total) * 100
categorias_principales = porcentajes[porcentajes >= umbral_porcentaje]
otros = porcentajes[porcentajes < umbral_porcentaje].sum()

if otros > 0:
    datos_torta = pd.concat([categorias_principales, pd.Series({'Otros': otros})])
else:
    datos_torta = categorias_principales

colores = plt.cm.Set3(range(len(datos_torta)))

plt.figure(figsize=(8, 8))
datos_torta.plot(kind='pie', autopct='%1.1f%%', startangle=90,
                 colors=colores, wedgeprops={'edgecolor': 'black'})
plt.title(f'Proporción de centros por entidad (agrupando <{umbral_porcentaje}% en "Otros")', fontsize=12)
plt.ylabel('')
plt.tight_layout()
plt.savefig('torta_entidades_agrupadas.png', dpi=150)
plt.close()
print(f"✅ Gráfico de torta agrupado guardado como 'torta_entidades_agrupadas.png'")

print("\n🎉 Todas las visualizaciones están listas.")