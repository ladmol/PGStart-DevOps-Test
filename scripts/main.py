import sys
import os
import atexit
import paramiko
import ansible_runner


def parse_ips(argv):
    if len(argv) == 2:
        parts = argv[1].split(',')
    elif len(argv) == 3:
        parts = [argv[1].rstrip(','), argv[2]]
    else:
        print("Использование: python3 script ip1,ip2 или python3 script ip1 ip2")
        sys.exit(1)

    # Убираем лишние пробелы
    ips = [part.strip() for part in parts if part.strip()]

    if len(ips) != 2:
        print("Ошибка: необходимо передать ровно два IP/DNS адреса.")
        sys.exit(1)

    return ips[0], ips[1]


def write_to_temp_hosts(ip1, ip2):
    """Write the IP addresses to a temporary hosts.txt file"""
    temp_hosts_file = os.path.join(os.path.dirname(__file__), 'hosts.txt')

    with open(temp_hosts_file, 'w') as f:
        f.write(f"{ip1}\n{ip2}\n")

    print(f"IP addresses written to {temp_hosts_file}")

    atexit.register(delete_temp_file, temp_hosts_file)

    return temp_hosts_file


def get_load_avg(ssh_client):
    """Get the load average from a remote server using SSH"""
    stdin, stdout, stderr = ssh_client.exec_command("cat /proc/loadavg")
    loadavg_output = stdout.read().decode().strip()
    loadavg = float(loadavg_output.split()[0])
    return loadavg


def connect_ssh(ip, username='vagrant', port=22):
    """Connect to a server using SSH agent for authentication"""
    print(f"Connecting to {ip}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(
            hostname=ip,
            username=username,
            port=port,
            allow_agent=True,
            timeout=10
        )
        print(f"Successfully connected to {ip}")
        return client
    except Exception as e:
        print(f"Failed to connect to {ip}: {str(e)}")
        exit(1)


def get_distro(ssh_client):
    """Retrieve and return the distro name in lowercase from the remote server (e.g., 'debian' or 'almalinux')."""
    _, stdout, _ = ssh_client.exec_command("cat /etc/os-release")
    os_release_content = stdout.read().decode()
    for line in os_release_content.splitlines():
        if line.startswith("ID="):
            distro = line.split('=')[1].strip().replace('"', '').lower()
            return distro
    return ""


def delete_temp_file(file_path):
    """Delete a temporary file"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Temporary file {file_path} has been deleted")
    except Exception as e:
        print(f"Error deleting temporary file: {e}")


def main():
    ip1, ip2 = parse_ips(sys.argv)
    print("IP/DNS 1: {}".format(ip1))
    print("IP/DNS 2: {}".format(ip2))

    hosts_file = write_to_temp_hosts(ip1, ip2)

    ssh_client1 = connect_ssh(ip1)
    ssh_client2 = connect_ssh(ip2)

    ssh_client1_distribution = get_distro(ssh_client1)
    ssh_client2_distribution = get_distro(ssh_client2)

    print(f"Distribution for {ip1}: {ssh_client1_distribution}")
    print(f"Distribution for {ip2}: {ssh_client2_distribution}")

    load_avg1 = None
    load_avg2 = None

    if ssh_client1:
        try:
            load_avg1 = get_load_avg(ssh_client1)
            print(f"Load average for {ip1}: {load_avg1}")
        finally:
            ssh_client1.close()

    if ssh_client2:
        try:
            load_avg2 = get_load_avg(ssh_client2)
            print(f"Load average for {ip2}: {load_avg2}")
        finally:
            ssh_client2.close()

    less_load = 0
    max_load = ''
    if load_avg1 > load_avg2:
        less_load = ip2
        max_load = ssh_client1_distribution
    else:
        less_load = ip1
        max_load = ssh_client2_distribution

    print(f"Server with bigger load: {less_load}")
    print(f"Max load: {max_load}")

    private_data_dir = './demo'
    os.makedirs(private_data_dir, exist_ok=True)

    result = ansible_runner.run(
        private_data_dir='./demo',
        playbook='../ansible/playbook.yml',
        inventory={
            'all': {
                'hosts': {
                    ip1: {"ansible_user": "vagrant", "ansible_ssh_common_args": "-o StrictHostKeyChecking=no"},
                    ip2: {"ansible_user": "vagrant",
                          "ansible_ssh_common_args": "-o StrictHostKeyChecking=no"}
                }
            }
        },  # путь к инвентарю
        extravars={
            'postres_allow_student_connect_from': less_load,
            'max_load': max_load,
        },
    )

    print("Status:", result.status)
    print("RC:", result.rc)


if __name__ == "__main__":
    main()
