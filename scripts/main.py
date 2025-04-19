import sys
import os
import atexit
import paramiko


def parse_ips(argv):
    if len(argv) == 2:
        # Один аргумент: ip1,ip2 или ip1, ip2
        parts = argv[1].split(',')
    elif len(argv) == 3:
        # Два аргумента: ip1 и ip2 (возможно, с запятой в конце первого)
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
    
    # Register function to delete the file on script exit
    atexit.register(delete_temp_file, temp_hosts_file)
    
    return temp_hosts_file

def get_load_avg(ssh_client):
    """Get the load average from a remote server using SSH"""
    stdin, stdout, stderr = ssh_client.exec_command("cat /proc/loadavg")
    loadavg_output = stdout.read().decode().strip()
    # Parse the first value (1 minute load average)
    loadavg = float(loadavg_output.split()[0])
    return loadavg

def connect_ssh(ip, username='vagrant', port=22):
    """Connect to a server using SSH agent for authentication"""
    print(f"Connecting to {ip}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Try to connect using SSH agent authentication
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
    
    # Write IPs to temporary hosts.txt file
    hosts_file = write_to_temp_hosts(ip1, ip2)
    
    # Connect to servers and get load average
    ssh_client1 = connect_ssh(ip1)
    ssh_client2 = connect_ssh(ip2)
    
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

    bigger_load = 0
    if load_avg1 > load_avg2:
        bigger_load = ip1
    else:
        bigger_load = ip2

    print(f"Server with bigger load: {bigger_load}")
    

if __name__ == "__main__":
    main()