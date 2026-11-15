import numba
import shutil
import subprocess


from os         import environ, path
from enum       import Enum
from os.path    import dirname, abspath
from harmonize.python import errors, logging

class ShouldCompile(Enum):
    ALWAYS = 1
    NEVER  = 2


DEBUG   = False
VERBOSE = False
INTERNAL_DEBUG = False
ERROR_PRINT = True
COLOR_LOG = True

NONE_AVAILABLE = True
ROCM_AVAILABLE = None
CUDA_AVAILABLE = None
SHOULD_COMPILE = None


# The GPU platform is chosen once, at import. Set HARMONIZE_PLATFORM to "cuda"
# or "rocm" to require a platform; the default, "auto", prefers ROCm when its
# Numba backend is installed and falls back to CUDA.
PLATFORM_ENV_VAR = "HARMONIZE_PLATFORM"
PLATFORM_CHOICES = ("auto", "cuda", "rocm")
PLATFORM_REQUEST = environ.get(PLATFORM_ENV_VAR, "auto").strip().lower() or "auto"
if PLATFORM_REQUEST not in PLATFORM_CHOICES:
    raise ValueError(
        f"{PLATFORM_ENV_VAR}={PLATFORM_REQUEST!r} is not one of {PLATFORM_CHOICES}."
    )

# Why each Numba GPU backend could not be imported, for diagnostics
PLATFORM_IMPORT_ERRORS = {}


if PLATFORM_REQUEST in ("auto", "rocm"):
    try:
        import numba.hip as hip
        ROCM_AVAILABLE = True
        NONE_AVAILABLE = False
        logging.verbose_print(f"ROCM_PLATFORM detected. Proceeding under ROCM.")
    except ImportError as error:
        ROCM_AVAILABLE = False
        PLATFORM_IMPORT_ERRORS["rocm"] = str(error)
else:
    ROCM_AVAILABLE = False


# The HIP version of Numba "has" a cuda module,
# but doesn't support the things normal Numba does
if not ROCM_AVAILABLE and PLATFORM_REQUEST in ("auto", "cuda"):
    try :
        import numba.cuda as cuda
        CUDA_AVAILABLE = True
        NONE_AVAILABLE = False
        logging.verbose_print(f"CUDA_PLATFORM detected. Proceeding under CUDA.")
    except ImportError as error:
        CUDA_AVAILABLE = False
        PLATFORM_IMPORT_ERRORS["cuda"] = str(error)
else:
    CUDA_AVAILABLE = False


def require_platform():
    """Raise a descriptive error if no GPU platform was selected at import.

    This is deferred to the point where GPU code is built, so harmonize can be
    imported (for example by `python -m harmonize check`) on machines without
    a usable GPU backend.
    """
    if NONE_AVAILABLE:
        errors.no_platforms(PLATFORM_REQUEST, PLATFORM_IMPORT_ERRORS)


def set_debug(debug):
    global DEBUG
    DEBUG = debug

def set_verbose(verbose):
    global VERBOSE
    VERBOSE = verbose

def set_internal_debug(internal_debug):
    global INTERNAL_DEBUG
    INTERNAL_DEBUG = internal_debug


class GPUPlatform(Enum):
    CUDA = 1
    ROCM = 2

CUDA_PATH  = None
ROCM_PATH  = None

HARMONIZE_ROOT_DIR    =  dirname(abspath(__file__))+"/.."
HARMONIZE_ROOT_HEADER = HARMONIZE_ROOT_DIR+"/cpp/harmonize.h"


def set_platform(platform):
    global GPU_PLATFORM
    GPU_PLATFORM = platform
    logging.verbose_print(f"GPU_PLATFORM set to {GPU_PLATFORM}")

def set_cuda_path(path):
    global CUDA_PATH
    CUDA_PATH = path
    if path == None:
        logging.verbose_print(f"CUDA_PATH cleared to default")
    else:
        logging.verbose_print(f"CUDA_PATH set to {CUDA_PATH}")

def set_rocm_path(path):
    global ROCM_PATH
    ROCM_PATH = path
    if path == None:
        logging.verbose_print(f"ROCM_PATH cleared to default")
    else:
        logging.verbose_print(f"ROCM_PATH set to {ROCM_PATH}")


def should_compile(mode):
    global SHOULD_COMPILE
    SHOULD_COMPILE = mode

def compilation_gate(auto):
    if   SHOULD_COMPILE == ShouldCompile.ALWAYS:
        return True
    elif SHOULD_COMPILE == ShouldCompile.NEVER:
        return False
    else:
        return auto


def check_rocm_path(quiet=False):

    dep_paths = [
        hipcc_path(),
        hipcc_clang_offload_bundler_path(),
        hipcc_llvm_link_path(),
        hipcc_llvm_as_path(),
    ]

    fail = False
    for dep in dep_paths:
        if not path.isfile(dep):
            if not quiet:
                logging.error_print(f"Path '{dep}' does not correspond to a file.")
            fail = True
    if fail and (not quiet):
        raise RuntimeError("Some required ROCM dependencies missing.")

    return not fail


def try_autoset_rocm_path():
    path = shutil.which("hipcc")
    if path is None:
        return

    tail = "/bin/hipcc"
    if not path.endswith(tail):
        return
    logging.verbose_print(f"Found hipcc located at '{path}'")

    path = path[:-len(tail)]
    set_rocm_path(path)
    if not check_rocm_path(quiet=True):
        set_rocm_path(None)

def nvcc_path():
    if CUDA_PATH == None:
        return "nvcc"
    else:
        return CUDA_PATH + "/bin/nvcc"

def hipcc_path():
    if ROCM_PATH == None:
        return "hipcc"
    else:
        return ROCM_PATH + "/bin/hipcc"

def hipcc_clang_offload_bundler_path():
    if ROCM_PATH == None:
        return "clang-offload-bundler"
    else:
        return ROCM_PATH + "/llvm/bin/clang-offload-bundler"

def hipcc_llvm_link_path():
    if ROCM_PATH == None:
        return "llvm-link"
    else:
        return ROCM_PATH + "/llvm/bin/llvm-link"

def hipcc_llvm_as_path():
    if ROCM_PATH == None:
        return "llvm-as"
    else:
        return ROCM_PATH + "/llvm/bin/llvm-as"


# Uses nvidia-smi to query the compute level of the GPUs on the system. This
# compute level is what is used for compling PTX.
def native_gpu_arch(platform):
    if platform == GPUPlatform.ROCM:
        return ""
    else:
        capability = cuda.get_current_device().compute_capability
        output = f"{capability[0]}{capability[1]}"
        return output

if ROCM_AVAILABLE:
    try_autoset_rocm_path()
