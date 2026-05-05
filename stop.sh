#!/bin/bash

# Path: stop.sh
# Script para detener el bot iniciado con run.sh

APP_DIR="/home/agustin/proyectos_software/telegram-gemini-cli"
PID_FILE="$APP_DIR/storage/bot.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    echo "🛑 Deteniendo bot (PID: $PID)..."
    kill $PID
    
    # Esperar un momento y verificar
    sleep 2
    if ps -p $PID > /dev/null; then
        echo "⚠️ No se detuvo, forzando kill -9..."
        kill -9 $PID
    fi
    
    rm "$PID_FILE"
    echo "✅ Bot detenido."
else
    echo "❌ No se encontró el archivo PID. ¿Está corriendo el bot?"
fi
