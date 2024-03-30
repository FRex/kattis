#!/usr/bin/env python3
import subprocess
import sys
import os

# NOTE: requests and bs4 are imported in ensure, to not waste time importing them when they wont be used


def red(x) -> str:
    return f"\u001b[31;1m{x}\u001b[0m"


def green(x) -> str:
    return f"\u001b[32;1m{x}\u001b[0m"


def yellow(x) -> str:
    return f"\u001b[33;1m{x}\u001b[0m"


def names(url):
    dname = url[url.index("problems/") :]
    return dname, dname + "/" + url.split("/")[-1] + ".py", dname + "/shortest.txt"


def ensure(url):
    dirname, pyname, shortestname = names(url)
    gotdir = os.path.exists(dirname)
    # NOTE: requests and bs4 are imported here, to not waste time importing them when they wont be used
    if not os.path.exists(shortestname):
        import requests, bs4  # pylint: disable=multiple-imports, import-outside-toplevel

        r = requests.get(url + "/statistics", timeout=30)
        print(r)
        s = bs4.BeautifulSoup(r.text, "html.parser")
        nums = s.find("div", {"id": "toplist_shortest_0"}).find_all(
            "td", {"data-type": "length"}
        )
        os.makedirs(dirname, exist_ok=True)
        with open(shortestname, "w", encoding="UTF-8") as f:
            f.write("\n".join(n.text for n in nums) + "\n")

    if gotdir:
        return True

    import requests, bs4  # pylint: disable=multiple-imports, import-outside-toplevel

    with open(pyname, "w", encoding="UTF-8"):
        pass
    codepath = r"C:\Users\rex\AppData\Local\Programs\Microsoft VS Code\Code.exe"
    subprocess.run([codepath, pyname], check=False)
    print(f"Downloading {url}")
    r = requests.get(url, timeout=30)
    print(r)
    s = bs4.BeautifulSoup(r.text, "html.parser")
    data = []
    for sample in s.find_all(class_="sample"):
        data.append(x.text for x in sample.find_all("pre"))
    if not data:
        return
    os.makedirs(dirname, exist_ok=True)
    for i, (a, b) in enumerate(data, 1):
        with open(f"{dirname}/in-{i}.txt", "w", encoding="UTF-8") as f:
            f.write(a)
        with open(f"{dirname}/out-{i}.txt", "w", encoding="UTF-8") as f:
            f.write(b)
    print(f"{len(data)} examples in {dirname}")
    print(pyname)
    return False


MYPYEXE = "D:/tmp/pypy3.8-v7.3.9-win64/python3.8.exe"


def execute(url):
    dirname, pyname, shortestname = names(url)
    inputs = [dirname + "/" + x for x in os.listdir(dirname) if x.startswith("in-")]
    outputs = [dirname + "/" + x for x in os.listdir(dirname) if x.startswith("out-")]
    cases = list(zip(inputs, outputs))
    jobs = []
    for a, b in cases:
        args = [MYPYEXE, pyname]
        f = open(a, encoding="UTF-8")
        j = subprocess.Popen(args, stdin=f, stdout=subprocess.PIPE, encoding="UTF-8")
        jobs.append(j)

    data = open(pyname, encoding="UTF-8").read()
    if data.endswith("\n"):
        data = data[:-1]
    print(f"Running {yellow(pyname)} - {green(len(data))} chars")
    shortest = list(map(int, open(shortestname, encoding="UTF-8").read().split()))
    won = None
    for i, n in enumerate(shortest):
        if len(data) < n:
            won = i + 1
            before = map(red, shortest[:i])
            after = map(green, shortest[i:])
            print(", ".join(list(before) + list(after)))
            parts = []
            parts.append(f"Position {green(won)} won by {green(n - len(data))}")
            if i > 0:
                parts.append(f", behind {red(i)} by {red(len(data) - shortest[i-1])}")
                parts.append(f", behind {red(1)} by {red(len(data) - shortest[0])}")
            print("".join(parts))
            break
    if won is None:
        print(shortest)

    print()
    produced = []
    for j in jobs:
        produced.append(j.communicate()[0])

    needed = [open(b).read() for b in outputs]
    badcount = 0
    casecount = len(list(zip(needed, produced, inputs)))
    for n, p, iname in zip(needed, produced, inputs):
        if n == p:
            print(f"{iname} {green('OK')}")
        else:
            badcount += 1
            print(f"{iname} {red('BAD')} # " + yellow(f"{MYPYEXE} {pyname} < {iname}"))
            lines1 = n.splitlines()
            lines2 = p.splitlines()
            m = max(len(lines1), len(lines2))
            lines1.extend([""] * (m - len(lines1)))
            lines2.extend([""] * (m - len(lines2)))
            width1 = max(map(len, lines1)) + 3
            width2 = max(map(len, lines2)) + 3
            for a, b in zip(lines1, lines2):
                parts = [a.rjust(width1), b.rjust(width2)]
                if a != b:
                    if a.strip() == b.strip():
                        parts = [
                            a.replace(" ", ".").rjust(width1),
                            b.replace(" ", ".").rjust(width2),
                        ]
                        parts = map(yellow, parts)
                    else:
                        parts = map(red, parts)
                else:
                    parts = map(green, parts)
                print("|".join(parts))
            print()
    if badcount:
        print(red(f"{badcount} ERRORS IN {casecount} CASES"))
    else:
        print(green(f"ALL {casecount} OKAY!"))


def main(args):
    if len(args) < 2:
        print(f"Usage: {args[0]} URL")
        return
    url = args[1]
    os.system("")  # this causes ansi color codes to work in windows terminal
    if ensure(url):
        execute(url)


if __name__ == "__main__":
    main(sys.argv)
