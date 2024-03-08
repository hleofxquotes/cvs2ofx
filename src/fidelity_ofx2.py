import argparse

from ofxtools.Parser import OFXTree

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()

    parser = OFXTree()
    with open(args.input, 'rb') as f:
        parser.parse(f)
        ofx = parser.convert()
        stmts = ofx.statements

