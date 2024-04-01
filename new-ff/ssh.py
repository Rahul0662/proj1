import paramiko

# SSH details
hostname = 'remote_server_hostname_or_ip'
port = 22  # Default SSH port
username = 'ssh_username'
password = 'ssh_password'

# Command to execute
command = 'ls -l'  # Example command

# Create SSH client
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # Connect to SSH server
    client.connect(hostname, port=port, username=username, password=password)

    # Execute command
    stdin, stdout, stderr = client.exec_command(command)

    # Get output
    output = stdout.read().decode()
    error = stderr.read().decode()

    if error:
        print("Error:", error)
    else:
        print("Output:", output)

except Exception as e:
    print("Error:", e)

finally:
    # Close SSH connection
    client.close()
