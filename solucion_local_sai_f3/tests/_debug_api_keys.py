import requests, json, os, sys
log_path = r"C:\Users\mvale\OneDrive\Escritorio\Caso 01\solucion_local_sai_f3\tests\debug_api_keys.txt"
with open(log_path, "w", encoding="utf-8") as log:
    for path in ["/api/v1/series/historico", "/api/v1/series/pred-vs-real", "/api/v1/track-a/umbrales", "/api/v1/validacion-historica", "/api/v1/kpis", "/health"]:
        try:
            r = requests.get("http://127.0.0.1:8000" + path, timeout=15)
            data = r.json()
            log.write(f"=== {path} HTTP {r.status_code} ===\n")
            if isinstance(data, list) and len(data) > 0:
                log.write(f"TYPE list len={len(data)}\n")
                log.write(f"FIRST ITEM KEYS (json): {sorted(list(data[0].keys()))}\n")
                log.write(f"FIRST ITEM JSON (2000 chars): {json.dumps(data[0], ensure_ascii=False)[:2000]}\n")
            elif isinstance(data, dict):
                log.write(f"TYPE dict KEYS: {sorted(list(data.keys()))}\n")
                log.write(f"DATA 3000 chars: {json.dumps(data, ensure_ascii=False, indent=2)[:3000]}\n")
            else:
                log.write(f"TYPE {type(data).__name__}: {str(data)[:500]}\n")
        except Exception as e:
            log.write(f"=== {path} ERROR: {type(e).__name__}: {e}\n")
log.close()
