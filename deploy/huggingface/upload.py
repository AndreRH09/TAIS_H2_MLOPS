"""Sube el bundle al Space de Hugging Face (lo crea si no existe).

Variables de entorno:
  HF_TOKEN  token de Hugging Face con permiso de escritura (Settings → Access Tokens)
  HF_SPACE  identificador del Space, p. ej. "tu-usuario/msft-mlops"

Uso:  uv run --no-project --with huggingface_hub python deploy/huggingface/upload.py space_bundle
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from huggingface_hub import HfApi


def main() -> int:
    folder = Path(sys.argv[1] if len(sys.argv) > 1 else "space_bundle")
    token, space = os.environ.get("HF_TOKEN"), os.environ.get("HF_SPACE")
    if not token or not space:
        print("Define HF_TOKEN y HF_SPACE (p. ej. tu-usuario/msft-mlops).", file=sys.stderr)
        return 2
    if not (folder / "Dockerfile").exists():
        print(f"{folder} no parece un bundle: ejecuta antes build_bundle.py", file=sys.stderr)
        return 2
    api = HfApi(token=token)
    api.create_repo(space, repo_type="space", space_sdk="docker", exist_ok=True)
    sha = os.environ.get("GITHUB_SHA", "")[:7] or "manual"
    info = api.upload_folder(
        folder_path=str(folder),
        repo_id=space,
        repo_type="space",
        commit_message=f"Despliegue {sha}",
        delete_patterns=["*"],  # sincroniza: borra del Space lo que ya no está en el bundle
    )
    print(f"Subido: {info.commit_url}")
    print(f"App: https://huggingface.co/spaces/{space}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
