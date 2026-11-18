# Python API

Everything below is available directly from the `harmonize` package
(`import harmonize`).

```{eval-rst}
.. module:: harmonize

Programs
--------

.. autoclass:: harmonize.RuntimeSpec
   :members:

Arrays and memory
-----------------

.. autofunction:: harmonize.local_array
.. autofunction:: harmonize.array_from_ptr
.. autofunction:: harmonize.alloc_device_bytes
.. autofunction:: harmonize.alloc_managed_bytes
.. autofunction:: harmonize.free_device_bytes
.. autofunction:: harmonize.memcpy_host_to_device
.. autofunction:: harmonize.memcpy_device_to_host

Atomics
-------

.. autofunction:: harmonize.array_atomic_add
.. autofunction:: harmonize.array_atomic_max

Output and timing
-----------------

.. autofunction:: harmonize.print_formatted
.. autofunction:: harmonize.get_wall_clock

C++ headers
-----------

.. autofunction:: harmonize.get_include

Configuration: ``harmonize.config``
-----------------------------------

.. automodule:: harmonize.config
   :members: require_platform, set_platform, set_cuda_path, set_rocm_path,
             set_debug, set_verbose, set_internal_debug

Pointers: ``harmonize.pointer``
-------------------------------

.. automodule:: harmonize.pointer
   :members:
   :undoc-members:
```
