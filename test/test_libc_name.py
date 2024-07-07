import ctypes
import os

print("Determining libc_name...")

try:
    if os.name == "nt":
        # For Windows, use a common C runtime library
        libc_name = "msvcrt.dll"
    else:
        # For Unix-like systems, find the C standard library
        import ctypes.util
        libc_name = ctypes.util.find_library("c")

    print(f"libc_name: {libc_name}")

    if libc_name:
        libc = ctypes.CDLL(libc_name)
        print("Successfully loaded the library.")
    else:
        raise ImportError("Could not determine libc_name for your platform.")
except Exception as e:
    print(f"Error: {e}")
