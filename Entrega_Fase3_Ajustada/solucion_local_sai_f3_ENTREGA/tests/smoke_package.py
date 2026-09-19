import sys, os, json
sys.path.insert(0, r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\package_src")
print("PYTHONPATH[0]:", sys.path[0])
import cafe_sai_modelos_equipo9 as m
print('package version:', m.__version__)
print('features:', m.FEATURES_FENOLOGICAS)

gold_path = r"c:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\_golden.json"
gold = json.load(open(gold_path, encoding='utf-8'))

case = gold['predictions']['Narino_2007']
out = m.predict_rendimiento('Narino', case['features'])
print('Narino_2007 package:', round(out['prediccion_kg_ha'],9), 'status=', out['status'])
print('Narino_2007 golden :', case['y_pred_kg_ha'])
assert abs(out['prediccion_kg_ha'] - case['y_pred_kg_ha']) < 1e-6, 'MISMATCH Narino'

case = gold['predictions']['Quindio_2015']
out = m.predict_rendimiento('Quindio', case['features'])
print('Quindio_2015 package:', round(out['prediccion_kg_ha'],9), 'status=', out['status'])
print('Quindio_2015 golden :', case['y_pred_kg_ha'])
assert abs(out['prediccion_kg_ha'] - case['y_pred_kg_ha']) < 1e-6, 'MISMATCH Quindio'

out_spi = m.predict_activacion_spi('Narino', {'spi_min_e9': -2.0, 'roya_dummy': 0})
print('Narino SPI-2.0 activo:', out_spi['activo'], 'regla=', out_spi['regla_activada'])
assert out_spi['activo'] is True
out_spi2 = m.predict_activacion_spi('Narino', {'roya_dummy': 1, 'roya_shock': 1})
print('Narino ROYA shock activo:', out_spi2['activo'])
assert out_spi2['activo'] is True

kp = m.get_kpis_actuariales()
print('KPIs Narino HE:', kp['Narino']['HE_Ederington'])
print('KPIs Narino prima:', kp['Narino']['prima_actuarial_pct'])
print('KPIs Quindio RMSE:', kp['Quindio']['rmse_holdout_mejor'])

print('panel shape:', m.get_panel_entrenamiento().shape)
print('loyo shape:', m.get_pred_vs_real_loyo().shape)
print('valhist shape:', m.get_validacion_historica_n1().shape)

# Validacion raise depto malo
try:
    m.predict_rendimiento('Bogota', case['features'])
    print('ERROR: depto malo NO raise')
    sys.exit(2)
except ValueError as e:
    print('OK raise depto malo:', type(e).__name__)

# Validacion raise falta campo
try:
    bad = {k:v for k,v in case['features'].items() if k != 'spi3_floracion'}
    m.predict_rendimiento('Narino', bad)
    print('ERROR: falta campo NO raise')
    sys.exit(3)
except ValueError as e:
    print('OK raise falta campo:', type(e).__name__)

# Validacion roya != {0,1}
try:
    bad = dict(case['features']) ; bad['roya_dummy'] = 5
    m.predict_rendimiento('Narino', bad)
    print('ERROR: roya NO raise')
    sys.exit(4)
except ValueError as e:
    print('OK raise roya inválido:', type(e).__name__)

print('[OK] TODOS LOS SMOKE TESTS DEL PACKAGE PASAN')
