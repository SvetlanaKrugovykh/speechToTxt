import ctypes
import os

print("Determining libc_name...")

if os.name == "nt":
    libc_name = "msvcrt.dll"  # Common C runtime library on Windows
else:
    try:
        import ctypes.util
        libc_name = ctypes.util.find_library("c")
    except AttributeError:
        libc_name = None

print(f"libc_name: {libc_name}")

if libc_name:
    libc = ctypes.CDLL(libc_name)
    print("Successfully loaded the library.")
else:
    raise ImportError("Could not determine libc_name for your platform.")
