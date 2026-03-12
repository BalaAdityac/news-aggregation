import subprocess
import sys
import os

def main():
    # Ensure we are in the directory of this script (Backend folder)
    backend_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_path)
    
    # Use the current python executable to run uvicorn
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "app.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload"
    ]
    
    print(f"Starting Backend from: {backend_path}")
    print("URL: http://localhost:8000")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nShutting down backend...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
