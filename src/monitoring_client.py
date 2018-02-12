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
    req.setField('Expression', expr)
    req.setField('Type', object_type)

    sock = send_message_by_address(req, (addr, port))
    return sock


def get_expression_report(sock):
    lenghtResponce = get_message(sock)
    lenght = lenghtResponce.getField('Lenght')

    units = []

    for i in range(lenght):
        unit = get_message(sock)
        units.append((unit.getField('Agent'), unit.getField('Space'),
                      unit.getField('Object'), unit.getField('String')))

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
