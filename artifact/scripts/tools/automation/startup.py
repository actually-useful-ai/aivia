import os
import subprocess

# Function to run a command and display output or error
def run_command(command):
    print(f"Running command: {command}")
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.stdout:
        print(f"Output: {result.stdout}")
    if result.stderr:
        print(f"Error: {result.stderr}")

# Unlock essential ports
# ports = [80, 4000, 4001, 5000, 8000, 8001, 8080]
# for port in ports:
#     run_command(f"sudo ufw allow {port}")

# Start services
# commands = [
#     "cd /home/one_impossible_thing && source venv/bin/activate && sudo python3 -m http.server 80",
      "cd /home/one_impossible_thing/local_web/drummer && source venv/bin/activate && python3 app.py",
#     "cd /home/one_impossible_thing && source venv/bin/activate && chainlit run app.py -h",
#     "cd /home/one_impossible_thing/copilots && source venv/bin/activate && chainlit run copilot.py --port 8001 -hw",
#     "cd /home/one_impossible_thing/local_web/ai && source venv/bin/activate && python3 api_regen.py",
#     "cd /home/one_impossible_thing/slp-get && source venv/bin/activate && uvicorn main:app --reload --port 8080",
# ]

# Pull latest changes from the Git repository
def update_from_git():
    try:
        subprocess.check_call(["git", "-C", "/home/coolhand/one_impossible_thing", "pull", "origin", "main"])
        print("Repository successfully updated.")
    except subprocess.CalledProcessError as e:
        print(f"Error updating repository: {e}")

# Set up Git credentials for authentication
def setup_git_credentials():
    try:
        subprocess.run(["git", "config", "--global", "credential.helper", "store"])
        print("Git credentials successfully set up.")
    except subprocess.CalledProcessError as e:
        print(f"Error setting up Git credentials: {e}")

# Run each command in the list of startup commands
 for cmd in commands:
     run_command(cmd)

# Dashboard function: display open ports, running services, and HTML files served
def create_dashboard():
    try:
        # Display open ports with firewall status
        open_ports = subprocess.check_output(["sudo", "ufw", "status", "numbered"]).decode()
        print("\nOpen Ports:\n", open_ports)
    except subprocess.CalledProcessError as e:
        print(f"Error checking open ports: {e}")

    try:
        # Get running services, sorted by CPU and RAM usage, with PID and port (if available)
        running_services = subprocess.check_output(["ps", "aux", "--sort=-%cpu,-%mem"]).decode().splitlines()
        print("\nRunning Services (Sorted by CPU and RAM):\n")
        for line in running_services[:10]:  # Display the top 10 processes
            print(line)
    except subprocess.CalledProcessError as e:
        print(f"Error checking running services: {e}")

    # Display HTML files available in the project directory
    html_files = [os.path.join(root, file) for root, _, files in os.walk("/home/coolhand/one_impossible_thing") for file in files if file.endswith(".html")]
    print("\nHTML Files Being Served:\n", "\n".join(html_files))

# Execute functions
update_from_git()
setup_git_credentials()
create_dashboard()