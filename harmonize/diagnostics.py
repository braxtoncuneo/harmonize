"""Environment report (`python -m harmonize info`) and readiness checks
(`python -m harmonize check`) for Harmonize's GPU platforms.

Both commands share `collect_info`, which never raises: anything that cannot
be determined is recorded as None or as an error string.
"""

import os
import platform as host_platform
import re
import shutil
import subprocess
import sys
import tempfile
from importlib import metadata

from harmonize import config


NUMBA_HIP_REPOSITORY = "https://github.com/ROCm/numba-hip.git"

# CUDA major versions with a `harmonize[cudaNN]` install extra (pyproject.toml)
CUDA_EXTRAS = (12, 13)


# ======================================================================================
# Information gathering
# ======================================================================================


def package_version(name):
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def run_text(command):
    """Return a command's stdout, or None if it cannot be run."""
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=60, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout


def parse_version(text, pattern):
    """Extract a (major, minor) tuple using a regex with two groups."""
    if text is None:
        return None
    match = re.search(pattern, text)
    if match is None:
        return None
    return int(match.group(1)), int(match.group(2))


def format_version(version):
    if version is None:
        return "unknown"
    else:
        return ".".join(str(part) for part in version)


def selected_platform():
    if config.CUDA_AVAILABLE:
        return "cuda"
    if config.ROCM_AVAILABLE:
        return "rocm"
    return None


def detect_rocm_version(rocm_path):
    """Best-effort ROCm version from hipconfig or the install's version file."""
    version = parse_version(
        run_text([shutil.which("hipconfig") or "hipconfig", "--version"]),
        r"(\d+)\.(\d+)",
    )
    if version is not None:
        return version
    if rocm_path is not None:
        try:
            with open(os.path.join(rocm_path, ".info", "version")) as file:
                return parse_version(file.read(), r"(\d+)\.(\d+)")
        except OSError:
            pass
    return None


def detect_cuda_version(nvcc):
    """Best-effort CUDA version"""
    return parse_version(
        run_text([nvcc, "--version"]), r"release (\d+)\.(\d+)"
    )


def collect_cuda_info():
    info = {
        "cuda_path": config.CUDA_PATH,
        "nvcc": None,
        "nvcc_version": None,
        "nvcc_archs": [],
        "driver_version": None,
        "runtime_version": None,
        "devices": [],
        "device_error": None,
    }

    # Toolkit compiler used to build Harmonize's runtime
    nvcc = config.nvcc_path()
    info["nvcc"] = shutil.which(nvcc)
    if info["nvcc"] is not None:
        info["nvcc_version"] = detect_cuda_version(info["nvcc"])
        archs = run_text([info["nvcc"], "--list-gpu-code"]) or ""
        info["nvcc_archs"] = re.findall(r"sm_(\d+)", archs)

    # Driver and devices, through the selected Numba CUDA backend
    if config.CUDA_AVAILABLE:
        cuda = config.cuda
        try:
            from numba.cuda.cudadrv import driver

            info["driver_version"] = tuple(driver.driver.get_version())
        except Exception as error:
            info["device_error"] = str(error)
        try:
            info["runtime_version"] = tuple(cuda.runtime.get_version())
        except Exception:
            pass
        try:
            if cuda.is_available():
                for device in cuda.list_devices():
                    name = device.name
                    if isinstance(name, bytes):
                        name = name.decode()
                    major, minor = device.compute_capability
                    info["devices"].append(
                        {"id": device.id, "name": name, "arch": f"{major}{minor}"}
                    )
            elif info["device_error"] is None:
                info["device_error"] = "numba.cuda.is_available() returned False"
        except Exception as error:
            info["device_error"] = str(error)

    if info["nvcc"] is not None and info["devices"]:
        info["ptx_probe"] = probe_ptx_assembly(info["nvcc"], info["devices"][0]["arch"])
    else:
        info["ptx_probe"] = None
    return info


def probe_ptx_assembly(nvcc, arch):
    """Compile a trivial device function to PTX with Numba's NVVM, then assemble it
    with nvcc as Harmonize does. NVVM comes from Numba's CUDA packages, not from
    nvcc's toolkit, and libNVVM's own version number does not identify the PTX ISA
    it emits, so trying the round trip is the only reliable check."""
    probe = {"ptx_version": None, "ok": None, "error": None}
    try:
        from numba import cuda, float64

        ptx, _ = cuda.compile_ptx(
            lambda a: None,
            (float64[:],),
            device=True,
            cc=(int(arch[:-1]), int(arch[-1])),
        )
    except Exception as error:
        probe["error"] = f"Numba could not generate PTX: {error}"
        return probe
    match = re.search(r"^\.version\s+(\S+)", ptx, re.MULTILINE)
    probe["ptx_version"] = match.group(1) if match else None
    with tempfile.TemporaryDirectory() as tmp:
        source = os.path.join(tmp, "probe.ptx")
        with open(source, "w") as file:
            file.write(ptx)
        try:
            result = subprocess.run(
                [nvcc, "-dc", f"-arch=sm_{arch}", source, "-o", os.path.join(tmp, "probe.o")],
                capture_output=True,
                text=True,
                timeout=120,
            )
        except (OSError, subprocess.SubprocessError) as error:
            probe["error"] = str(error)
            return probe
    probe["ok"] = result.returncode == 0
    if not probe["ok"]:
        lines = (result.stderr or result.stdout).strip().splitlines()
        probe["error"] = lines[0] if lines else f"nvcc exited with {result.returncode}"
    return probe




def collect_rocm_info():
    hipcc = shutil.which(config.hipcc_path())
    rocm_path = config.ROCM_PATH
    if rocm_path is None and hipcc is not None:
        rocm_path = os.path.dirname(os.path.dirname(os.path.realpath(hipcc)))
    return {
        "rocm_path": config.ROCM_PATH,
        "hipcc": hipcc,
        "rocm_version": detect_rocm_version(rocm_path),
        "tools_complete": config.ROCM_PATH is not None
        and config.check_rocm_path(quiet=True),
    }


def collect_info():
    return {
        "harmonize": {
            "version": package_version("harmonize-python"),
            "location": config.HARMONIZE_ROOT_DIR,
        },
        "host": {
            "python": sys.version.split()[0],
            "system": f"{host_platform.system()} {host_platform.machine()}",
        },
        "packages": {
            name: package_version(name)
            for name in (
                "numba",
                "numba-cuda",
                "numba-hip",
                "cuda-bindings",
                "nvidia-nvvm",
                "numpy",
            )
        },
        "platform": {
            "requested": config.PLATFORM_REQUEST,
            "selected": selected_platform(),
            "import_errors": dict(config.PLATFORM_IMPORT_ERRORS),
        },
        "cuda": collect_cuda_info(),
        "rocm": collect_rocm_info(),
    }


# ======================================================================================
# Readiness checks
# ======================================================================================


class Finding:
    def __init__(self, level, message, hint=None):
        self.level = level  # "error" or "warning"
        self.message = message
        self.hint = hint


def numba_hip_install_hint(rocm_version):
    if rocm_version is None:
        key = "rocm-<major>-<minor>-<patch>"
    else:
        key = f"rocm-{rocm_version[0]}-{rocm_version[1]}-<patch>"
    return (
        "Install AMD's Numba HIP backend for your ROCm release, e.g.\n"
        f'    pip install --extra-index-url https://test.pypi.org/simple "numba-hip[{key}] @ git+{NUMBA_HIP_REPOSITORY}"'
    )


def check_cuda(info, findings):
    cuda = info["cuda"]

    if cuda["device_error"] is not None or not cuda["devices"]:
        findings.append(
            Finding(
                "error",
                f"No usable CUDA device ({cuda['device_error'] or 'no devices found'}).",
                "Check the NVIDIA driver with `nvidia-smi`, and that this process can see a GPU "
                "(e.g. CUDA_VISIBLE_DEVICES, or a GPU allocation on a cluster).",
            )
        )

    if cuda["nvcc"] is None:
        findings.append(
            Finding(
                "error",
                f"nvcc was not found (looked for '{config.nvcc_path()}').",
                "Put a CUDA toolkit's bin directory on PATH (e.g. `module load cuda`, or "
                "`conda install -c nvidia cuda-nvcc`), or call harmonize.config.set_cuda_path().",
            )
        )
        return

    toolkit, driver = cuda["nvcc_version"], cuda["driver_version"]
    if toolkit is not None and driver is not None:
        if toolkit[0] > driver[0]:
            findings.append(
                Finding(
                    "error",
                    f"nvcc is CUDA {format_version(toolkit)}, but the driver only supports "
                    f"CUDA {format_version(driver)}.",
                    "Use a toolkit no newer than the driver, or update the driver.",
                )
            )
        elif toolkit > driver:
            findings.append(
                Finding(
                    "warning",
                    f"nvcc (CUDA {format_version(toolkit)}) is newer than the driver "
                    f"(CUDA {format_version(driver)}); this relies on minor-version compatibility.",
                )
            )

    bindings = info["packages"]["cuda-bindings"]
    if toolkit is not None and bindings is not None:
        if int(bindings.split(".")[0]) != toolkit[0]:
            if toolkit[0] in CUDA_EXTRAS:
                hint = f"Install the matching extra: `pip install harmonize[cuda{toolkit[0]}]`."
            else:
                hint = (
                    "Use a CUDA toolkit whose major version matches cuda-bindings "
                    f"(supported extras: {', '.join(f'cuda{v}' for v in CUDA_EXTRAS)})."
                )
            findings.append(
                Finding(
                    "warning",
                    f"cuda-bindings {bindings} (used by numba-cuda) and nvcc "
                    f"(CUDA {format_version(toolkit)}) are from different major CUDA versions.",
                    hint,
                )
            )

    probe = cuda.get("ptx_probe")
    if probe is not None and not probe["ok"]:
        if probe["ptx_version"] is not None:
            nvvm = info["packages"].get("nvidia-nvvm")
            source = f" (pip package nvidia-nvvm {nvvm})" if nvvm else ""
            message = (
                f"Numba's NVVM{source} emits PTX ISA {probe['ptx_version']}, which nvcc "
                f"(CUDA {format_version(toolkit)}) cannot assemble: {probe['error']}"
            )
            hint = (
                "Match Numba's NVVM to nvcc, e.g. "
                f"`pip install \"cuda-toolkit[nvvm,nvjitlink]=={format_version(toolkit)}.*\"`, "
                "or use an nvcc at least as new as NVVM (and no newer than the driver)."
            )
        else:
            message = f"Could not test PTX assembly with nvcc: {probe['error']}"
            hint = None
        findings.append(Finding("error", message, hint))

    supported = set(cuda["nvcc_archs"])
    for device in cuda["devices"]:
        if supported and device["arch"] not in supported:
            findings.append(
                Finding(
                    "error",
                    f"nvcc (CUDA {format_version(toolkit)}) cannot compile for device "
                    f"{device['id']} ({device['name']}, sm_{device['arch']}).",
                    "Use a newer CUDA toolkit that supports this GPU architecture.",
                )
            )


def check_rocm(info, findings):
    rocm = info["rocm"]
    if rocm["hipcc"] is None and config.ROCM_PATH is None:
        findings.append(
            Finding(
                "error",
                "hipcc was not found.",
                "Put ROCm's bin directory on PATH (e.g. `module load rocm`), or call "
                "harmonize.config.set_rocm_path().",
            )
        )
    elif not rocm["tools_complete"]:
        findings.append(
            Finding(
                "error",
                "The ROCm install is missing tools Harmonize needs "
                "(hipcc, clang-offload-bundler, llvm-link, llvm-as).",
                "Point harmonize.config.set_rocm_path() at a complete ROCm install.",
            )
        )


def run_checks(info):
    findings = []
    selected = info["platform"]["selected"]
    requested = info["platform"]["requested"]

    if selected is None:
        if requested == "rocm":
            hint = numba_hip_install_hint(info["rocm"]["rocm_version"])
        elif requested == "cuda":
            hint = "Install the CUDA backend: `pip install harmonize[cuda12]` or `harmonize[cuda13]`."
        else:
            hint = (
                "For NVIDIA GPUs: `pip install harmonize[cuda12]` or `harmonize[cuda13]`.\n"
                + numba_hip_install_hint(info["rocm"]["rocm_version"])
            )
        reasons = "; ".join(
            f"{name}: {reason}" for name, reason in info["platform"]["import_errors"].items()
        )
        findings.append(
            Finding(
                "error",
                f"No GPU platform is available (HARMONIZE_PLATFORM={requested}). {reasons}",
                hint,
            )
        )
        return findings

    if selected == "cuda":
        check_cuda(info, findings)
    else:
        check_rocm(info, findings)
    return findings


# ======================================================================================
# Report formatting
# ======================================================================================


def format_info(info):
    lines = []

    def section(title):
        lines.append("")
        lines.append(title)

    def item(label, value):
        lines.append(f"  {label:<22}{'not found' if value is None else value}")

    section("Harmonize")
    item("version", info["harmonize"]["version"])
    item("location", os.path.realpath(info["harmonize"]["location"]))
    item("python", info["host"]["python"])
    item("system", info["host"]["system"])

    section("Packages")
    for name, version in info["packages"].items():
        item(name, version)

    section("Platform")
    item("requested", f"{info['platform']['requested']} ({config.PLATFORM_ENV_VAR})")
    item("selected", info["platform"]["selected"] or "none")
    for name, reason in info["platform"]["import_errors"].items():
        item(f"{name} unavailable", reason)

    cuda = info["cuda"]
    section("CUDA")
    item("nvcc", cuda["nvcc"])
    if cuda["nvcc"] is not None:
        item("nvcc version", format_version(cuda["nvcc_version"]))
    if info["platform"]["selected"] == "cuda":
        item("driver supports", format_version(cuda["driver_version"]))
        item("runtime version", format_version(cuda["runtime_version"]))
        for device in cuda["devices"]:
            item(f"device {device['id']}", f"{device['name']} (sm_{device['arch']})")
        probe = cuda.get("ptx_probe")
        if probe is not None:
            status = "ok" if probe["ok"] else f"FAILED ({probe['error']})"
            item("numba PTX -> nvcc", f"PTX ISA {probe['ptx_version']}: {status}")
        if cuda["device_error"] is not None:
            item("device error", cuda["device_error"])

    rocm = info["rocm"]
    section("ROCm")
    item("hipcc", rocm["hipcc"])
    item("ROCm version", format_version(rocm["rocm_version"]) if rocm["hipcc"] else None)
    if config.ROCM_PATH is not None:
        item("ROCm path", config.ROCM_PATH)

    return "\n".join(lines[1:])


def format_findings(findings):
    if not findings:
        return "OK: Harmonize is ready to build GPU programs."
    lines = []
    for finding in findings:
        lines.append(f"{finding.level.upper()}: {finding.message}")
        if finding.hint:
            for hint_line in finding.hint.splitlines():
                lines.append(f"    {hint_line}")
    errors = sum(finding.level == "error" for finding in findings)
    warnings = len(findings) - errors
    lines.append(f"\n{errors} error(s), {warnings} warning(s).")
    return "\n".join(lines)
