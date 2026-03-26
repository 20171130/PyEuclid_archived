import argparse
import json
import os

import matplotlib.pyplot as plt


def resolve_data_path(path_text, base_dir):
    if os.path.isabs(path_text):
        return path_text
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    root_relative = os.path.normpath(os.path.join(project_root, path_text))
    if os.path.exists(root_relative):
        return root_relative
    sample_relative = os.path.normpath(os.path.join(base_dir, path_text))
    if os.path.exists(sample_relative):
        return sample_relative
    return root_relative


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-json", required=True)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    with open(args.data_json, "r") as f:
        data = json.load(f)

    base_dir = os.path.dirname(args.data_json)
    before_path = resolve_data_path(data["diagram_before_auxiliary_png"], base_dir)
    after_path = resolve_data_path(data["diagram_after_auxiliary_png"], base_dir)

    output_path = args.output
    if output_path is None:
        output_path = os.path.join(base_dir, "diagram_after_auxiliary_reconstructed.png")

    if "auxiliary_construction_plot_code_numeric" in data:
        code_entries = data["auxiliary_construction_plot_code_numeric"]
    else:
        code_entries = data["auxiliary_construction_plot_code"]
    before_img = plt.imread(before_path)

    bottom_left = data["diagram_before_auxiliary_bounds"]["bottom_left"]
    top_right = data["diagram_before_auxiliary_bounds"]["top_right"]
    x_left = float(bottom_left[0])
    y_bottom = float(bottom_left[1])
    x_right = float(top_right[0])
    y_top = float(top_right[1])

    h, w = before_img.shape[:2]
    dpi = 300
    fig = plt.figure(figsize=(w / dpi, h / dpi), dpi=dpi)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax = fig.add_subplot(111)
    ax.set_position([0, 0, 1, 1])
    ax.set_facecolor((1.0, 1.0, 1.0))
    x_span = x_right - x_left
    y_span = y_top - y_bottom
    image_aspect = w / h
    bounds_aspect = x_span / y_span

    padded_x_left = x_left
    padded_x_right = x_right
    padded_y_bottom = y_bottom
    padded_y_top = y_top

    if image_aspect > bounds_aspect:
        padded_x_span = y_span * image_aspect
        x_pad = (padded_x_span - x_span) / 2
        padded_x_left = x_left - x_pad
        padded_x_right = x_right + x_pad
    else:
        padded_y_span = x_span / image_aspect
        y_pad = (padded_y_span - y_span) / 2
        padded_y_bottom = y_bottom - y_pad
        padded_y_top = y_top + y_pad

    ax.imshow(
        before_img,
        extent=[padded_x_left, padded_x_right, padded_y_bottom, padded_y_top],
        interpolation="nearest",
    )

    for entry in code_entries:
        for line in entry["code"]:
            exec(line, {"ax": ax})

    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_xlim(padded_x_left, padded_x_right)
    ax.set_ylim(padded_y_bottom, padded_y_top)
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)

    print(output_path)
    print(after_path)


if __name__ == "__main__":
    main()
