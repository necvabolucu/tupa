import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from argparse import ArgumentParser


def main(args):
    _, axes = plt.subplots(len(args.data), figsize=(19, 10))
    for i, filename in enumerate(args.data):
        print(filename)
        plt.sca(axes[i] if len(args.data) > 1 else axes)
        plt.xlabel(filename)
        end = 0
        ticks = []
        ticklabels = []
        name = None
        with open(filename) as f:
            for line in f:
                if line.startswith("#"):
                    name = line
                    print(name.strip())
                else:
                    values = np.fromstring(line, sep=" ")
                    start = end
                    end += len(values)
                    ticks.append((start + end) / 2)
                    ticklabels.append(name.split()[1][1:6])
                    plt.bar(range(start, end), values)
        plt.xticks(ticks, ticklabels, rotation="vertical", fontsize=8)
        print()
    plt.savefig(args.output_file)
    print("Saved '%s'." % args.output_file)


if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("data", nargs="+")
    argparser.add_argument("-o", "--output-file", default="viz.png")
    args = argparser.parse_args()
    main(args)
