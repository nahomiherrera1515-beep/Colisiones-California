# Diccionario de datos

Este documento describe, campo por campo, la base normalizada `base_normalizada.duckdb` y su copia en Parquet dentro de `data/processed/`. El período es 2010-2019. Los porcentajes de nulos y de "Sin clasificar" los medimos sobre la base cargada por `03_procesamiento_carga.py`; la sección 15 explica cómo reproducirlos.

| Grupo | Tablas | Filas |
|---|---:|---:|
| Datos de casos (secciones 1 a 10) | 10 | 59.585.754 |
| Catálogos (sección 11) | 42 | 9.127 |
| Vistas de consumo (sección 12) | 5 | no guardan filas |

La base tiene las mismas tablas en local (`base_normalizada.duckdb`) y en MotherDuck (`colisiones_normalizada`). Comparamos las dos con una huella por fila y son idénticas.

## Convenciones

| Etiqueta | Qué quiere decir |
|---|---|
| FUENTE | El valor viene de SWITRS tal cual; a lo sumo cambia el tipo. |
| DERIVADO | Sale de un campo de la fuente con una regla que se indica entre paréntesis. |
| CONSTRUIDO | No existe en la fuente. Lo definimos nosotros. |

- PK es llave primaria y "FK tabla" es llave foránea hacia esa tabla.
- En todos los catálogos de códigos el id 0 es "Sin clasificar". Ahí caen los NULL y los códigos que no figuran en el catálogo, así que ninguna fila se descarta por un código raro.
- Las llaves de las tablas grandes no se declaran en DuckDB. Están documentadas aquí y la razón está en [MODELADO_DE_DATOS.md](MODELADO_DE_DATOS.md#5-llaves-no-declaradas).
- En la carpeta `data/processed/`, cada tabla con datos de casos tiene un archivo por año: `<tabla>/<tabla>_<año>.parquet`. Los catálogos están en `catalogos/<catalogo>.parquet`.

---

## 1. `colision` (4.368.293 filas)

Una fila por colisión.

| Campo | Tipo | Llave | Procedencia | Descripción | Nulos o sin clasificar |
|---|---|---|---|---|---:|
| `case_id` | INTEGER | PK | FUENTE (`case_id`) | Identificador del parte policial. En la fuente es texto, pero en el período es siempre numérico. | 0 % |
| `fecha` | DATE | | FUENTE (`collision_date`) | Fecha del choque. El calendario se arma en la vista `vw_calendario`. | 0 % |
| `hora` | TIME | | FUENTE (`collision_time`) | Hora del choque. NULL quiere decir hora desconocida; no se rellena con 00:00. | 0,91 % nulo |
| `ubicacion_id` | USMALLINT | FK ubicacion | FUENTE (`county_city_location`) | Código de condado y ciudad. De él dependen el condado y el rango de población. | 0 % |
| `jurisdiccion` | USMALLINT | | FUENTE (`jurisdiction`) | Agencia que levantó el parte. La fuente no trae sus nombres. | 0,19 % nulo |
| `iluminacion_id` | UTINYINT | FK iluminacion | FUENTE (`lighting`) | Condición de luz. | 0,45 % sin clasificar |
| `superficie_id` | UTINYINT | FK superficie | FUENTE (`road_surface`) | Estado de la calzada. | 0,67 % sin clasificar |
| `dispositivo_control_id` | UTINYINT | FK dispositivo_control | FUENTE (`control_device`) | Semáforo o señal y su estado. | 0,61 % sin clasificar |
| `tipo_colision_id` | UTINYINT | FK tipo_colision | FUENTE (`type_of_collision`) | Cómo fue el impacto. | 0,88 % sin clasificar |
| `implicado_con_id` | UTINYINT | FK implicado_con | FUENTE (`motor_vehicle_involved_with`) | Contra qué chocó el vehículo. | 0,53 % sin clasificar |
| `factor_primario_id` | UTINYINT | FK factor_primario | FUENTE (`primary_collision_factor`) | Factor primario. Incluye un código basura `'2'`. | 0,35 % sin clasificar |
| `categoria_infraccion_id` | UTINYINT | FK categoria_infraccion | FUENTE (`pcf_violation_category`) | Categoría de la infracción principal. | 1,29 % sin clasificar |
| `infraccion_vehicular_id` | USMALLINT | FK infraccion_vehicular | DERIVADO (`pcf_violation` + `pcf_violation_subsection`) | Sección e inciso del código vehicular citados. NULL si no hay cita. Un inciso sin sección no identifica ninguna cita y no se guarda (128 casos entre colisiones y partes). | 6,42 % nulo |
| `fuga_id` | UTINYINT | FK fuga | FUENTE (`hit_and_run`) | Si el responsable huyó y cómo se tipificó. | 1 fila sin clasificar |
| `accion_peaton_id` | UTINYINT | FK accion_peaton | FUENTE (`pedestrian_action`) | Qué hacía el peatón, si lo había. | 0,07 % sin clasificar |
| `en_interseccion` | BOOLEAN | | FUENTE (`intersection`) | Ocurrió en una intersección. | 0,61 % nulo |
| `vehiculo_remolcado` | BOOLEAN | | FUENTE (`tow_away`) | Algún vehículo salió en grúa. | 0,73 % nulo |
| `carretera_estatal` | BOOLEAN | | FUENTE (`state_highway_indicator`) | Ocurrió en una carretera estatal. No se deriva de `colision_carretera`: hay 802.244 choques marcados en carretera estatal sin bloque Caltrans. | 0,02 % nulo |
| `condicion_especial` | BOOLEAN | | DERIVADO (`special_condition = '1'`) | Condición especial del lugar. | 0 % |

Columnas de la fuente que no guardamos porque se recalculan en `vw_colision`: `alcohol_involved` (vale 1 exactamente cuando alguna parte había bebido), `killed_victims`, `injured_victims`, `severe_injury_count`, `other_visible_injury_count`, `complaint_of_pain_injury_count`, los conteos por peatón, ciclista y motociclista, `party_count`, `collision_severity`, `pedestrian_collision`, `bicycle_collision`, `motorcycle_collision`, `truck_collision` y los tipos de vehículo del culpable. `county_location` y `population` dependen de `county_city_location` y viven en `ubicacion`. `weather_1/2` y `road_condition_1/2` pasaron a tablas puente.

## 2. `colision_clima` (4.471.970 filas)

Tabla puente para el grupo repetido `weather_1` y `weather_2`.

| Campo | Tipo | Llave | Procedencia | Descripción |
|---|---|---|---|---|
| `case_id` | INTEGER | PK, FK colision | FUENTE | |
| `orden` | UTINYINT | PK | CONSTRUIDO | Posición en la fuente: 1 para `weather_1`, 2 para `weather_2`. |
| `clima_id` | UTINYINT | FK clima | FUENTE (`weather_1` o `weather_2`) | Condición atmosférica. |

Solo hay fila si la fuente llenó esa posición: 4.352.898 con orden 1 y 119.072 con orden 2. Las 15.395 colisiones sin clima principal aparecen en `vw_colision` con `clima_id = 0`.

## 3. `colision_condicion_via` (4.357.925 filas)

Tabla puente para el grupo repetido `road_condition_1` y `road_condition_2`.

| Campo | Tipo | Llave | Procedencia | Descripción |
|---|---|---|---|---|
| `case_id` | INTEGER | PK, FK colision | FUENTE | |
| `orden` | UTINYINT | PK | CONSTRUIDO | 1 para `road_condition_1`, 2 para `road_condition_2`. |
| `condicion_via_id` | UTINYINT | FK condicion_via | FUENTE (`road_condition_1` o `road_condition_2`) | Obras, baches, objetos en la vía, carril reducido o normal. |

Hay 4.338.207 filas con orden 1 y 19.718 con orden 2. Las colisiones sin fila de orden 1 aparecen en `vw_colision` con `condicion_via_id = 0`.

## 4. `colision_geo` (2.159.739 filas)

Colisiones con coordenadas. Relación 1:0..1 con `colision`: el 49,4 % de los choques tiene coordenadas.

| Campo | Tipo | Llave | Procedencia | Descripción |
|---|---|---|---|---|
| `case_id` | INTEGER | PK, FK colision | FUENTE | La PK también es FK, así que cada colisión tiene a lo sumo una fila. |
| `latitud` | DECIMAL(8,5) | | FUENTE (`latitude`) | Grados decimales, de 32,50 a 42,04. La fuente trae como máximo 5 decimales. |
| `longitud` | DECIMAL(8,5) | | FUENTE (`longitude`) | Grados decimales, de -124,50 a -114,10. |

Solo entran pares completos dentro de la caja de California (latitud 32 a 43, longitud -125 a -114). No imputamos coordenadas. La cobertura crece con los años (34,3 % en 2010 y 64,1 % en 2019), así que un mapa de los diez años juntos mostraría sobre todo cómo mejoró el registro.

## 5. `colision_carretera` (904.581 filas)

Colisiones con datos de carretera estatal (bloque Caltrans). Relación 1:0..1 con `colision`. Las columnas del bloque son nulas o no nulas siempre juntas.

| Campo | Tipo | Llave | Procedencia | Descripción | Nulos |
|---|---|---|---|---|---:|
| `case_id` | INTEGER | PK, FK colision | FUENTE | | 0 % |
| `condado_caltrans_id` | UTINYINT | FK condado | FUENTE (`caltrans_county`) | Condado del tramo según Caltrans. Puede no coincidir con el condado de la colisión. | 2 filas sin clasificar |
| `distrito_caltrans` | UTINYINT | | FUENTE (`caltrans_district`) | Distrito Caltrans (1 a 12). No depende solo del condado: seis condados tienen tramos en dos distritos. | 0 % |
| `ruta_estatal` | USMALLINT | | FUENTE (`state_route`) | Número de la ruta. | 0 % |
| `prefijo_postmile` | VARCHAR | | FUENTE (`postmile_prefix`) | Letra que acompaña al postmile (R, M, L...). Es parte de la notación, no un código con catálogo. | 69,18 % |
| `postmile` | DECIMAL(6,3) | | FUENTE (`postmile`) | Punto kilométrico de la ruta, en millas. | 0 % |
| `tipo_ubicacion_id` | UTINYINT | FK tipo_ubicacion | FUENTE (`location_type`) | Tramo, intersección o rampa. Cuando hay `rampa_interseccion`, coincide siempre con ella; cuando no hay, es el único dato. | 1 fila sin clasificar |
| `sentido_id` | UTINYINT | FK sentido | FUENTE (`side_of_highway`) | Calzada por la que circulaba. | 7 filas sin clasificar |
| `rampa_interseccion_id` | UTINYINT | FK rampa_interseccion | FUENTE (`ramp_intersection`) | Posición respecto de rampas e intersecciones. NULL si no aplica. | 77,97 % |

## 6. `parte` (8.688.142 filas)

Una fila por parte implicada: conductor, peatón, ciclista, vehículo estacionado u otro.

| Campo | Tipo | Llave | Procedencia | Descripción | Nulos o sin clasificar |
|---|---|---|---|---|---:|
| `case_id` | INTEGER | PK, FK colision | FUENTE | | 0 % |
| `numero_parte` | UTINYINT | PK | FUENTE (`party_number`) | Número de la parte dentro de la colisión. | 0 % |
| `tipo_parte_id` | UTINYINT | FK tipo_parte | FUENTE (`party_type`) | Conductor, peatón, ciclista... | 0,10 % sin clasificar |
| `culpable` | BOOLEAN | | DERIVADO (`at_fault = 1`) | La parte fue señalada como responsable. Hay a lo sumo un culpable por colisión. | 0 % |
| `sexo_id` | UTINYINT | FK sexo | FUENTE (`party_sex`) | | 13,64 % sin clasificar |
| `edad` | UTINYINT | | DERIVADO (`party_age` en 0-110) | Edad en años. Fuera del rango queda NULL. | 15,62 % nulo |
| `edad_en_cuarentena` | BOOLEAN | | CONSTRUIDO | TRUE si la fuente traía una edad fuera de 0-110 (38 casos). Distingue ese NULL de uno de origen. | 0 % |
| `raza_id` | UTINYINT | FK raza | FUENTE (`party_race`) | | 17,31 % sin clasificar |
| `sobriedad_id` | UTINYINT | FK sobriedad | FUENTE (`party_sobriety`) | Si había bebido y con qué efecto. De aquí sale `alcohol_implicado` de la colisión. | 2,65 % sin clasificar |
| `droga_fisica_id` | UTINYINT | FK droga_fisica | FUENTE (`party_drug_physical`) | Drogas, impedimento físico o fatiga. La fuente lo llena poco. | 82,88 % sin clasificar |
| `direccion_id` | UTINYINT | FK direccion | FUENTE (`direction_of_travel`) | Sentido de circulación. | 2,75 % sin clasificar |
| `movimiento_previo_id` | UTINYINT | FK movimiento_previo | FUENTE (`movement_preceding_collision`) | Qué hacía justo antes del choque. | 1,89 % sin clasificar |
| `tipo_vehiculo_id` | UTINYINT | FK tipo_vehiculo | FUENTE (`statewide_vehicle_type`) | Tipo de vehículo, con un `grupo` para agregar. | 10,15 % sin clasificar |
| `anio_vehiculo` | USMALLINT | | DERIVADO (`vehicle_year` en 1900-2020) | Año del modelo. La antigüedad al chocar se calcula en las vistas. | 10,01 % nulo |
| `anio_vehiculo_en_cuarentena` | BOOLEAN | | CONSTRUIDO | TRUE si el año venía fuera de 1900-2020 (2 casos). | 0 % |
| `marca_vehiculo_id` | USMALLINT | FK marca_vehiculo | FUENTE (`vehicle_make`) | Marca tal como la escribió el agente. | 9,22 % sin clasificar |
| `vehiculo_chp_id` | UTINYINT | FK vehiculo_chp | FUENTE (`chp_vehicle_type_towing`) | Tipo de vehículo según la clasificación de la CHP. | 9,27 % sin clasificar |
| `remolque_chp_id` | UTINYINT | FK vehiculo_chp | FUENTE (`chp_vehicle_type_towed`) | Lo que remolcaba, con la misma clasificación. La fuente no documenta el código `00`; lo leemos como "ninguno o no consignado". | 68,23 % sin clasificar |
| `responsabilidad_financiera_id` | UTINYINT | FK responsabilidad_financiera | FUENTE (`financial_responsibility`) | Si mostró comprobante de seguro. | 7,78 % sin clasificar |
| `uso_celular_id` | UTINYINT | FK uso_celular | FUENTE (`cellphone_use_type`) | Uso del celular. El catálogo trae `en_uso`, que reproduce `cellphone_in_use`. | 15,20 % sin clasificar |
| `materiales_peligrosos` | BOOLEAN | | DERIVADO (`1` pasa a TRUE) | TRUE o NULL, como en la fuente. | 99,86 % nulo |
| `relacion_bus_escolar` | BOOLEAN | | DERIVADO (`1` pasa a TRUE) | TRUE o NULL, como en la fuente. | 99,63 % nulo |
| `otra_infraccion_categoria_id` | UTINYINT | FK otra_infraccion_categoria | FUENTE (`oaf_violation_category`) | Otra infracción de la parte, aparte de la principal. NULL si no hubo. | 93,49 % nulo |
| `otra_infraccion_vehicular_id` | USMALLINT | FK infraccion_vehicular | DERIVADO (`oaf_violation_section` + `oaf_violation_suffix`) | Sección e inciso de esa otra infracción. | 93,42 % nulo |

Columnas de la fuente que ya no están: `cellphone_in_use` (se deriva de `uso_celular`), `party_safety_equipment_1/2` y `other_associate_factor_1/2` (tablas puente).

## 7. `parte_equipo_seguridad` (14.175.726 filas)

| Campo | Tipo | Llave | Procedencia | Descripción |
|---|---|---|---|---|
| `case_id` | INTEGER | PK, FK parte | FUENTE | |
| `numero_parte` | UTINYINT | PK, FK parte | FUENTE | |
| `orden` | UTINYINT | PK | CONSTRUIDO | 1 para `party_safety_equipment_1`, 2 para `party_safety_equipment_2`. |
| `equipo_seguridad_id` | UTINYINT | FK equipo_seguridad | FUENTE (`party_safety_equipment_1` o `_2`) | Cinturón, casco, airbag o silla infantil, usado o no. |

Hay 7.203.018 filas con orden 1 y 6.972.708 con orden 2.

## 8. `parte_factor_asociado` (8.370.228 filas)

| Campo | Tipo | Llave | Procedencia | Descripción |
|---|---|---|---|---|
| `case_id` | INTEGER | PK, FK parte | FUENTE | |
| `numero_parte` | UTINYINT | PK, FK parte | FUENTE | |
| `orden` | UTINYINT | PK | CONSTRUIDO | 1 para `other_associate_factor_1`, 2 para `other_associate_factor_2`. |
| `factor_asociado_id` | UTINYINT | FK factor_asociado | FUENTE (`other_associate_factor_1` o `_2`) | Otro factor que el agente asoció a la parte: visión obstruida, distracción, clima, etc. |

Hay 8.197.200 filas con orden 1 y 173.028 con orden 2.

## 9. `victima` (4.280.801 filas)

Una fila por víctima. Incluye a los ilesos que el agente registró.

| Campo | Tipo | Llave | Procedencia | Descripción | Nulos o sin clasificar |
|---|---|---|---|---|---:|
| `case_id` | INTEGER | PK, FK parte | FUENTE | | 0 % |
| `numero_parte` | UTINYINT | PK, FK parte | FUENTE (`party_number`) | Parte con la que viajaba la víctima. | 0 % |
| `numero_victima` | UTINYINT | PK | CONSTRUIDO | `ROW_NUMBER()` por `id` dentro de cada parte. La fuente no numera las víctimas y su `id` no es único. | 0 % |
| `rol_victima_id` | UTINYINT | FK rol_victima | FUENTE (`victim_role`) | Conductor, pasajero, peatón... | 0 % |
| `sexo_id` | UTINYINT | FK sexo | FUENTE (`victim_sex`) | | 2,41 % sin clasificar |
| `edad` | UTINYINT | | DERIVADO (`victim_age` en 0-110) | | 3,32 % nulo |
| `edad_en_cuarentena` | BOOLEAN | | CONSTRUIDO | TRUE si la edad venía fuera de 0-110 (171 casos). | 0 % |
| `lesion_id` | UTINYINT | FK lesion | FUENTE (`victim_degree_of_injury`) | Grado de lesión. Su nivel KABCO está en el catálogo. | 0 % |
| `asiento_id` | UTINYINT | FK asiento | FUENTE (`victim_seating_position`) | | 0,01 % sin clasificar |
| `eyeccion_id` | UTINYINT | FK eyeccion | FUENTE (`victim_ejected`) | | 0,08 % sin clasificar |

Cuando la víctima es el conductor, su edad y sexo difieren de los de su parte en cerca del 8 % de los casos. No lo corregimos: son dos registros distintos del mismo parte policial.

## 10. `victima_equipo_seguridad` (7.808.349 filas)

Tabla puente de `victim_safety_equipment_1` y `_2`.

| Campo | Tipo | Llave | Procedencia | Descripción |
|---|---|---|---|---|
| `case_id` | INTEGER | PK, FK victima | FUENTE | |
| `numero_parte` | UTINYINT | PK, FK victima | FUENTE | |
| `numero_victima` | UTINYINT | PK, FK victima | CONSTRUIDO | El mismo número que en `victima`. |
| `orden` | UTINYINT | PK | CONSTRUIDO | 1 para `victim_safety_equipment_1`, 2 para `victim_safety_equipment_2`. |
| `equipo_seguridad_id` | UTINYINT | FK equipo_seguridad | FUENTE (`victim_safety_equipment_1` o `_2`) | Mismo catálogo que el equipo de las partes. 1 fila sin clasificar. |

Hay 4.031.624 filas con orden 1 y 3.776.725 con orden 2.

---

## 11. Catálogos

### Catálogos de códigos

Todos tienen la misma estructura:

| Campo | Tipo | Descripción |
|---|---|---|
| `<catalogo>_id` | UTINYINT PK | 0 es "Sin clasificar"; los demás siguen el orden de la lista en `catalogos.py`. |
| `codigo` | VARCHAR UNIQUE | Valor literal de la fuente. NULL en el id 0. |
| `etiqueta` | VARCHAR | Nombre en español. |
| `orden` | UTINYINT | Orden para presentar (no alfabético). |

Algunos llevan columnas extra:

| Catálogo | Columna extra | Para qué sirve |
|---|---|---|
| `clima` | `es_adverso` | Lluvia, niebla, nieve y viento fuerte. |
| `iluminacion` | `es_oscuridad` | Los tres tipos de oscuridad. |
| `superficie` | `es_adversa` | Mojada, nieve o hielo, resbaladiza. |
| `categoria_infraccion` | `grupo` | Conducta, prioridad y señalización, estado del conductor, peatón, vehículo, otros. |
| `tipo_vehiculo` | `grupo` | Automóvil, camioneta, camión, motocicleta, autobús, no motorizado, otro. |
| `sobriedad` | `bebio` | TRUE en los tres códigos "had been drinking", FALSE si no había bebido y NULL si se desconoce. |
| `uso_celular` | `en_uso` | TRUE, FALSE o NULL. Reemplaza a la columna `cellphone_in_use`. |
| `lesion` | `kabco`, `observado_desde`, `observado_hasta` | Nivel KABCO del código y años en que aparece en los datos. |

Los 32 catálogos de este tipo, con sus filas (incluido el id 0) y dónde se usan:

| Catálogo | Filas | Columna de la fuente | Se usa en |
|---|---:|---|---|
| `accion_peaton` | 8 | `pedestrian_action` | `colision` |
| `asiento` | 11 | `victim_seating_position` | `victima` |
| `categoria_infraccion` | 24 | `pcf_violation_category` | `colision` |
| `clima` | 8 | `weather_1`, `weather_2` | `colision_clima` |
| `condicion_via` | 9 | `road_condition_1`, `road_condition_2` | `colision_condicion_via` |
| `direccion` | 5 | `direction_of_travel` | `parte` |
| `dispositivo_control` | 5 | `control_device` | `colision` |
| `droga_fisica` | 6 | `party_drug_physical` | `parte` |
| `equipo_seguridad` | 24 | `party_safety_equipment_1/2`, `victim_safety_equipment_1/2` | `parte_equipo_seguridad`, `victima_equipo_seguridad` |
| `eyeccion` | 5 | `victim_ejected` | `victima` |
| `factor_asociado` | 13 | `other_associate_factor_1/2` | `parte_factor_asociado` |
| `factor_primario` | 6 | `primary_collision_factor` | `colision` |
| `fuga` | 4 | `hit_and_run` | `colision` |
| `iluminacion` | 6 | `lighting` | `colision` |
| `implicado_con` | 11 | `motor_vehicle_involved_with` | `colision` |
| `lesion` | 9 | `victim_degree_of_injury` | `victima` |
| `movimiento_previo` | 19 | `movement_preceding_collision` | `parte` |
| `otra_infraccion_categoria` | 33 | `oaf_violation_category` | `parte` |
| `rampa_interseccion` | 7 | `ramp_intersection` | `colision_carretera` |
| `raza` | 6 | `party_race` | `parte` |
| `responsabilidad_financiera` | 5 | `financial_responsibility` | `parte` |
| `rol_victima` | 6 | `victim_role` | `victima` |
| `sentido` | 5 | `side_of_highway` | `colision_carretera` |
| `sexo` | 4 | `party_sex`, `victim_sex` | `parte`, `victima` |
| `sobriedad` | 7 | `party_sobriety` | `parte` |
| `superficie` | 5 | `road_surface` | `colision` |
| `tipo_colision` | 9 | `type_of_collision` | `colision` |
| `tipo_parte` | 6 | `party_type` | `parte` |
| `tipo_ubicacion` | 4 | `location_type` | `colision_carretera` |
| `tipo_vehiculo` | 16 | `statewide_vehicle_type` | `parte` |
| `uso_celular` | 6 | `cellphone_use_type` | `parte` |
| `vehiculo_chp` | 89 | `chp_vehicle_type_towing`, `chp_vehicle_type_towed` | `parte` (vehículo y remolque) |

Todos declaran su PK y `codigo` como UNIQUE.

### `kabco` y `lesion`

| Campo de `kabco` | Tipo | Descripción |
|---|---|---|
| `kabco` | VARCHAR PK | K, A, B, C u O. |
| `nivel` | UTINYINT UNIQUE | 4 (K) a 0 (O). Sirve para ordenar y tomar el máximo. |
| `etiqueta` | VARCHAR | Fallecido, lesión grave, lesión visible, posible lesión o dolor, sin lesiones. |
| `severidad_fuente` | VARCHAR UNIQUE | Valor de `collision_severity` que corresponde a ese nivel. |

| Código en `lesion` | KABCO | Observado |
|---|:---:|---|
| `killed` | K | 2010-2019 |
| `severe injury` | A | 2010-2019 |
| `suspected serious injury` | A | 2016-2019 |
| `other visible injury` | B | 2010-2019 |
| `suspected minor injury` | B | 2016-2019 |
| `complaint of pain` | C | 2010-2019 |
| `possible injury` | C | 2016-2019 |
| `no injury` | O | 2010-2019 |

La escala no es continua entre años. En 2017 SWITRS empezó a usar códigos nuevos (en 2016 hay unos pocos casos) y los dos juegos conviven hasta 2019. Entre 2016 y 2019 las víctimas en A suben un 23,9 % y los ilesos bajan un 67,2 %. Para comparar años usamos solo K.

### Geografía y población

| Tabla | Llave | Campos | Notas |
|---|---|---|---|
| `condado` | `condado_id` (1 Alameda a 58 Yuba, 0 Sin clasificar) | `codigo`, `nombre` | 59 filas. `codigo` es el nombre como aparece en la fuente. Lo usan `ubicacion` y `colision_carretera`. |
| `rango_poblacion` | `rango_poblacion_id` | `codigo`, `etiqueta`, `orden` | 9 filas. Tamaño de la ciudad, desde `population`: de menos de 2.500 habitantes a más de 250.000, y zona no incorporada. |
| `ubicacion` | `ubicacion_id` (`county_city_location`) | `condado_id`, `rango_poblacion_id` | 542 ubicaciones. El condado son los dos primeros dígitos del código. Comprobamos que cada ubicación tiene un solo condado y un solo rango de población en la fuente. |
| `poblacion_condado` | `condado_id`, `anio` | `habitantes` | Estimaciones del Census Bureau (vintage 2019) al 1 de julio de cada año. 580 filas. |

### Calendario

| Tabla o vista | Llave | Campos |
|---|---|---|
| `mes` | `mes` | `nombre`, `trimestre` |
| `dia_semana` | `dia_semana` (1 lunes a 7 domingo) | `nombre`, `es_fin_semana` |
| `vw_calendario` | `fecha` | `anio`, `mes`, `nombre_mes`, `trimestre`, `dia_semana`, `nombre_dia`, `es_fin_semana` |

### Construidos y armados desde la fuente

| Tabla | Llave | Campos | Notas |
|---|---|---|---|
| `banda_edad` | `banda_edad_id` | `etiqueta`, `edad_min`, `edad_max` | 10 filas: menos de 16 (0-15), 16-19, 20-24, 25-34, 35-44, 45-54, 55-64, 65-74 y 75 o más (75-110). La banda 0 es "Desconocida". |
| `marca_vehiculo` | `marca_vehiculo_id` | `codigo` | 5.193 marcas más el id 0, numeradas de la más a la menos frecuente. No unificamos variantes como `KW` y `kenworth`. |
| `infraccion_vehicular` | `infraccion_vehicular_id` | `seccion`, `inciso` | 2.328 citas del California Vehicle Code. La comparten la infracción principal y la otra infracción de cada parte. |

---

## 12. Vistas de consumo

Las vistas recalculan todo lo que no guardamos. Están en `consumo.py` y funcionan igual sobre la base DuckDB y sobre los Parquet.

| Vista | Grano | Qué agrega |
|---|---|---|
| `vw_calendario` | día | Los 3.652 días del período con mes, trimestre y día de la semana. |
| `vw_colision` | colisión | Año, mes, día de la semana y hora, condado, clima y condición de la vía principales y secundarios, severidad (peor KABCO de sus víctimas), conteos por nivel, número de partes, alcohol, banderas de peatón, ciclista, motociclista y camión, fuga, edad y banda del conductor culpable, antigüedad de su vehículo, cobertura de coordenadas y Caltrans. |
| `vw_parte` | parte | Año, condado, banda de edad, antigüedad del vehículo, equipo de seguridad y factor asociado, `usaba_celular` y la peor lesión de sus víctimas. |
| `vw_victima` | víctima | Nivel KABCO, banda de edad, equipo de seguridad, si era ocupante de un vehículo y datos del vehículo en que viajaba. |
| `vw_condado_anio` | condado y año | Colisiones, fallecidos, habitantes y tasas por 100.000 habitantes. |

Definiciones que conviene tener a mano:

- `severidad`: peor nivel KABCO entre las víctimas. Sin víctimas registradas, O.
- `con_fallecido`: la colisión tiene al menos una víctima K.
- `es_grave`: severidad K o A. Ojo con comparar años por el cambio de 2017.
- `alcohol_implicado`: TRUE si alguna parte había bebido y NULL en otro caso, nunca FALSE. Reproduce `alcohol_involved` de la fuente (440.916 colisiones con TRUE). NULL quiere decir "no reportado", no "sobrio".
- `hay_conductor_culpable`: el culpable de la colisión es un conductor. Es el universo del objetivo 2.
- `edad_conductor_culpable`: edad de la parte culpable solo si es conductor.
- `banda_edad_conductor_culpable_id`: NULL si no hay conductor culpable; 0 ("Desconocida") si lo hay pero falta su edad.
- `conductor_culpable_bebio`: si el conductor culpable había bebido (TRUE en 393.839 colisiones). No es lo mismo que `alcohol_implicado`: en 12.655 colisiones el conductor culpable consta como que no había bebido y otra parte sí.
- `es_ocupante`: la víctima iba como conductor o pasajero de un vehículo. Es el universo del objetivo 4; deja fuera a peatones y ciclistas.
- `edad_vehiculo`: año de la colisión menos año del modelo. Un modelo del año siguiente da -1 y se lleva a 0.
- Las banderas `peaton_implicado`, `ciclista_implicado`, `motociclista_implicado` y `camion_implicado` no son excluyentes: 1.178 colisiones tienen a la vez peatón y motociclista. Sumarlas no da el total de colisiones.

Distribución de `severidad` en `vw_colision`:

| `severidad` | Significado | Colisiones | % |
|:---:|---|---:|---:|
| K | Al menos un fallecido | 30.867 | 0,71 |
| A | Peor víctima con lesión grave | 108.209 | 2,48 |
| B | Peor víctima con lesión visible | 535.313 | 12,25 |
| C | Peor víctima con posible lesión o dolor | 1.102.846 | 25,25 |
| O | Sin lesionados (incluye 2.032.351 colisiones sin víctimas registradas) | 2.591.058 | 59,32 |

### Columnas que agrega cada vista

Cada vista trae todas las columnas de su tabla base (`colision`, `parte` o `victima`) y agrega estas. Las columnas `_id` se unen con el catálogo del mismo nombre.

**`vw_colision`** (55 columnas: las 19 de `colision` y 36 nuevas)

| Columna | Tipo | Definición |
|---|---|---|
| `anio`, `mes`, `dia_semana` | BIGINT | Año, mes (1 a 12) y día ISO (1 lunes a 7 domingo) de `fecha`. |
| `hora_del_dia` | BIGINT | Hora 0 a 23 de `hora`. NULL si la hora es desconocida. |
| `condado_id`, `rango_poblacion_id` | UTINYINT | Desde `ubicacion`. |
| `clima_id`, `clima_2_id` | UTINYINT | Clima de orden 1 (0 si no hay) y de orden 2 (NULL si no hay). |
| `condicion_via_id`, `condicion_via_2_id` | UTINYINT | Igual, para la condición de la vía. |
| `severidad`, `nivel_severidad` | VARCHAR, UTINYINT | Peor letra KABCO entre sus víctimas y su nivel (4 a 0). |
| `con_fallecido`, `es_grave` | BOOLEAN | Severidad K; severidad K o A. |
| `victimas`, `fallecidos`, `heridos_graves`, `heridos_visibles`, `posibles_lesionados` | BIGINT | Víctimas registradas y cuántas en K, A, B y C. |
| `partes` | BIGINT | Número de partes. |
| `peaton_implicado`, `ciclista_implicado` | BOOLEAN | Alguna parte es peatón o ciclista (`tipo_parte`). |
| `motociclista_implicado`, `camion_implicado` | BOOLEAN | Algún vehículo es del grupo Motocicleta o Camión (`tipo_vehiculo.grupo`). |
| `alcohol_implicado` | BOOLEAN | Ver arriba. TRUE o NULL. |
| `hubo_fuga` | BOOLEAN | `fuga` distinto de "not hit and run". |
| `tipo_parte_culpable_id`, `tipo_vehiculo_culpable_id` | UTINYINT | Tipo de la parte culpable y de su vehículo. NULL si no hay culpable. |
| `hay_conductor_culpable` | BOOLEAN | El culpable es un conductor (3.926.268 colisiones). |
| `edad_conductor_culpable`, `banda_edad_conductor_culpable_id` | UTINYINT | Ver arriba. |
| `conductor_culpable_bebio` | BOOLEAN | Ver arriba. |
| `anio_vehiculo_culpable`, `edad_vehiculo_culpable` | USMALLINT, BIGINT | Año del modelo del vehículo culpable y su antigüedad al chocar. |
| `tiene_coordenadas`, `tiene_datos_caltrans` | BOOLEAN | Hay fila en `colision_geo` o en `colision_carretera`. |

**`vw_parte`** (37 columnas: las 24 de `parte` y 13 nuevas)

| Columna | Tipo | Definición |
|---|---|---|
| `fecha`, `anio`, `condado_id` | DATE, BIGINT, UTINYINT | De la colisión de la parte. |
| `banda_edad_id` | UTINYINT | Banda de `edad`; 0 si falta la edad. |
| `edad_vehiculo` | BIGINT | Antigüedad del vehículo al chocar. |
| `equipo_seguridad_id`, `equipo_seguridad_2_id` | UTINYINT | Equipo de orden 1 (0 si no hay) y de orden 2 (NULL si no hay). |
| `factor_asociado_id`, `factor_asociado_2_id` | UTINYINT | Igual, para el factor asociado. |
| `usaba_celular` | BOOLEAN | `en_uso` del catálogo `uso_celular`. |
| `nivel_max_victimas` | UTINYINT | Peor nivel KABCO entre las víctimas de esa parte. NULL si no tiene víctimas. |
| `victimas`, `fallecidos` | BIGINT | Víctimas de la parte y cuántas en K. |

**`vw_victima`** (24 columnas: las 10 de `victima` y 14 nuevas)

| Columna | Tipo | Definición |
|---|---|---|
| `kabco`, `nivel_lesion` | VARCHAR, UTINYINT | Letra KABCO de la lesión y su nivel. |
| `banda_edad_id` | UTINYINT | Banda de `edad`; 0 si falta la edad. |
| `equipo_seguridad_id`, `equipo_seguridad_2_id` | UTINYINT | Equipo de orden 1 (0 si no hay) y de orden 2 (NULL si no hay). |
| `tipo_parte_id`, `tipo_vehiculo_id`, `anio_vehiculo` | UTINYINT, USMALLINT | De la parte con la que viajaba. |
| `edad_vehiculo` | BIGINT | Antigüedad de ese vehículo al chocar. |
| `parte_culpable` | BOOLEAN | Su parte fue la culpable. |
| `es_ocupante` | BOOLEAN | Rol conductor o pasajero (4.008.982 víctimas). |
| `fecha`, `anio`, `condado_id` | DATE, BIGINT, UTINYINT | De la colisión. |

**`vw_condado_anio`** (580 filas: 58 condados por 10 años)

| Columna | Tipo | Definición |
|---|---|---|
| `condado_id`, `condado` | UTINYINT, VARCHAR | Condado y su nombre. |
| `anio` | USMALLINT | Año. |
| `habitantes` | INTEGER | Población al 1 de julio (Census Bureau). |
| `colisiones`, `fallecidos` | BIGINT | Colisiones del condado y víctimas K en ellas. |
| `colisiones_por_100k`, `fallecidos_por_100k` | DOUBLE | Cada conteo dividido entre `habitantes` y multiplicado por 100.000. |

**`vw_calendario`** (3.652 filas, una por día de 2010 a 2019)

| Columna | Tipo | Definición |
|---|---|---|
| `fecha` | DATE | Día. Incluye los días sin colisiones, para que las series no salten. |
| `anio`, `mes`, `trimestre` | BIGINT, UTINYINT | Año, mes y trimestre. |
| `nombre_mes` | VARCHAR | Enero a diciembre. |
| `dia_semana`, `nombre_dia` | UTINYINT, VARCHAR | 1 lunes a 7 domingo y su nombre. |
| `es_fin_semana` | BOOLEAN | Sábado o domingo. |

---

## 13. Columnas de la fuente que no se cargan

Documentar lo que no entró es tan importante como lo que sí. Ninguna se pierde sin motivo: o se recalcula, o depende de otra columna, o no aporta al estudio.

| Origen | Columnas | Motivo |
|---|---|---|
| `collisions` | `collision_severity`, `killed_victims`, `injured_victims`, `severe_injury_count`, `other_visible_injury_count`, `complaint_of_pain_injury_count`, `pedestrian_killed_count`, `pedestrian_injured_count`, `bicyclist_killed_count`, `bicyclist_injured_count`, `motorcyclist_killed_count`, `motorcyclist_injured_count`, `party_count`, `alcohol_involved`, `pedestrian_collision`, `bicycle_collision`, `motorcycle_collision`, `truck_collision`, `statewide_vehicle_type_at_fault`, `chp_vehicle_type_at_fault` | Se pueden recalcular desde `parte` y `victima`. Las principales ya están en `vw_colision`: fallecidos, heridos por nivel, severidad, partes, alcohol, las cuatro banderas y el tipo de vehículo del culpable. Comparamos cada una con su columna original y coinciden en las 4.368.293 colisiones salvo una, el caso 90771643, que trae `collision_severity = 'N'`, 22 heridos graves, `party_count = 0` y alcohol, aunque tiene dos partes sin víctimas ni alcohol. Lo tratamos como error de captura. |
| `collisions` | `county_location` | Depende de `county_city_location`: vive en `ubicacion`. |
| `collisions` | `officer_id`, `reporting_district`, `chp_shift`, `beat_type`, `chp_beat_type`, `chp_beat_class`, `beat_number`, `city_division_lapd`, `process_date` | Datos internos de la policía y del trámite del parte. No describen el choque. |
| `collisions` | `primary_road`, `secondary_road`, `distance`, `direction`, `primary_ramp`, `secondary_ramp`, `route_suffix`, `chp_road_type` | Localización a nivel de calle, en texto libre o con códigos sin documentar. El estudio trabaja por condado. |
| `collisions` | `pcf_violation_code` | Cuerpo legal de la infracción. Está vacío en todo el período salvo 294 casos. |
| `collisions` | `not_private_property` | Vale 1 en todas las colisiones del período menos una: no distingue nada. |
| `parties` | `party_number_killed`, `party_number_injured` | Se recalculan en `vw_parte` desde `victima`. |
| `parties` | `cellphone_in_use` | Se deriva del catálogo `uso_celular` (columna `en_uso`). |
| `parties` | `oaf_violation_code` | Igual que `pcf_violation_code`: vacío salvo 30 casos. |
| `case_ids` | `case_id`, `db_year` | Solo dice en qué versión del archivo original entró cada caso. No es un dato del choque. |

---

## 14. Calidad de la fuente que conviene recordar

- La escala de lesiones cambió en 2017 (sección 11, `kabco` y `lesion`).
- Las coordenadas pasan de 34,3 % de las colisiones en 2010 a 64,1 % en 2019.
- La edad del conductor culpable falta en el 71,2 % de las colisiones con fuga y en el 2,2 % de las demás.
- `droga_fisica_id` (82,88 % sin clasificar) y `remolque_chp_id` (68,23 %) están poco llenas en la fuente; úselas con cuidado.
- El alcohol y otras marcas solo se registran cuando ocurrieron: NULL es "no reportado".

---

## 15. Cómo verificar este diccionario

Los conteos y porcentajes salen de la base. Por ejemplo, para la tabla `parte`:

```python
import duckdb

con = duckdb.connect("base_de_datos/base_normalizada.duckdb", read_only=True)
con.sql("""
    SELECT COUNT(*)                                                   AS filas,
           ROUND(100 * AVG(CAST(edad IS NULL AS DOUBLE)), 2)          AS pct_edad_nula,
           ROUND(100 * AVG(CAST(sexo_id = 0 AS DOUBLE)), 2)           AS pct_sexo_sin_clasificar,
           COUNT(*) FILTER (WHERE edad_en_cuarentena)                 AS edades_en_cuarentena
    FROM parte
""").show()
```

Con los Parquet se usa `conectar_lago()` de `consumo.py` en lugar de abrir el archivo.
