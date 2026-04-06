import subprocess
import sys
import os
import time

def main():
    print("====================================")
    print("      Starting MedRAG System        ")
    print("====================================")
    print("\n[1/2] Starting MedRAG Backend (FastAPI)...")
    
    # Using shell=True so we don't have to worry about .cmd extension mapping on Windows
    backend_process = subprocess.Popen(
        "uvicorn backend.main:app --reload",
        shell=True,
    )

    # Let the backend initialize
    time.sleep(3)
    
    print("\n" + "="*40)
    print("Which frontend platform would you like to run?")
    print("1. Web Frontend (React/Vite)")
    print("2. Mobile Frontend (Flutter)")
    print("====================================")
    
    choice = input("Enter 1 or 2: ").strip()
    
    frontend_process = None
    
    print("\n[2/2] Starting Frontend...")
    if choice == '1':
        print("-> Launching Web App via 'npm run dev' ...")
        frontend_process = subprocess.Popen(
            "npm run dev",
            shell=True
        )
    elif choice == '2':
        print("-> Launching Mobile App via 'flutter run' ...")
        frontend_process = subprocess.Popen(
            "flutter run",
            cwd="mobile_app",
            shell=True
        )
    else:
        print("Invalid choice, continuing with only backend running.")
        
    print("\n[System] All requested services are starting!")
    print("[System] Press Ctrl+C at any time to shut down the processes.")
    
    try:
        if frontend_process:
            frontend_process.wait()
        backend_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down MedRAG services...")
        backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        sys.exit(0)

if __name__ == "__main__":
    main()
