# Conway's Game of Life

Simulador de escritorio del clásico Juego de la Vida de Conway con interfaz gráfica moderna, controles de zoom, navegación por paneles y funcionalidad completa de guardado/carga de plantillas en formato JSON.

## Características principales

- Interfaz gráfica intuitiva desarrollada en PyQt6
- Controles de reproducción, pausa y paso a paso
- Zoom y navegación fluida por el tablero
- Guardado y carga de patrones en formato JSON
- Empaquetado como ejecutable independiente

## Licencia

Este software es **software libre** distribuido bajo licencia que permite su libre distribución y uso personal, pero **prohíbe expresamente su comercialización por terceros**. Únicamente el autor original conserva los derechos de comercialización.

## Requisitos del sistema

- Python 3.8 o superior
- Sistema operativo: Windows, macOS o Linux
- Git (para clonar el repositorio)

## Instalación y configuración

### 1. Obtener el código fuente

```bash
git clone <URL_DEL_REPOSITORIO>
cd conways-game-of-life
```

### 2. Configurar entorno virtual

**Windows (PowerShell):**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## Uso

### Ejecutar en modo desarrollo

```bash
python src/main.py
```

### Formato de plantillas JSON

Las plantillas utilizan la siguiente estructura:

```json
{
  "width": 50,
  "height": 50,
  "alive": [
    [10, 15],
    [11, 15],
    [12, 15]
  ]
}
```

- `width` y `height`: Dimensiones del tablero
- `alive`: Array de coordenadas [x, y] de células vivas
- Las coordenadas deben estar dentro de los límites del tablero

## Distribución

### Generar ejecutable (Windows)

```bash
pyinstaller --onefile --windowed ^
  --name "Conways_Game_of_Life" ^
  --icon=assets/app/app.ico ^
  --add-data "assets/icons;assets/icons" ^
  src/main.py
```

### Generar ejecutable (macOS/Linux)

```bash
pyinstaller --onefile --windowed \
  --name "Conways_Game_of_Life" \
  --icon=assets/app/app.ico \
  --add-data "assets/icons:assets/icons" \
  src/main.py
```

**Nota:** El separador en `--add-data` varía según el sistema: `;` para Windows, `:` para macOS/Linux.

## Solución de problemas

### Iconos SVG no aparecen

- Asegúrese de importar `PyQt6.QtSvg` en el código principal
- Verifique que las opciones `--collect-*` estén incluidas en el comando de empaquetado

### Ejecutable no encuentra recursos

- Confirme que el separador en `--add-data` sea correcto para su sistema operativo
- Verifique que las rutas de los assets sean relativas al directorio del proyecto

### Error de permisos en Windows

- Ejecute PowerShell como administrador al crear el entorno virtual
- Configure la política de ejecución: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

## Contribuciones

Las contribuciones son bienvenidas siguiendo las pautas de la licencia. Para reportar bugs o solicitar características, utilice el sistema de issues del repositorio.

---

_Desarrollado con Python y PyQt6 | © 2024 - Software libre con restricciones comerciales_
