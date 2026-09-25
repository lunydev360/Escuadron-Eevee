# Bot de Discord con cogs

Base de un bot de Discord usando `discord.py` y carga automática de cogs.

## Requisitos

- Python 3.10 o superior
- Un bot creado en el [Discord Developer Portal](https://discord.com/developers/applications)

## Instalación

En PowerShell, desde esta carpeta:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edita `.env` y reemplaza `DISCORD_TOKEN` por el token de tu bot.

En el Developer Portal, activa **Message Content Intent** en `Bot > Privileged Gateway Intents`.

## Ejecutar

```powershell
py bot.py
```

## Comandos incluidos

- `!ping`: muestra la latencia del bot.
- `!hola`: saluda al usuario.
- `!help`: muestra la ayuda generada por `discord.py`.

## Añadir un cog

Crea un archivo `.py` dentro de `cogs/` con una función `async def setup(bot)`. El bot lo cargará automáticamente al iniciar.
