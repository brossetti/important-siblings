# myproject6/myscript.py

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'classes'))
from myclass import MyClass

def main():
    print(f"myscript attributes...")
    print(f"Module: {__name__}")
    print(f"Package: {__package__}")
    print(f"File Path: {__file__}")
    print(f"sys.path: {sys.path}")
    print()

    mc = MyClass()
    mc.dump()

if __name__ == "__main__":
    print("myscript.py called directly")
    main()