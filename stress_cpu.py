# This script will max out a single CPU core by running an infinite, empty loop.
# It's a simple and effective way to test high CPU load scenarios.
# To stop it, simply press Ctrl+C in the terminal where it's running.

print("Starting CPU stress test...")
print("This will use 100% of one CPU core.")
print("Press Ctrl+C to stop.")

try:
    while True:
        pass
except KeyboardInterrupt:
    print("\nCPU stress test stopped.")
