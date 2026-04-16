import subprocess
import sys
import os
import time

ROOT = os.path.dirname(os.path.abspath(__file__))

def ask(prompt, options):
    """Ask a numbered question and return the validated choice."""
    while True:
        choice = input(prompt).strip()
        if choice in options:
            return choice
        print(f"  Invalid choice. Please enter one of: {', '.join(options)}")

def main():
    print("=" * 44)
    print("        MedRAG System Launcher           ")
    print("=" * 44)

    # ── Collect all choices BEFORE starting anything ──
    print("\nWhich frontend platform would you like to run?")
    print("  1. Web Frontend  (React / Vite)")
    print("  2. Mobile App    (Flutter)")
    print("  3. Backend only")
    frontend_choice = ask("Enter 1, 2, or 3: ", ["1", "2", "3"])

    flutter_device = None
    if frontend_choice == "2":
        print("\nWhich device for Flutter?")
        print("  1. Windows (desktop)")
        print("  2. Chrome  (web)")
        print("  3. Edge    (web)")
        dev_choice = ask("Enter 1, 2, or 3: ", ["1", "2", "3"])
        flutter_device = {
            "1": "windows",
            "2": "chrome",
            "3": "edge",
        }[dev_choice]

    # ── Start Backend ──
    print("\n[1/2] Starting MedRAG Backend (FastAPI)…")
    # Auto-detect local venv to prevent global system module errors
    venv_python = os.path.join(ROOT, "venv", "Scripts", "python.exe")
    if not os.path.exists(venv_python):
        print("      ⚠️ Warning: No local 'venv' found. Falling back to global python...")
        venv_python = sys.executable

    backend = subprocess.Popen(
        f'"{venv_python}" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000',
        shell=True,
        cwd=ROOT,
    )
    print("      Backend starting on http://127.0.0.1:8000")
    time.sleep(4)  # Give it a moment to initialise

    # ── Start Frontend ──
    frontend = None
    if frontend_choice == "1":
        print("\n[2/2] Launching Web Frontend (npm run dev)…")
        frontend = subprocess.Popen(
            "npm run dev",
            shell=True,
            cwd=ROOT,
        )
    elif frontend_choice == "2":
        print(f"\n[2/2] Launching Flutter on {flutter_device}…")
        frontend = subprocess.Popen(
            f"flutter run -d {flutter_device}",
            shell=True,
            cwd=os.path.join(ROOT, "mobile_app"),
        )

    print("\n" + "=" * 44)
    print("  All services running. Press Ctrl+C to stop.")
    print("=" * 44 + "\n")

    try:
        if frontend:
            frontend.wait()
        backend.wait()
    except KeyboardInterrupt:
        print("\n\nShutting down MedRAG services…")
        if frontend and frontend.poll() is None:
            frontend.terminate()
        if backend.poll() is None:
            backend.terminate()
        # Give processes a moment to exit
        time.sleep(1)
        sys.exit(0)

if __name__ == "__main__":
    main()
