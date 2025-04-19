import sys

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

def main():
    ip1, ip2 = parse_ips(sys.argv)
    print("IP/DNS 1: {}".format(ip1))
    print("IP/DNS 2: {}".format(ip2))

if __name__ == "__main__":
    main()