import argparse
import json
import os
import re

import matplotlib.pyplot as plt
import numpy as np


def parse_coordinates(coordinates_text):
    points = []
    pattern = r"[A-Za-z]+:\s*\(([^,]+),\s*([^)]+)\)"
    for x_str, y_str in re.findall(pattern, coordinates_text):
        points.append((float(x_str), float(y_str)))
    return points


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-json", required=True)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    with open(args.data_json, "r") as f:
        data = json.load(f)

    base_dir = os.path.dirname(args.data_json)
    before_path = data["diagram_before_auxiliary_png"]
    after_path = data["diagram_after_auxiliary_png"]
    if not os.path.isabs(before_path):
        before_path = os.path.join(base_dir, before_path)
    if not os.path.isabs(after_path):
        after_path = os.path.join(base_dir, after_path)

    output_path = args.output
    if output_path is None:
        output_path = os.path.join(base_dir, "diagram_after_auxiliary_reconstructed.png")

    if "auxiliary_construction_plot_code_numeric" in data:
        code_entries = data["auxiliary_construction_plot_code_numeric"]
    else:
        code_entries = data["auxiliary_construction_plot_code"]
    before_img = plt.imread(before_path)

    coords = parse_coordinates(data["coordinates"])
    xs = [p[0] for p in coords]
    ys = [p[1] for p in coords]
    xmin = min(xs)
    xmax = max(xs)
    ymin = min(ys)
    ymax = max(ys)
    x_margin = (xmax - xmin) * 0.1
    y_margin = (ymax - ymin) * 0.1

    h, w = before_img.shape[:2]
    dpi = 300
    fig = plt.figure(figsize=(w / dpi, h / dpi), dpi=dpi)
    ax = fig.add_subplot(111)
    ax.set_facecolor((1.0, 1.0, 1.0))
    ax.imshow(
        before_img,
        extent=[xmin - x_margin, xmax + x_margin, ymin - y_margin, ymax + y_margin],
        origin="lower",
        interpolation="nearest",
    )

    for entry in code_entries:
        for line in entry["code"]:
            exec(line, {"ax": ax})

    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_xlim(xmin - x_margin, xmax + x_margin)
    ax.set_ylim(ymin - y_margin, ymax + y_margin)
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight", pad_inches=0)
    plt.close(fig)

    print(output_path)
    print(after_path)


if __name__ == "__main__":
    main()
