"""A small Harmonize program that counts Collatz steps on the GPU.

    python collatz.py {event,async}

Builds the program, runs it in the given mode, and checks every result against
a CPU reference. Run it in an empty directory: Harmonize writes its build cache
to __harmonize_cache__/ in the working directory.

Numba must see the functions below as module-level Python functions, so the
program lives in its own file and the tests run it in a subprocess.
"""

import sys

import numba
import numpy as np
from numba import njit

import harmonize as harm

MODE = sys.argv[1]
assert MODE in ("event", "async"), sys.argv

VALUE_COUNT = 4096
STEPS_PER_MAKE_WORK = 4

dev_state_type = numba.from_dtype(
    np.dtype([("next", np.dtype((np.uintp, 1))), ("steps", np.dtype((np.uintp, VALUE_COUNT)))])
)
grp_state_type = numba.from_dtype(np.dtype([]))
thd_state_type = numba.from_dtype(np.dtype([]))
state_spec = (dev_state_type, grp_state_type, thd_state_type)

iter_type = numba.from_dtype(
    np.dtype([("value", np.int64), ("start", np.int64), ("steps", np.int64)])
)


def even(prog: numba.uintp, it: iter_type):
    if it["value"] <= 1:
        device(prog)["steps"][it["start"]] = it["steps"]
    else:
        it["steps"] += 1
        it["value"] //= 2
        if it["value"] % 2 == 0:
            even_async(prog, it)
        else:
            odd_async(prog, it)


def odd(prog: numba.uintp, it: iter_type):
    if it["value"] <= 1:
        device(prog)["steps"][it["start"]] = it["steps"]
    else:
        it["steps"] += 1
        it["value"] = it["value"] * 3 + 1
        if it["value"] % 2 == 0:
            even_async(prog, it)
        else:
            odd_async(prog, it)


def initialize(prog: numba.uintp):
    pass


def finalize(prog: numba.uintp):
    pass


def make_work(prog: numba.uintp) -> numba.boolean:
    first = harm.array_atomic_add(device(prog)["next"], 0, STEPS_PER_MAKE_WORK)
    if first >= VALUE_COUNT:
        return False
    it = harm.local_array(1, iter_type)
    value = first
    while value < VALUE_COUNT and value < first + STEPS_PER_MAKE_WORK:
        it[0]["value"] = value
        it[0]["start"] = value
        it[0]["steps"] = 0
        if value % 2 == 0:
            even_async(prog, it[0])
        else:
            odd_async(prog, it[0])
        value += 1
    return True


access = harm.RuntimeSpec.access_fns(state_spec)
device = access["device"]
odd_async, even_async = harm.RuntimeSpec.async_dispatch(odd, even)

spec = harm.RuntimeSpec(
    "collatz", state_spec, (initialize, finalize, make_work), [odd, even]
)
harm.RuntimeSpec.bind_specs()
harm.RuntimeSpec.load_specs()

fns = spec.event_functions() if MODE == "event" else spec.async_functions()
alloc_state = fns["alloc_state"]
free_state = fns["free_state"]
alloc_program = fns["alloc_program"]
free_program = fns["free_program"]
store_state = fns["store_state_device"]
load_state = fns["load_state_device"]
init_program = fns["init_program"]
exec_program = fns["exec_program"]
complete = fns["complete"]

# Event mode: the size of each IO buffer. Async mode: the arena size.
PROGRAM_SIZE = 0x10000 if MODE == "event" else 0x1000
GRID_SIZE = 256
# Event mode: work items per thread per pass. Async mode: cycles per launch.
EXEC_CHUNK = 1 if MODE == "event" else 0x10000


@njit
def run_on_gpu(state):
    gpu_state = alloc_state()
    program = alloc_program(gpu_state, PROGRAM_SIZE)
    store_state(gpu_state, state)
    init_program(program, GRID_SIZE)
    exec_program(program, GRID_SIZE, EXEC_CHUNK)
    while not complete(program):
        exec_program(program, GRID_SIZE, EXEC_CHUNK)
    load_state(state, gpu_state)
    free_program(program)
    free_state(gpu_state)


@njit
def reference_steps(value):
    steps = 0
    while value > 1:
        steps += 1
        if value % 2 == 0:
            value //= 2
        else:
            value = value * 3 + 1
    return steps


state = np.zeros((1,), dev_state_type)
run_on_gpu(state[0])
wrong = [
    value
    for value in range(VALUE_COUNT)
    if state[0]["steps"][value] != reference_steps(value)
]
if wrong:
    sys.exit(f"{len(wrong)} of {VALUE_COUNT} results are wrong, first at {wrong[:5]}")
print(f"collatz {MODE}: OK")
