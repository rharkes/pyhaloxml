from pathlib import Path
from pyhaloxml import HaloXML
import time
import statistics


def main():
    NUM_RUNS = 10
    file = Path(
        Path.cwd(),
        "testdata",
        "biganno",
        "472e91fc2a774c42b89186a4f6d13c51.annotations",
    )
    timevec = []
    for _ in range(NUM_RUNS):
        hx = HaloXML()
        hx.load(file)
        start = time.time()
        hx.matchnegative()
        timevec.append(time.time() - start)
    avg_duration = statistics.mean(timevec)
    print(f"Matching negative regions took {avg_duration * 1e3 :.2f} ms on average")


def loadfile(file):

    hx.matchnegative()


if __name__ == "__main__":
    main()
