#!/usr/bin/env python3
"""
Script para cambiar entre modo simulado y real del LLM
"""

import os
import sys

def switch_mode(mode):
    """
    Cambiar entre modo simulado y real
    """
    env_file = ".env"
    
    # Leer archivo .env actual
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            lines = f.readlines()
    else:
        lines = []
    
    # Buscar y actualizar USE_MOCK_LLM
    mock_line_found = False
    for i, line in enumerate(lines):
        if line.startswith("USE_MOCK_LLM="):
            lines[i] = f"USE_MOCK_LLM={mode}\n"
            mock_line_found = True
            break
    
    # Si no se encontró, agregar la línea
    if not mock_line_found:
        lines.append(f"USE_MOCK_LLM={mode}\n")
    
    # Escribir archivo actualizado
    with open(env_file, 'w') as f:
        f.writelines(lines)
    
    print(f"✅ Modo cambiado a: {'SIMULADO' if mode == 'True' else 'REAL'}")

def show_current_mode():
    """
    Mostrar el modo actual
    """
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith("USE_MOCK_LLM="):
                    mode = line.strip().split("=")[1]
                    current_mode = "SIMULADO" if mode == "True" else "REAL"
                    print(f"🔄 Modo actual: {current_mode}")
                    return
    
    print("🔄 Modo actual: NO CONFIGURADO")

def show_usage():
    """
    Mostrar uso del script
    """
    print("""
🔄 Script para cambiar modo del LLM

Uso:
  python3 switch_mode.py [comando]

Comandos:
  simulado    - Activar modo simulado (sin costos)
  real        - Activar modo real (con OpenAI)
  status      - Mostrar modo actual
  help        - Mostrar esta ayuda

Ejemplos:
  python3 switch_mode.py simulado
  python3 switch_mode.py real
  python3 switch_mode.py status

Notas:
  - Modo simulado: Sin costos, respuestas predefinidas
  - Modo real: Usa OpenAI GPT, requiere API key válida
  - Después de cambiar, reinicia el servicio
""")

def main():
    """
    Función principal
    """
    if len(sys.argv) < 2:
        show_usage()
        return
    
    command = sys.argv[1].lower()
    
    if command == "simulado":
        switch_mode("True")
        print("💡 Para activar: reinicia el servicio con 'python3 main.py'")
    elif command == "real":
        switch_mode("False")
        print("💡 Para activar: reinicia el servicio con 'python3 main.py'")
    elif command == "status":
        show_current_mode()
    elif command == "help":
        show_usage()
    else:
        print(f"❌ Comando no reconocido: {command}")
        show_usage()

if __name__ == "__main__":
    main() 