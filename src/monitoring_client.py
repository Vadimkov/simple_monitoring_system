import argparse
from socket import *
from protocol import *


addr = "localhost"
port = 8080


def configure():
    parser = argparse.ArgumentParser(description='Send request to monitoring.')
    parser.add_argument('expression')
    parser.add_argument('type')

    args = parser.parse_args()
    return args.__dict__


def send_expression_request(expr, object_type):
    req = ExpressionRequestMes()
    req.set_field('Expression', expr)
    req.set_field('Type', object_type)

    sock = send_message_by_address(req, (addr, port))
    return sock


def get_expression_report(sock):
    lenghtResponce = get_message(sock)
    lenght = lenghtResponce.get_field('Lenght')

    units = []

    for i in range(lenght):
        unit = get_message(sock)
        units.append((unit.get_field('Agent'), unit.get_field('Space'),
                      unit.get_field('Object'), unit.get_field('String')))

    return units


def main():
    args = configure()
    print("Expressin:", args["expression"])
    print("Type:", args["type"])

    sock = send_expression_request(args["expression"], args["type"])
    report = get_expression_report(sock)
    print(report)

if __name__ == "__main__":
    main()
