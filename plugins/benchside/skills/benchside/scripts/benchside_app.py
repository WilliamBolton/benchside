"""Bootstrap the packaged runtime and accept one structured request on stdin."""

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


def bootstrap():
    if sys.version_info < (3, 11):  # noqa: UP036 - this bootstrap runs before package installation.
        raise RuntimeError("Benchside needs Python 3.11 or later in this app")
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "runtime/manifest.json").read_text())
    wheel = root / "runtime" / manifest["wheel"]
    requirements = root / "runtime/requirements.txt"
    if hashlib.sha256(wheel.read_bytes()).hexdigest() != manifest["wheel_sha256"]:
        raise RuntimeError("Packaged runtime checksum does not match")
    if hashlib.sha256(requirements.read_bytes()).hexdigest() != manifest["requirements_sha256"]:
        raise RuntimeError("Dependency lock checksum does not match")
    dependencies = manifest.get("dependency_wheels")
    if not dependencies:
        raise RuntimeError("This package has no offline dependencies; install a rebuilt release")
    wheelhouse = root / "runtime/wheels"
    for name, digest in dependencies.items():
        if Path(name).name != name or not name.endswith(".whl"):
            raise RuntimeError("Invalid dependency wheel name")
        if hashlib.sha256((wheelhouse / name).read_bytes()).hexdigest() != digest:
            raise RuntimeError(f"Packaged dependency checksum does not match: {name}")
    identity = hashlib.sha256(
        (json.dumps(manifest, sort_keys=True) + sys.version).encode(),
    ).hexdigest()
    directory = Path(tempfile.gettempdir()) / f"benchside-runtime-{os.getuid()}" / identity
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    # First-use setup is isolated and locked. It never installs into the project.
    import fcntl

    with (directory / ".install.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        marker = directory / ".ready"
        if not marker.exists():
            if importlib.util.find_spec("pip"):
                installer = [sys.executable, "-m", "pip", "install", "--disable-pip-version-check"]
            elif shutil.which("uv"):
                installer = ["uv", "pip", "install", "--python", sys.executable]
            else:
                raise RuntimeError("The app needs pip or uv to install the bundled runtime")
            # Host installer settings must not add remote find-links or indexes.
            environment = {
                key: value
                for key, value in os.environ.items()
                if not key.startswith(("PIP_", "UV_")) or key == "UV_CACHE_DIR"
            }
            environment.update(
                PIP_CONFIG_FILE=os.devnull, UV_OFFLINE="true", UV_NO_CONFIG="true"
            )
            subprocess.run(
                installer
                + [
                    "--target", str(directory), "--no-index", "--no-deps",
                    "--find-links", str(wheelhouse), "--only-binary=:all:",
                    "--require-hashes", "-r", str(requirements),
                ],
                check=True,
                env=environment,
                stdout=sys.stderr,
                timeout=180,
            )
            with zipfile.ZipFile(wheel) as archive:
                for name in archive.namelist():
                    target = (directory / name).resolve()
                    if not target.is_relative_to(directory.resolve()):
                        raise RuntimeError("Unsafe runtime archive path")
                archive.extractall(directory)
            marker.write_text("ready\n")
    sys.path.insert(0, str(directory))


def main():
    try:
        request = json.load(sys.stdin)
        if not isinstance(request, dict) or not isinstance(request.get("action"), str):
            raise TypeError("Provide a JSON object with an action")
        bootstrap()
        from benchside.application.bridge import run

        result = run(request)
        print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
        return 0
    except Exception as error:  # noqa: BLE001 - the process boundary must return a JSON error.
        print(
            json.dumps(
                {"ok": False, "error": str(error), "code": getattr(error, "code", "setup_failed")}
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
