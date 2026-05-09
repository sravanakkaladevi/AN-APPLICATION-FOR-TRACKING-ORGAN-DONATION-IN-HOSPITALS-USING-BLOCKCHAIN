import os
import subprocess
import sys

def run_command(command, cwd=None):
    print(f"Running: {' '.join(command)}")
    try:
        subprocess.check_call(command, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        sys.exit(1)

def main():
    root_dir = os.getcwd()
    backend_dir = os.path.join(root_dir, "backend")
    contracts_dir = os.path.join(backend_dir, "contracts")
    
    print("--- Starting Full Project Setup ---")

    # 1. Install dependencies
    print("\n[1/5] Installing dependencies...")
    run_command([sys.executable, "-m", "pip", "install", "-r", os.path.join(backend_dir, "requirements.txt")])

    # 2. Database Migrations
    print("\n[2/5] Running migrations...")
    run_command([sys.executable, "manage.py", "makemigrations", "core"], cwd=backend_dir)
    run_command([sys.executable, "manage.py", "migrate"], cwd=backend_dir)

    # 3. Seed Hospitals
    print("\n[3/5] Seeding hospital data...")
    run_command([sys.executable, "scripts/seed_mca_hospitals.py"], cwd=backend_dir)

    # 4. Compile Smart Contract
    print("\n[4/5] Compiling Smart Contract...")
    run_command([sys.executable, "compile_contract.py"], cwd=contracts_dir)

    # 5. Deploy Smart Contract
    print("\n[5/5] Deploying Smart Contract to Ganache...")
    run_command([sys.executable, "deploy_contract.py"], cwd=contracts_dir)

    print("\n--- Setup Complete! ---")
    print("1. Ensure Ganache is running on http://127.0.0.1:7545")
    print("2. Run the server: cd backend && python manage.py runserver")

if __name__ == "__main__":
    main()
