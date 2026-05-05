#!/bin/bash

# Path: run.sh
# Script para iniciar el bot en segundo plano

APP_DIR="/home/agustin/proyectos_software/telegram-gemini-cli"
LOG_DIR="$APP_DIR/storage/logs"
PID_FILE="$APP_DIR/storage/bot.pid"
VENV_PATH="$APP_DIR/venv/bin/activate"

# Asegurar que el directorio de logs existe
mkdir -p "$LOG_DIR"

# Verificar si ya está corriendo
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null; then
        echo "⚠️ El bot ya está corriendo (PID: $PID)."
        exit 1
    else
        rm "$PID_FILE"
    fi
fi

# Activar entorno virtual e iniciar
echo "🚀 Iniciando Telegram Gemini CLI en segundo plano..."
source "$VENV_PATH"

# Ejecutar con nohup para que persista tras cerrar la terminal
# Redirigir stdout y stderr al log
nohup python3 main.py > "$LOG_DIR/bot.log" 2>&1 &

# Guardar PID
PID=$!
echo $PID > "$PID_FILE"

# 'disown' asegura que el proceso se desvincule totalmente de la sesión de la terminal actual
disown $PID

echo "✅ Bot lanzado con PID: $PID"
echo "------------------------------------------------"
echo "🔍 Verificando arranque (esperando 3s)..."
sleep 3

if ps -p $PID > /dev/null; then
    echo "🟢 El bot parece estar corriendo correctamente."
    echo "📋 Últimas líneas del log:"
    tail -n 5 "$LOG_DIR/bot.log"
else
    echo "🔴 ERROR: El bot se detuvo inmediatamente. Revisá el log en $LOG_DIR/bot.log"
fi

echo "------------------------------------------------"
echo "💡 Podés cerrar esta ventana. El bot seguirá en 2do plano."
echo "Presioná ENTER para salir de esta ventana..."
read
