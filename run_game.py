import subprocess
import sys
import time
import socket # To get local IP
import os

# --- Configuration ---
# Use sys.executable to ensure the correct Python interpreter is used (especially within venv)
PYTHON_EXECUTABLE = sys.executable
SCRIPT_DIR = os.path.join(os.path.dirname(__file__), 'src') # Path to the src directory

SERVER_SCRIPT = os.path.join(SCRIPT_DIR, 'server.py')
CLIENT_SCRIPT = os.path.join(SCRIPT_DIR, 'client.py')
AI_CLIENT_SCRIPT = os.path.join(SCRIPT_DIR, 'ai_client.py')

AI_LAUNCH_DELAY_SECONDS = 4 # Wait time after launching AI before launching human client

# --- Helper Function ---
def get_local_ip():
    """Gets the local IP address of the machine."""
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to an external host (doesn't send data) to find preferred outgoing IP
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        return ip
    except Exception as e:
        print(f"Could not determine local IP automatically: {e}")
        # Fallback attempt
        try:
            return socket.gethostbyname(socket.gethostname())
        except socket.gaierror:
             print("Fallback failed. Please find your IP manually (ipconfig/ifconfig).")
             return "?.?.?.?"
    finally:
        if s:
            s.close()

def print_menu():
    """Prints the main menu options."""
    print("\n--- Tic Tac Toe Menu ---")
    print("1. Play vs AI (Runs Server, AI Client, Human Client)")
    print("2. Host LAN Game (Starts Server only)")
    print("3. Join LAN Game (Connects as Human Client)")
    print("4. Quit")
    print("------------------------")

# --- Main Execution ---
if __name__ == "__main__":
    running_processes = [] # Keep track of started processes (optional basic tracking)

    while True:
        print_menu()
        choice = input("Enter your choice (1-4): ")

        try:
            choice_int = int(choice)

            if choice_int == 1:
                print("Starting Human vs AI game...")
                print("  - Starting Server...")
                server_proc = subprocess.Popen([PYTHON_EXECUTABLE, SERVER_SCRIPT])
                running_processes.append(server_proc)
                time.sleep(1) # Give server a moment to start

                print(f"  - Starting AI Client (will connect as X)...")
                ai_proc = subprocess.Popen([PYTHON_EXECUTABLE, AI_CLIENT_SCRIPT])
                running_processes.append(ai_proc)

                print(f"  - Waiting {AI_LAUNCH_DELAY_SECONDS}s for AI to load/connect...")
                time.sleep(AI_LAUNCH_DELAY_SECONDS)

                print("  - Starting Human Client (will connect as O)...")
                # Human client connects to localhost server started above
                human_proc = None  # Initialize variable
                try:
                    # *** Modify Popen to capture output/error ***
                    human_proc = subprocess.Popen(
                        [PYTHON_EXECUTABLE, CLIENT_SCRIPT, '--host', '127.0.0.1'],
                        stdout=subprocess.PIPE,  # Capture standard output
                        stderr=subprocess.PIPE,  # Capture standard error
                        text=True,  # Decode streams as text
                        bufsize=1,  # Line-buffered (optional, might help see output sooner)
                        universal_newlines=True  # Alias for text=True, line buffering
                    )
                    running_processes.append(human_proc)  # Add to list *if successful*

                    # *** Add check for early exit ***
                    print("     (Checking if Human Client started okay...)")
                    time.sleep(1.0)  # Wait 1 second
                    return_code = human_proc.poll()  # Check if process terminated (None if running)

                    if return_code is not None:
                        # Process terminated early! Print its output/error.
                        print(f"!!! FATAL: Human Client process terminated immediately with code {return_code} !!!")
                        # Use communicate() to get all output after termination
                        stdout, stderr = human_proc.communicate()
                        if stdout:
                            print("--- Human Client STDOUT ---")
                            print(stdout.strip())
                            print("---------------------------")
                        if stderr:
                            print("--- Human Client STDERR ---")
                            print(stderr.strip())
                            print("---------------------------")
                        # Stop trying to proceed with the game in this case
                        # You might want to add logic here to also terminate the server/AI processes if desired
                    else:
                        print("     (Human Client process seems to be running)")

                except FileNotFoundError:
                    print(f"!!! FATAL: Could not find script to run: {CLIENT_SCRIPT} using {PYTHON_EXECUTABLE} !!!")
                    # Handle error, maybe exit or return to menu
                except Exception as e:
                    print(f"!!! Error launching Human Client process: {e} !!!")

                print("\nGame components started...")  # Continue if launch seemed okay


            elif choice_int == 2:

                local_ip = get_local_ip()

                print(f"\nStarting Server to host a LAN game...")

                print(f"Your Local IP Address is approximately: {local_ip}")

                print(f"Tell the other player to use this IP when they choose option 3.")

                print("Starting server in the background...")

                # Launch Server

                server_proc = subprocess.Popen([PYTHON_EXECUTABLE, SERVER_SCRIPT])

                running_processes.append(server_proc)

                time.sleep(1)  # Give server a moment to start

                # *** Automatically launch client for the host ***

                print("Starting client for you (connecting to 127.0.0.1)...")

                try:

                    host_client_proc = subprocess.Popen(

                        [PYTHON_EXECUTABLE, CLIENT_SCRIPT, '--host', '127.0.0.1'],

                        stdout=subprocess.PIPE,  # Capture output/error

                        stderr=subprocess.PIPE,

                        text=True,

                        bufsize=1,

                        universal_newlines=True

                    )

                    running_processes.append(host_client_proc)

                    # Optional: Add quick check for host client startup

                    print("     (Checking if Host Client started okay...)")

                    time.sleep(1.0)

                    return_code = host_client_proc.poll()

                    if return_code is not None:

                        print(f"!!! WARNING: Host Client process terminated immediately with code {return_code} !!!")

                        stdout, stderr = host_client_proc.communicate()

                        if stderr:
                            print("--- Host Client STDERR ---")

                            print(stderr.strip())

                            print("---------------------------")

                    else:

                        print("     (Host Client process seems to be running)")


                except FileNotFoundError:

                    print(f"!!! FATAL: Could not find script to run: {CLIENT_SCRIPT} using {PYTHON_EXECUTABLE} !!!")

                except Exception as e:

                    print(f"!!! Error launching Host Client process: {e} !!!")

                print("\nServer and your client are running.")

                print("Wait for another player to join using option 3 and your IP.")

                print("Close the server's terminal window or use Ctrl+C to stop hosting.")

                print("Close your Pygame window when finished playing.")


            elif choice_int == 3:
                host_ip = input("Enter the IP address of the person hosting the game: ")
                if not host_ip:
                    print("Host IP cannot be empty.")
                    continue
                print(f"\nAttempting to join game hosted at {host_ip}...")
                # Launch client, passing the host IP as an argument
                join_proc = subprocess.Popen([PYTHON_EXECUTABLE, CLIENT_SCRIPT, '--host', host_ip])
                running_processes.append(join_proc)
                print("Client started. Close the Pygame window to disconnect.")

            elif choice_int == 4:
                print("Exiting.")
                # Optional: Try to terminate started processes (might not always work cleanly)
                # print("Attempting to close background processes...")
                # for proc in running_processes:
                #     try: proc.terminate()
                #     except ProcessLookupError: pass # Already finished
                break # Exit the menu loop

            else:
                print("Invalid choice. Please enter a number between 1 and 4.")

        except ValueError:
            print("Invalid input. Please enter a number.")
        except FileNotFoundError as e:
             print(f"\nError: Could not find a required script.")
             print(f"Details: {e}")
             print(f"Ensure '{PYTHON_EXECUTABLE}' is correct and the 'src' directory contains the necessary .py files.")
             break # Exit if files are missing
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")