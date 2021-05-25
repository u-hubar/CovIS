from streaming.server import StreamServer


def main():
    prototxt = "models/deploy.prototxt"
    model = "models/res10_300x300_ssd_iter_140000.caffemodel"

    server = StreamServer(prototxt, model, 0.1, 2, 2)
    server.stream()


if __name__ == "__main__":
    main()
