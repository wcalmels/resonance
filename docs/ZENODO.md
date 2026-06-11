# Archivar en Zenodo (DOI permanente)

Zenodo genera un DOI al archivar cada **GitHub Release**. Este repositorio incluye `.zenodo.json` para metadatos automáticos.

## Paso 1 — Conectar GitHub (una sola vez)

1. Inicia sesión en [zenodo.org](https://zenodo.org) (usa cuenta GitHub si prefieres).
2. Ve a **Account → GitHub** (o directo: https://zenodo.org/account/settings/github/ ).
3. Pulsa **Sync** para ver tus repositorios.
4. Activa el interruptor junto a **`wcalmels/resonance`**.

## Paso 2 — Release en GitHub

Ya existe el release **v0.2.0** en:

https://github.com/wcalmels/resonance/releases/tag/v0.2.0

Si Zenodo estaba conectado **antes** del release, el archivo se crea en minutos. Si conectaste **después**, crea un release nuevo (p. ej. v0.2.1) o en Zenodo usa **Re-sync** en el repositorio.

## Paso 3 — Obtener el DOI

1. En Zenodo: **Uploads** → busca "Resonance".
2. Copia el DOI (formato `10.5281/zenodo.XXXXXXX`).
3. Actualiza `CITATION.cff`:

```yaml
preferred-citation:
  doi: 10.5281/zenodo.XXXXXXX   # reemplazar con DOI real
```

4. Actualiza el badge en `README.md`:

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
```

5. Commit y push los cambios.

## Verificación

- Registro Zenodo: `https://doi.org/10.5281/zenodo.XXXXXXX`
- GitHub muestra el DOI en la release si Zenodo comentó o si lo añades manualmente a las release notes.

## Citar el software

```bibtex
@software{resonance2026,
  author    = {Calmels, W. and {Resonance Contributors}},
  title     = {Resonance: Task-Specialized LLM Orchestration with Minimal Context},
  year      = {2026},
  version   = {0.2.0},
  doi       = {10.5281/zenodo.XXXXXXX},
  url       = {https://github.com/wcalmels/resonance}
}
```

## Problemas frecuentes

| Problema | Solución |
|----------|----------|
| No aparece en Zenodo | Verifica que el repo esté activado en GitHub settings de Zenodo |
| Release sin archivo | Crea un nuevo tag/release después de activar Zenodo |
| DOI diferente por versión | Normal: cada release tiene su propio DOI; usa *concept DOI* para citar siempre la última versión |
