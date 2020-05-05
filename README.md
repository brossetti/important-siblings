# `import`ant Siblings

Have you ever looked at a piece of code and thought, "there must be a better solution"? This happened to me recently when I was working on a project that included some Python code. All I wanted to do was import a python module into a script located in a sibling directory. It seemed like an easy problem on the surface, but I quickly realized that I was venturing into strange territory. I developed this repository as a way of exploring the different methods for importing python packages and modules. I wanted to know which method was best and for which situations. The answer, it turns out, was not so clear. If you really just want the solution, head down to the [TL;DR](#the-final-solution--tldr) section.

A few notes before we get started. The information and code in this document pertains to Python 3.8. Code blocks that start with `# path/to/file.py` show the contents of a file with the same path in this repository. For code blocks showing input/output from an interactive terminal, I distinguish between the shell and python REPL using the symbols `$` and `>>>`, respectively. See a mistake? Please feel free to submit an issue.

## Setting the Stage

Let's begin by defining some terms. The [python docs](https://docs.python.org/3/tutorial/modules.html) tell us that, "a module is a file containing Python definitions and statements. The file name is the module name with the suffix `.py` appended." People also refer to modules as programs, scripts, or classes depending on the file's content and purpose. Modules can be groups together in packages. The [docs](https://docs.python.org/3/tutorial/modules.html#packages) describe packages as "a way of structuring Python's module namespace by using 'dotted module names'." Most often a package is simply a directory of Python files. The [docs](https://docs.python.org/3/reference/import.html#packages) also make the important distinction that, "all packages are modules, but not all modules are packages. Or put another way, packages are just a special kind of module. Specifically, any module that contains a `__path__` attribute is considered a package." We'll touch on `__path__` again a bit later.

To get access to the code in a module or package, we leverage Python's import system (most commonly through the `import` statement). For example, adding `import os` to your module will give you access to a variety of useful file system functions. The `import` statement performs two operations: (1) it iteratively searches for each module listed in the `import` statement and, if found, (2) binds them to names in the local scope. Understanding how Python searches for a module is critical to understanding how to properly import local modules.

When the `import` statement is executed, Python first searches for the module among the built-in modules. If the module is not found, it then searches for a `.py` file of the same name in `sys.path`. The [docs](https://docs.python.org/3/tutorial/modules.html#the-module-search-path) indicate that

>`sys.path` is initialized from these locations:
>
>* The directory containing the input script (or the current directory when no file is specified).
>
>* `PYTHONPATH` (a list of directory names, with the same syntax as the shell variable `PATH`).
>
>* The installation-dependent default.

If Python is unable to find the module's `.py` file among the `sys.path` directories, a `ModuleNotFoundError` is raised.

### The Problem

With that out of the way, we should formally stating the problem we are trying to solve. Let's assume that we have a project with the following directory hierarchy.

```text
myproject/
├── classes/
│     └── myclass.py
└── scripts/
      └── myscript.py
```

Our project separates class files and scripts into sibling directories. We might be doing this for organization or to conform to some constraint in our project. The question is, **how do we import `myclass.py` into `myscript.py` when they exist in sibling directories?** I could just give you the answer now, but that wouldn't be very academic of me. Instead, we should start by exploring some easier cases. Doing so will give us a better frame of reference, and we can pick up a few more details along the way.

## Importing a Module from the Same Directory

### `myproject0`

For many simple projects, most (or all) of the files can exist together in a single directory. For example, we might have the following situation.

```text
myproject0/
├── myclass.py
└── myscript.py
```

The question in this scenario is how do we import `myclass.py` into `myscript.py` when everyone lives in the same directory. Let's take a look at what we have in `myclass.py`.

```python
# myproject0/myclass.py

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
```

This class file is pretty straightforward, but we should note a few important items. First, `MyClass` has two methods: (1) `__init__()` which gets called when we create an instance of `MyClass` and (2) `dump()` which prints out some useful attributes. Despite being clearly named, I've included a quick description of these attributes.

```text
__name__    : fully-qualified module name
__package__ : name of the module's package (when the module is a package, __package__ is set to __name__)
__file__    : module's path
```

These attributes will help us diagnose problems with our imports later.

Finally, `myclass.py` contains code blocked by an `if __name__ == "__main__":` statement. This statement ensures that any code within its scope will only be executed if the file is called directly (e.g., as with `$ python /path/to/myproject0/myclass.py`). This works because the `__name__` attribute reflects the scope where the code is executed, which in this case is the top-level scope called `__main__`.

Let's shift our attention back to the problem of importing `MyClass` into `myscript.py`. We learned earlier that Python will look through `sys.path` for our module, and one of the directories that `sys.path` contains is the parent directory of the input script. That means that `myproject0` is going to be on our module search path. Therefore, we should be able to include the module directly in our `import` statement.

```python
# myproject0/myscript.py

from myclass import MyClass
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
```

The statement `from myclass import MyClass` will cause Python to look for a file called `myclass.py` within `sys.path`. If it's found, Python will bind the class `MyClass` to our local scope. Note that we also included some helpful print statements within the `main()` method of `myscript.py`. Let's call this script to see if everything works properly.

```text
$ python myproject0/myscript.py
myscript.py called directly
myscript attributes...
Module: __main__
Package: None
File Path: myproject0/myscript.py
sys.path: ['/path/to/important-siblings/myproject0', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python38.zip', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python3.8', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python3.8/lib-dynload', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python3.8/site-packages']

MyClass initialized
myclass attributes...
Module: myclass
Package: 
File Path: /path/to/important-siblings/myproject0/myclass.py
```

Awesome! We can see a couple of interesting thing in this result. First, `/path/to/important-siblings/myproject0` is indeed in our list of `sys.path` search directories. The module name for `myscript.py` is `__main__` (because we called it directly) and `myclass` for `myclass.py` (because it was imported). There is also a slight difference in the package names (i.e., `None` for `myscript.py` and undefined for `myclass.py`). Since neither module is in a package, neither `__package__` attribute is set. However, the [docs](https://docs.python.org/3/reference/import.html#__package__) says that, "when the module is not a package, `__package__` should be set to the empty string for top-level modules, or for submodules, to the parent package’s name." Speaking of packages, let's see if there is another solution to this problem that uses packages.

### `myproject1`

Just as before, we will assume that both `myclass.py` and `myscript.py` exist in the same directory, but now we will treat `myproject1` as a package. We do this my including a special `__init__.py` file inside `myproject1`.

```text
myproject1/
├── __init__.py
├── myclass.py
└── myscript.py
```

When Python sees the `__init__.py` file, it knows to treat the parent directory as a package. When the package is loaded, the contents of `__init__.py` are executed. In the trivial case, `__init__.py` can be an empty file. However, we will add a print statement to ours so that we can observe the value of `__path__`. As we mentioned before, any package must define the `__path__` attribute.

```python
# myproject1/__init__.py

print("__init__.py attributes...")
print(f"Search Path: {__path__}")
print()
```

The `__path__` attribute acts much like `sys.path` in that it tells Python where to find the package modules. Because of this, we can change how we write our `import` statement in `myscript.py`. Since we are importing a module within the same package, and all modules in the package are on the search path, we can use a relative or absolute `import` statement. There is a subtle difference between the two (described in the [docs](https://docs.python.org/3/reference/import.html#package-relative-imports)), but we will use absolute imports because they are more versatile.

```python
# myproject1/myscript.py

from myproject1.myclass import MyClass
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
```

As we can see, our absolute import is written as `from myproject1.myclass import MyClass`. The relative version would be `from .myclass import MyClass`. Notice that the relative import uses a single `.` to specify that `myclass` lives in the same directory as the file doing the importing. Let's see what happens when we try to call `myscript.py`.

```text
$ python myproject1/myscript.py
Traceback (most recent call last):
  File "myproject1/myscript.py", line 3, in <module>
    from myproject1.myclass import MyClass
ModuleNotFoundError: No module named 'myproject1'
```

Uh-oh! Why did we get a `ModuleNotFoundError`? Well, our `import` statement is looking on `sys.path` for a file named `myproject1.py`, and it doesn't exist. When we deal with packages, we can no longer call modules by their file path. Instead, we have to execute `myscript.py` as a module, and we must do so from the package's parent directory. We can run a file as a module using the Python interpreter's `-m` option and providing the absolute module name.

```text
$ python -m myproject1.myscript
__init__.py attributes...
Search Path: ['/path/to/important-siblings/myproject1']

myscript.py called directly
myscript attributes...
Module: __main__
Package: myproject1
File Path: /path/to/important-siblings/myproject1/myscript.py
sys.path: ['/path/to/important-siblings', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python38.zip', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python3.8', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python3.8/lib-dynload', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python3.8/site-packages']

MyClass initialized
myclass attributes...
Module: myproject1.myclass
Package: myproject1
File Path: /path/to/important-siblings/myproject1/myclass.py
```

Perfect, we can still import `MyClass` when our modules are setup as a package. The down side is that we are much more restricted in how we can execute `myscript.py`. To remove this limitation, you can take the extra step of installing our local package into `site-packages` using the `pip install -e` command. This will create a symlink inside `site-packages` to your local package directory. Since `site-packages` is already on `sys.path`, Python will always be able to find your local package. Keep in mind that you will also need to include a `setup.py` file in your root package if you want to use `pip install -e`.

Interestingly, we don't really need the `__init__.py` file to make this package solution work. Python has two types of packages: (1) [regular packages](https://docs.python.org/3/glossary.html#term-regular-package) and (2) [namespace packages](https://docs.python.org/3/glossary.html#term-namespace-package). What we just saw was a regular package (i.e., anything that includes `__init__.py` files). [Namespace package](https://www.python.org/dev/peps/pep-0420/) are intended to allow single Python packages to be spread across multiple directories. They are implicitly created and initialized when Python is searching for the module of an `import` statement.

### `myproject2`

In this scenario, we are going to use the exact same import method as before except we won't use the `__init__.py` file.

```text
myproject2/
├── myclass.py
└── myscript.py
```

Now what happens when we run `myscript.py` the same way we did previously?

```text
$ python -m myproject2.myscript
myscript.py called directly
myscript attributes...
Module: __main__
Package: myproject2
File Path: /path/to/important-siblings/myproject2/myscript.py
sys.path: ['/path/to/important-siblings', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python38.zip', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python3.8', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python3.8/lib-dynload', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python3.8/site-packages']

MyClass initialized
myclass attributes...
Module: myproject2.myclass
Package: myproject2
File Path: /path/to/important-siblings/myproject2/myclass.py
```

Sure enough, Python still implicitly recognizes that both `myclass.py` and `myscript.py` are in the `myproject2` package. As a result, the `from myprojectX.myclass import MyClass` statement works identically with either regular or namespace packages. Before me move on, we should probably see how this all works if we are using the Python REPL.

```text
$ cd /path/to/important-siblings
$ python
>>> from myproject2.myclass import MyClass
>>> mc = MyClass()
MyClass initialized
>>> mc.dump()
myclass attributes...
Module: myproject2.myclass
Package: myproject2
File Path: /path/to/important-siblings/myproject2/myclass.py
```

Just as before, we are able to load `MyClass` within the Python REPL since `myclass` is implicitly a module of the `myproject2` namespace package. Let's switch gears a bit by looking at a different directory hierarchy for our project.

## Importing a Module from a Child Directory

### `myproject3`

As a project becomes larger, it might be useful to separate files into subdirectories. Let's assume that we have pulled all of our class files into a `classes` child directory.

```text
myproject3/
├── classes/
│     └── myclass.py
└── myscript.py
```

At this point, not too much has changed for us. If we call `myscript.py` directy, then we know `sys.path` will include `/path/to/myproject3`. Therefore, Python should be able to find and traverse the `classes` subdirectory. The important thing to recognize here is that `classes` will be treated as a namespace package containing `myclass.py`. We can import this namespace package using another absolute `import` statement (the relative import would be `from .myclass import MyClass`).

```python
# myproject3/myscript.py

from classes.myclass import MyClass
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
```

But how do we call `myscript.py`? Do we call the file directly or run it as a module? Well, `myscript.py` is not in a package. Therefore, we can call the file directly.

```text
$ python myproject3/myscript.py
myscript.py called directly
myscript attributes...
Module: __main__
Package: None
File Path: myproject3/myscript.py
sys.path: ['/path/to/important-siblings/myproject3', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python38.zip', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python3.8', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python3.8/lib-dynload', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python3.8/site-packages']

MyClass initialized
myclass attributes...
Module: classes.myclass
Package: classes
File Path: /path/to/important-siblings/myproject3/classes/myclass.py
```

Just as we expected, `myscript.py` has no package; whereas, `myclass.py` is within the `classes` package. What is nice about this situation is that we can again call `myscript.py` from anywhere without having to use the `-m` option with the Python interpreter. There is no reason that we can't treat the entire `myproject3` directory as a regular or namespace package. For completeness, let's look at what our `import` statement would be for this scenario.

### `myproject4`

Let's assume that we have the same directory hiearchy as our previous example.

```text
myproject4/
├── classes/
│     └── myclass.py
└── myscript.py
```

This time we want to treat the root directory, `myproject4`, as a package. We will do this implicitly with a namespace package. For this, we need only to slightly alter the `import` statement in `myscript.py`.

```python
# myproject4/myscript.py

from myproject4.classes.myclass import MyClass
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
```

As you can see, we've only added `myproject4` to the `import` statement. Keep in mind that we now need to run `myscript.py` as a module because it lives inside a package.

```text
$ python -m myproject4.myscript
myscript.py called directly
myscript attributes...
Module: __main__
Package: myproject4
File Path: /path/to/important-siblings/myproject4/myscript.py
sys.path: ['/path/to/important-siblings', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python38.zip', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python3.8', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python3.8/lib-dynload', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python3.8/site-packages']

MyClass initialized
myclass attributes...
Module: myproject4.classes.myclass
Package: myproject4.classes
File Path: /path/to/important-siblings/myproject4/classes/myclass.py
```

Both `myscript.py` and `myclass.py` are contained within the `myproject4` package. We should also note that `myclass.py` is a module in the subpackage `classes`. If we wanted to achieve the same results with a regular package instead of a namespace package, we would use two `__init__.py` files.

```text
myprojectX/
├── __init__.py
├── classes/
│     ├── __init__.py
│     └── myclass.py
└── myscript.py
```

Which solution you choose for importing from a child directory is dependent on the context of your problem. That said, `myproject3` appears to be the cleaner solution because `myscript.py` is not included in the package, and none of the restrictions of packages apply.Note that if we ever wanted to call `myclass.py` directly, we would have to execute the file as a module with `-m`.

## Importing a Module from a Sibling Directory

### `myproject5`

Finally, we made it to the problem that started this whole endeavour. How do we import a module from a sibling directory? We will remind ourselves of the directory hierarchy.

```text
myproject5/
├── classes/
│     └── myclass.py
└── scripts/
      └── myscript.py
```

The problem is that calling `myscript.py` directly will only put `/path/to/myproject5/scripts` into `sys.path`. This is not very useful because we have no convenient way to reach `/path/to/myproject5/classes` even if we treat `scripts` as a package. However, if we treat `myproject5` as a package containing two subpackages, `classes` and `scripts`, then suddenly everything exists on our `__path__` attribute. Recall, `__path__` acts like `sys.admin` in that it contains the search directories for the modules in a package. It may be surprising, but the solution to our problem uses the same absolute `import` statement as the previous example.

```python
# myproject5/scripts/myscript.py

from myproject5.classes.myclass import MyClass
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
```

I should note, however, that the relative `import` statement would be slightly different, `from ..classes.myclass import MyClass`, since the relative location of files have changed. Again, executing the files requires that we run `myscript.py` as a module.

```text
$ python -m myproject5.scripts.myscript
myscript.py called directly
myscript attributes...
Module: __main__
Package: myproject5.scripts
File Path: /path/to/important-siblings/myproject5/scripts/myscript.py
sys.path: ['/path/to/important-siblings', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python38.zip', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python3.8', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python3.8/lib-dynload', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python3.8/site-packages']

MyClass initialized
myclass attributes...
Module: myproject5.classes.myclass
Package: myproject5.classes
File Path: /path/to/important-siblings/myproject5/classes/myclass.py
```

There we have it! All done, right? Well, no... not really. This solution requires again that we run everything inside of `myproject5` as a module. This is particularly annoying when you are not dealing with a large project. Instead of being able to run `myscript.py` from anywhere, we have to run in from the parent of `myproject5` using the `-m` option. To get around this, I mentioned that we could install the project in the `site-packages` directory. However, it feels like there should be a better way.

We mentioned several times now that modules are found by searching the directories on `sys.path`, and `sys.path` gets populated by the directory of the executed file, `PYTHONPATH`, and installation-dependent defaults. So one option is that we could modify `PYTHONPATH` to include `/path/to/myproject5/classes`. This is somewhat unsatisfying because it would mean that we need to run a shell script that appends `PYTHONPATH` and executes our script, or we need to modify `PYTHONPATH` in our `.rc` file. There must be another way!

### `myproject6`

What if we modify `sys.path` itself? In fact, the [docs](https://docs.python.org/3/tutorial/modules.html#the-module-search-path) loosely suggest this as an option.

>After initialization, Python programs can modify `sys.path`. The directory containing the script being run is placed at the beginning of the search path, ahead of the standard library path. This means that scripts in that directory will be loaded instead of modules of the same name in the library directory.

Moreover, this is one of the most commonly suggested methods for importing modules without dealing with regular or namespace packages. Adding a hard-coded path to `sys.path` would be a bad idea. If the script ever gets moved, your code will break. Fortunately, the `os` package will allow us to build a relative path at runtime.

```python
# myproject6/scripts/myscript.py

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
```

The secret sauce is the `sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'classes'))` statement. This line uses the `__file__` attribute to get the name of the file being executed. Then `os.path.dirname()` is used to get the path of the parent directory. We then use `os.path.join` to move up one directly (i.e., `..`) and into the `classes` sibling directory. Finally, we append this path to `sys.path`.

```text
$ python myproject6/scripts/myscript.py
myscript.py called directly
myscript attributes...
Module: __main__
Package: None
File Path: myproject6/scripts/myscript.py
sys.path: ['/path/to/important-siblings/myproject6/scripts', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python38.zip', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python3.8', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python3.8/lib-dynload', '/usr/local/Caskroom/miniconda/base/envs/important-siblings/lib/python3.8/site-packages', 'myproject6/scripts/../classes']

MyClass initialized
myclass attributes...
Module: myclass
Package: 
File Path: myproject6/scripts/../classes/myclass.py
```

We can see that `sys.path.append` has added a new directory onto the end of `sys.path`. Now comes the controversy. Is this a hack or is this a legitimate solution?

#### Hack or Not?

Many people refer to the `sys.path.append` method as being a hack. But why? One of the more popular reasons is that, "modifying `sys.path` at runtime is a bad idea." This point is not so clear to me. In fact, all of our methods modify `sys.path`. The only difference is in how we go about making the modification. I suspect the more likely reason is that `sys.path.append` is ugly. Mixing `import` statements with a line of code just looks and feels wrong. It seems like there should be a more Pythonic way of doing this. Unfortunately, there is not. We can solve our problem with packages, `PYTHONPATH`, or `sys.path`. Treating everything as a package certainly makes the code cleaner, but it also adds a lot of complication. I think there is room for both solutions, and it depends on your project. For a big project, you are probably already using packages, and you might just want to continue. For a small project, however, I think the `sys.path.append` method is perfectly fine. It's fast, requires only one line, and doesn't alter your existing workflow. Aside from being ugly, there does not appear to be anything hacky about it.

## Wrapping Things Up

If you want to import code from `myclass.py` into another module (regardless of their relative locations), Python must be able to find the `myclass` module. In general, this means that the `myclass` module must exist somewhere within a directory stored in `sys.path`. There are a bunch of methods for getting the `myclass.py` parent directory onto `sys.path`, but two methods prevail. First, you can modify `sys.path` directly with the `sys.path.append` (or `sys.path.insert`) method. This will push whatever directory you want onto the list of searchable module locations at runtime. Some people don't like this option because it requires that you modify `sys.path` directly. The more elegant (albeit more complicated) solution is to make the parent directory of `myclass.py` into a package. Installing this package into `site-packages` with `pip install -e` will create a symlink inside `site-packages` that points to the package containing `myclass.py`. Since `site-packages` already exists in `sys.path`, the `myclass` module will be available everywhere. The last detail is whether you use a regular or namespace package. Since [namespace packages are new](https://www.python.org/dev/peps/pep-0420/) (as of Python 3.3), it is probably best to use a regular package with `__init__.py` files. Although they require a bit of extra work, the `__init__.py` files are a clear indicator to other programmers that they are working with a Python package.

## The Final Solution / TL;DR

If you are in a rush (or have one-off code), you can import `myclass.py` into `myscript.py` from sibling directories using the following code.

```python
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'classes'))
from myclass import MyClass
```

This solution uses `sys.path.append` to add the directory containing `myclass.py ` to your module search path. Check out the `myproject6` directory for a complete example of the quick n' dirty method.

If you want to follow best practices, you should add `__init__.py` files to your directories to create a Python package (`mypkg`) that contains two subpackages (`classes` and `scripts`). You will also need a `setup.py` file so that you can install the package into `site-packages` using `pip install -e`. Your project will end up having the following structure.

```text
bestpractice/
├── setup.py
└── mypkg/
      ├── __init__.py
      ├── classes/
      │     ├── __init__.py
      │     └── myclass.py
      └── scripts/
            ├── __init__.py
            └── myscript.py
```

Inside `setup.py`, you will have to include some basic information about the package (i.e., the name, version, and list of included packages).

```python
# bestpractice/setup.py

from setuptools import setup, find_packages

setup(
    name='mypkg',
    version='0.0.1',
    packages=find_packages()
)
```

To actually install `mypkg` into `site-packages`, you will need to do the following.

```text
$ cd /path/to/bestpractice
$ pip install -e .
Obtaining file:///path/to/important-siblings/bestpractice
Installing collected packages: mypkg
  Running setup.py develop for mypkg
Successfully installed mypkg
```

Finally, you can execute `myscript.py` from anywhere using `python /path/to/bestpractice/mpkg/scripts/myscript.py` or `python -m mypkg.scripts.myscript`. Enjoy!
