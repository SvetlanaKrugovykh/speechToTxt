import os
import ctypes

# Determine the correct library name based on the operating system
if os.name == "nt":
    libc_name = "msvcrt.dll"  # Use the common C runtime library on Windows
else:
    import ctypes.util
    libc_name = ctypes.util.find_library("c")  # Standard for Unix-like systems

# Print the determined library name for debugging
print(f"Using libc_name: {libc_name}")

# Load the library if the name is determined
if libc_name:
    try:
        libc = ctypes.CDLL(libc_name)
        print("Library loaded successfully.")
    except OSError as e:
        print(f"Failed to load the library: {e}")
else:
    raise ImportError("libc_name is None. Could not load the library.")

# Now import whisper after ensuring the necessary library is loaded
import whisper

print("Whisper package loaded successfully!")
