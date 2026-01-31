import pyglet
import pickle
import pandas as pd
from field_layout import (
    sizeX,
    sizeY,
    batch,
    nBatch,
    background_box2,
    background_box,
    labels,
    layout_real,
    layout_diversity,
    layout_block_2,
)
import argparse
from os import listdir

from tools import (

    load_heat,
    build_color_range_numeric,
    transform_values_to_heat,
    change_colors,
    change_values,
    create_dataset_from_csv,
    average_data,
    build_color_range,
    map_values_to_colors,
    add_legend_to_batch,
    draw_everything,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--static", action="store_true")
    parser.add_argument("--averaging", action="store_true")
    parser.add_argument("--path", default="sources/example_format.csv", type=str)
    parser.add_argument("--what", default=2, type=int)
    parser.add_argument("--heat_boxes", default=20, type=int)
    parser.add_argument("--speed", default=0.25, type=float)
    parser.add_argument("--layout", default="real", type=str)
    parser.add_argument("--heat", default="heats/heat.txt", type=str)
    parser.add_argument("--display_values", action="store_true")
    parser.add_argument("--no_csv_cash", action="store_true")
    parser.add_argument("--nan_color", default=(255, 255, 255), type=int, nargs="+")
    parser.add_argument("--up_extreme", default=30.0, type=float)
    parser.add_argument("--low_extreme", default=-1.0, type=float)
    parser.add_argument("--start", default=0, type=int)
    parser.add_argument("--end", default=-1, type=int)
    parser.add_argument("--unit", default="°C", type=str)
    parser.add_argument("--record", action="store_true")
    parser.add_argument("--font_sizes", default=(15, 15, 15, 15), type=int, nargs="+")
    parser.add_argument("--legend_title", default="_", type=str)

    args = parser.parse_args()

    # load infos
    heat = load_heat(args.heat)

    # load layout
    if args.layout == "real":
        layout_real(args.font_sizes)
    elif args.layout == "diversity":
        layout_diversity(args.font_sizes)
    elif args.layout == "block2":
        layout_block_2(args.font_sizes)
    else:
        print("unknown layout")
        return

    # load and process for display and add it to the clock
    if args.static:
        data = pd.read_csv(args.path)
        if args.layout == "block2":
            data = data.loc[data["plotcode"].str.contains("2A")]
        what = data.columns[args.what]
        labels["3"].text = args.legend_title
        colors = build_color_range_numeric(data[what].values, heat)
        data["colors"] = transform_values_to_heat(data[what].values, colors)
        # legend = add_numeric_legend_to_batch(colors, args.layout, args.font_sizes[2])
        change_colors(data, args.layout)
        if args.display_values:
            change_values(data, what, args.layout)
        window = pyglet.window.Window(sizeX, sizeY)
        window.set_location(0, 0)
    else:
        # check for cashed data
        dataName = args.path.split("/")[-1][:-4]
        data = pd.read_csv(args.path)
        data, time = create_dataset_from_csv(
            data, frequency="original"
        )  # should implement more frequency options
        if args.no_csv_cash:
            pass
        else:
            pickle.dump(
                data, open("cached_csv/" + dataName + "_original.p", "wb")
            )
            pickle.dump(
                time, open("cached_csv/" + dataName + "_original_time.p", "wb")
            )

        # keep only data that is needed.
        labels["3"].text = list(data.keys())[args.what - 2]
        data = data[list(data.keys())[args.what - 2]]
        if args.layout == "block2":
            filtered = {}
            for x in data.keys():
                if "2A" in x:
                    filtered[x] = data[x]
            data = filtered
        if args.end == -1:
            time = time[args.start :]
            for x in data.keys():
                data[x] = data[x][args.start :]
        else:
            time = time[args.start : args.end]
            for x in data.keys():
                data[x] = data[x][args.start : args.end]

        diversity = pd.read_csv(
            "sources/field_diversity.csv"
        )  # loads the diversity levels and keeps only those that are relevant
        diversity = diversity.loc[
            diversity["plotcode"].isin(data.keys()), ["plotcode", "diversity level"]
        ]
        diversity = diversity.reset_index(drop=True)

        if args.averaging:
            print("Averaging data")
            data = average_data(data, diversity)

        colors = build_color_range(data, args.heat_boxes, heat)
        colorData = map_values_to_colors(data, colors, args.nan_color)
        _ = add_legend_to_batch(colors, args.layout, args.unit)

        # draw window
        window = pyglet.window.Window(sizeX, sizeY)
        window.set_location(0, 0)
        pyglet.clock.schedule_interval(
            draw_everything,
            args.speed,
            data,
            colorData,
            time,
            [args.low_extreme, args.up_extreme],
            args.layout,
            args.record,
            args.display_values,
            window.get_location(),
        )

    # draw loop
    @window.event
    def on_draw():
        window.clear()
        # image.blit(0,0,width= sizeX,height= sizeY)
        background_box.draw()
        background_box2.draw()
        batch.draw()
        nBatch.draw()
        # Screenshot saving code (disable)
        #pyglet.image.get_buffer_manager().get_color_buffer().save("screenshot.png")

    pyglet.app.run()


if __name__ == "__main__":
    main()
