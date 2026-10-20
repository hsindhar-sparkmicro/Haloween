import argparse
import webbrowser
import threading
from waitress import serve
from .app import create_app


def main():
    parser = argparse.ArgumentParser(description='Halloween Hub kiosk server')
    parser.add_argument('--lan', action='store_true', help='Listen on all interfaces for trusted LAN access')
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    if not args.no_browser:
        threading.Timer(1, lambda: webbrowser.open(f'http://127.0.0.1:{args.port}/?desktop=1')).start()
    print(f'Halloween Hub: http://127.0.0.1:{args.port} — simulated hardware', flush=True)
    serve(create_app(), host='0.0.0.0' if args.lan else '127.0.0.1', port=args.port, threads=6)


if __name__ == '__main__':
    main()
