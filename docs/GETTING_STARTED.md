# ⚡ INSTALACIÓN SÚPER SIMPLE - 3 Pasos

## 🎯 Resumen: 5 minutos total

```
PASO 1: Instalar Python (2 min)
   ↓
PASO 2: Instalar anthropic (1 min)
   ↓
PASO 3: Ejecutar el demo (2 min)
   ↓
¡LISTO! 🎉
```

---

## 📝 PASO 1: Instalar Python

### ¿Ya lo tienes?

Abre tu terminal/cmd y escribe:

```bash
python --version
```

**Si ves:** `Python 3.9.x` o superior → ✅ **Ya lo tienes, salta a PASO 2**

**Si ves:** Error o versión menor → Instálalo:

---

### 🪟 Windows

1. Ve a: https://www.python.org/downloads/
2. Click "Download Python"
3. Ejecuta el instalador
4. ⚠️ **IMPORTANTE:** Marca "Add Python to PATH"
5. Click "Install Now"

---

### 🍎 Mac

Abre Terminal y escribe:

```bash
brew install python3
```

*(Si no tienes Homebrew, instálalo primero desde https://brew.sh)*

---

### 🐧 Linux

```bash
sudo apt install python3 python3-pip
```

---

## 📦 PASO 2: Instalar anthropic

En tu terminal/cmd:

```bash
pip install anthropic
```

Espera 10 segundos... ✅ Listo

---

## 🚀 PASO 3: Ejecutar el Demo

### 1. Descarga los archivos

Todos los archivos de Claude están en tus descargas. Busca `bot_factory_poc.py`

### 2. Abre terminal en esa carpeta

**Windows:**
- Navega a la carpeta en Explorador
- Click derecho → "Abrir en Terminal"

**Mac:**
- Abre Terminal
- Escribe: `cd ` (con espacio)
- Arrastra la carpeta al Terminal
- Enter

**Linux:**
- Click derecho en carpeta → "Abrir Terminal aquí"

### 3. Ejecuta:

```bash
python bot_factory_poc.py
```

¿Ves texto corriendo y bots trabajando? 

**✅ ¡FUNCIONÓ!**

---

## 🎬 Comandos Completos (Copia-Pega)

### Windows (PowerShell):

```powershell
# Verificar Python
python --version

# Instalar anthropic
pip install anthropic

# Ir a carpeta (ajusta la ruta)
cd C:\Users\TuUsuario\Downloads\bot-factory

# Ejecutar
python bot_factory_poc.py
```

---

### Mac (Terminal):

```bash
# Verificar Python
python3 --version

# Instalar anthropic
pip3 install anthropic

# Ir a carpeta (ajusta la ruta)
cd ~/Downloads/bot-factory

# Ejecutar
python3 bot_factory_poc.py
```

---

### Linux (Terminal):

```bash
# Verificar Python
python3 --version

# Instalar anthropic
pip3 install anthropic

# Ir a carpeta (ajusta la ruta)
cd ~/Downloads/bot-factory

# Ejecutar
python3 bot_factory_poc.py
```

---

## ❌ Si Algo Falla

### Error: "python no reconocido"

**Solución:** Usa `python3` en lugar de `python`

```bash
python3 bot_factory_poc.py
```

---

### Error: "No module named anthropic"

**Solución:**

```bash
pip3 install anthropic
```

---

### Error: "Permission denied"

**Solución (Mac/Linux):**

```bash
chmod +x bot_factory_poc.py
python3 bot_factory_poc.py
```

---

## ✅ ¿Funcionó?

Si ves esto en tu terminal:

```
████████████████████████████████████████████████
█                                              █
█         BOT FACTORY - Proof of Concept      █
█                                              █
████████████████████████████████████████████████

🏭 BOT FACTORY - Construyendo: Project Management SaaS

📋 FASE 1: Análisis y Generación de Bots
   ✅ Equipo generado: 8 bots especializados
```

**✅ ¡ÉXITO! Ya tienes Bot Factory corriendo**

---

## 📚 Próximo Paso

Lee el plan de acción:

```bash
cat PLAN_ACCION_INMEDIATO.md
```

(O ábrelo con cualquier editor de texto)

---

## 🆘 Ayuda Rápida

**¿Necesitas ayuda?**

Responde con:
- Tu sistema operativo (Windows/Mac/Linux)
- El error exacto que ves
- Resultado de: `python --version`

Y te ayudo específicamente.

---

**¡Es así de simple!** 🚀

3 pasos, 5 minutos, listo para revolucionar el desarrollo de software.
