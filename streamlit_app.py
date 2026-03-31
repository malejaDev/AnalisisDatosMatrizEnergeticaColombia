"""
Entrypoint recomendado para despliegues (Streamlit Community Cloud, etc.).

Mantener el archivo en la raíz evita problemas de importación cuando el script
se ejecuta desde un subdirectorio como `app/`.
"""

from app.main import main

if __name__ == "__main__":
    main()

