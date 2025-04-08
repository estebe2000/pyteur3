#!/bin/sh

# Lancer Ollama en mode arrière-plan
echo "Starting Ollama server temporarily in background mode..."
ollama serve --host 0.0.0.0 &

OLLAMA_PID=$!
echo "Waiting for Ollama server to initialize..."
sleep 10

# Vérifier si Ollama est bien lancé
if curl -s http://localhost:11434 > /dev/null; then
    echo "Ollama server started successfully, downloading model..."
    
    # Télécharger le modèle `qwen2.5-coder:0.5b`
    ollama pull qwen2.5-coder:0.5b
    
    echo "Model downloaded. Stopping background Ollama process..."
    kill $OLLAMA_PID
    
    sleep 5
    echo "Starting Ollama server in foreground mode..."
    
    # Relancer Ollama en mode premier plan
    exec ollama serve --host 0.0.0.0
else
    echo "Failed to start Ollama server in background mode. Starting in foreground mode..."
    kill $OLLAMA_PID
    exec ollama serve --host 0.0.0.0
fi
