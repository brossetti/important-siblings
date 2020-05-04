# myproject2/myscript.py

from myproject2.myclass import MyClass
import sys

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