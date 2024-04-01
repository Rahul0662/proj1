import paramiko

# SSH details
hostname = 'remote_server_hostname_or_ip'
port = 22  # Default SSH port
username = 'ssh_username'
password = 'ssh_password'


def send_email(sub, body, to):
    # Command to execute
    command = f'./CMailer -s "{sub}" -m "{body}" -t "{to}"'

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
            return False

        print("Output:", output)

        if "Email sent successfully!" in output:
            return True
        else:
            return False

    except Exception as e:
        print("Error:", e)
        return False

    finally:
        # Close SSH connection
        client.close()
