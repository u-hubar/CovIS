from streaming.client import StreamClient


def main():
    server_ip = "localhost"
    client = StreamClient(server_ip)
    client.stream()


if __name__ == "__main__":
    main()
