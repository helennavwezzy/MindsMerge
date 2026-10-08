import json


def crunch(*args):
    for arg in args:
        try:
            assert isinstance(arg, dict)
            print(json.dumps(arg, indent=2))
        except Exception:
            print(arg)
    print()
