import numba

def no_platforms(request="auto", import_errors=None):
    message = "No GPU platforms (CUDA/ROCM) "
    if request != "auto":
        message += f"\nHARMONIZE_PLATFORM={request} was requested, but it is unavailable."
    for platform, reason in (import_errors or {}).items():
        message += f"\n  {platform}: {reason}"
    message += "\nRun `python -m harmonize check` for details."
    raise numba.errors.UnsupportedError(message)


