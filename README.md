# WILLIE

Jednoduchý “smart dashboard” ako statická web aplikácia (PWA).

## Spustenie

Najjednoduchšie je pustiť lokálny HTTP server v priečinku projektu.

### Python

```bash
python -m http.server 8000
```

Potom otvor `http://localhost:8000/`.

## Súbory

- `index.html`: štartovacia stránka (iframe wrapper)
- `app.html`: hlavná aplikácia (single-file)
- `sw.js`: service worker pre offline cache
- `manifest.webmanifest`: PWA manifest
- `tools/`: pomocné Python skripty (spracovanie assetov)

## Nástroje (Python)

Skripty v `tools/` používajú Pillow.

```bash
python -m pip install -r requirements.txt
```

## Licencia

MIT – pozri `LICENSE`.

