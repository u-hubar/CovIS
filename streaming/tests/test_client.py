from streaming.client import StreamClient


def main():
    server_ip = "192.168.0.103"
    client = StreamClient(server_ip)
    client.stream()


if __name__ == "__main__":
    main()
