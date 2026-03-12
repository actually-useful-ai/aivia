import os
import subprocess

def find_virtual_envs(start_path='/'):
    virtual_envs = []
    for root, dirs, files in os.walk(start_path):
        # Look for typical virtual environment folders or activation scripts
        if 'bin' in dirs and 'activate' in os.listdir(os.path.join(root, 'bin')):
            virtual_envs.append(root)
        elif 'Scripts' in dirs and 'activate' in os.listdir(os.path.join(root, 'Scripts')):  # For Windows
            virtual_envs.append(root)
    return virtual_envs

def check_virtual_env(env_path):
    activate_script = os.path.join(env_path, 'bin', 'activate') if os.name != 'nt' else os.path.join(env_path, 'Scripts', 'activate')
    if os.path.exists(activate_script):
        # Check if the environment works by running a basic Python command
        result = subprocess.run(
            f"source {activate_script} && python -c 'import sys; print(sys.executable)'",
            shell=True, capture_output=True, text=True, executable='/bin/bash'  # Use bash for non-Windows
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    else:
        return False, "Activation script not found"

if __name__ == "__main__":
    start_path = "/"  # Set to root or a more specific directory
    print(f"Searching for virtual environments starting at: {start_path}")
    virtual_envs = find_virtual_envs(start_path)
    
    if not virtual_envs:
        print("No virtual environments found.")
    else:
        for env in virtual_envs:
            is_working, message = check_virtual_env(env)
            status = "Working" if is_working else "Broken"
            print(f"Environment found at: {env} - Status: {status}")
            print(f"Message: {message}")
            print("-" * 40)