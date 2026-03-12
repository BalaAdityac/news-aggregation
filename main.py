import os
import subprocess
import sys

def main():
    # Make sure we are in the script's directory (the root)
    root_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(root_path)
    
    backend_path = os.path.join(root_path, "Backend")
    if not os.path.exists(backend_path):
        print(f"Error: Backend directory not found at {backend_path}")
        sys.exit(1)
    
    os.chdir(backend_path)
    
    # Check if we should start mongo via docker
    # In a production/integrated setup, we might want to check if mongo is running
    # but for now, we'll just try to start the backend.
    
    python_exe = sys.executable
    # Running uvicorn as a module
    cmd = [python_exe, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    
    print(f"Starting News Aggregation Backend from {backend_path}...")
    print(f"Endpoint: http://localhost:8000")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nStopping backend...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting backend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
