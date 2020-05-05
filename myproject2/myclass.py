# myproject2/myclass.py

class MyClass:
    def __init__(self):
        print(f"MyClass initialized")

    def dump(self):
        print("myclass attributes...")
        print(f"Module: {__name__}")
        print(f"Package: {__package__}")
        print(f"File Path: {__file__}")
        print()

if __name__ == "__main__":
    print("myclass.py called directly")
    mc = MyClass()
    mc.dump()