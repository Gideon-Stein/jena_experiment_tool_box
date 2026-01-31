import pyglet
from pyglet import shapes
import pickle
import numpy as np
import cv2
import math
from field_layout import sizeX, sizeY, batch, nBatch, labels, borderX, borderY, legendSquareSize, FONT_COLOR
from layout_state import squares, extreme, blockValues
from mss import mss
from PIL import Image
import os.path

frameCounter = 0  # should be inside of main() but scope doesnt work?
recording = []
recorded = False


def hex_to_rgb(value):
    value = value.lstrip("#")
    lv = len(value)
    return tuple(int(value[i : i + lv // 3], 16) for i in range(0, lv, lv // 3))


def load_plotnames():
    allPlotCodes = pickle.load(open("plotNames.p", "rb"))
    for x in range(len(allPlotCodes)):
        allPlotCodes[x] = allPlotCodes[x][:-1]
    return allPlotCodes


def build_color_range(data, boxes, heatRange):
    combine = np.array([data[x] for x in data.keys()])
    threshold = np.arange(
        np.nanmin(combine),
        np.nanmax(combine),
        (np.nanmax(combine) - np.nanmin(combine)) / boxes,
    )
    selection = heatRange[np.linspace(0, len(heatRange) - 1, num=boxes).astype(int)]
    out = {}
    for x in range(len(threshold)):
        out[threshold[x]] = selection[x]
    return out


def build_color_range_numeric(data, heatRange):
    threshholds = list(set(data))
    threshholds.sort()
    assert len(threshholds) < len(heatRange), "too many numeric features!"
    selection = np.arange(0, len(heatRange), int(len(heatRange) / len(threshholds)))
    selection = heatRange[selection]
    out = {}
    for x in range(len(threshholds)):
        out[threshholds[x]] = selection[x]
    return out


def transform_values_to_heat(data, colors):
    threshholds = list(colors.keys())
    threshholds.sort()
    threshholds.reverse()
    result = []
    for x in data:
        for y in threshholds:
            if x >= y:
                result.append(tuple(colors[y]))
                break
            else:
                pass
    return result


def load_heat(path):
    f = open(path, "r")
    f = f.read()
    f = f.split("\n")
    del f[-1]
    heat = []
    for x in f:
        heat.append(hex_to_rgb(x))
    del f
    return np.array(heat)


def add_numeric_legend_to_batch(colors, layout, fontsize):
    global batch
    global nBatch
    legend = {}
    if layout == "diversity":
        row = 21
    else:
        row = 11
    for x in colors.keys():
        legend[x] = shapes.BorderedRectangle(
            borderX * 1,
            sizeY - borderY * row,
            legendSquareSize,
            legendSquareSize,
            border=1,
            color=colors[x],
            batch=batch,
        )
        legend[str(x) + " text"] = pyglet.text.Label(
            str(x),
            font_name="Verdana",
            font_size=fontsize,
            color=FONT_COLOR,
            x=borderX * 2,
            y=sizeY - borderY * row - 6,
            anchor_x="left",
            anchor_y="bottom",
            batch=nBatch,
        )
        row += 1
    return legend


def add_legend_to_batch(colors, layout, unit):
    global batch
    global nBatch
    legend = {}
    if layout == "diversity":
        row = 21
    else:
        row = 11
    description = list(colors.keys())
    description = [
        description[0],
        description[-1],
        description[int(len(description) / 2)],
    ]
    legend[str(description[0]) + " text"] = pyglet.text.Label(
        str(int(description[0])) + " " + unit,
        font_name="Verdana",
        font_size=10,
        color=FONT_COLOR,
        x=borderX * 3.5,
        y=sizeY - borderY * row,
        anchor_x="left",
        anchor_y="bottom",
        batch=nBatch,
    )
    for x in colors.keys():
        legend[x] = shapes.BorderedRectangle(
            borderX * 3,
            sizeY - borderY * row,
            legendSquareSize,
            legendSquareSize,
            border=1,
            color=colors[x],
            batch=batch,
        )
        if len(colors.keys()) <= 20:
            row += 0.4
        else:
            row += 0.2
    legend[str(description[1]) + " text"] = pyglet.text.Label(
        str(int(description[1])) + " " + unit,
        font_name="Verdana",
        font_size=10,
        color=FONT_COLOR,
        x=borderX * 3.5,
        y=sizeY - borderY * row,
        anchor_x="left",
        anchor_y="bottom",
        batch=nBatch,
    )
    return legend


def map_values_to_colors(data, colors, nanColor):
    threshholds = list(colors.keys())
    threshholds.sort()
    threshholds.reverse()
    out = {}
    for key in data:
        current_row = []
        for value in data[key]:
            if math.isnan(value):
                current_row.append(tuple(nanColor))
            for y in threshholds:
                if value >= y:
                    current_row.append(tuple(colors[y]))
                    break
        out[key] = current_row
    return out


def change_colors(data, layout):
    global squares
    for x in data["plotcode"].values:
        if x == "3A18":
            pass
        else:
            if layout == "block2":
                squares["D_" + x].color = data.loc[
                    data["plotcode"] == x, "colors"
                ].values[0]
            squares[x].color = data.loc[data["plotcode"] == x, "colors"].values[0]


def change_values(data, what, layout):
    global blockValues
    for x in data["plotcode"].values:
        if x == "3A18":
            pass
        else:
            if layout == "block2":
                blockValues["D_" + x].text = str(
                    data.loc[data["plotcode"] == x, what].values[0]
                )
            blockValues[x].text = str(data.loc[data["plotcode"] == x, what].values[0])


def reset_colors():
    global squares
    for x in squares.keys():
        if x == "3A18":
            pass
        else:
            squares[x].color = (0, 0, 0)


def draw_everything(
    t, data, colorData, time, extremeBorder, layout, record, display_values, location
):
    global recorded
    global frameCounter
    global squares
    global extreme
    # capture screen
    h = sizeY - 20
    mon = {"left": location[0], "top": location[1] + 40, "width": sizeX, "height": h}
    with mss() as sct:
        screenShot = sct.grab(mon)
        img = Image.frombytes(
            "RGB",
            (screenShot.width, screenShot.height),
            screenShot.rgb,
        )
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        recording.append(img)
    # color plots
    for key in data.keys():
        if layout == "block2":
            squares["D_" + key].color = colorData[key][frameCounter]
            extreme["D_" + key].color = colorData[key][frameCounter]
        squares[key].color = colorData[key][frameCounter]
        extreme[key].color = colorData[key][frameCounter]
    # mark extremes
    for key in data.keys():
        if layout == "block2":
            if (
                data[key][frameCounter] >= extremeBorder[1]
                or data[key][frameCounter] <= extremeBorder[0]
            ):
                extreme["D_" + key].visible = True
            else:
                extreme["D_" + key].visible = False
        if (
            data[key][frameCounter] >= extremeBorder[1]
            or data[key][frameCounter] <= extremeBorder[0]
        ):
            extreme[key].visible = True
        else:
            extreme[key].visible = False
    # draw values if necessary
    if display_values:
        for key in data.keys():
            blockValues[key].text = str(round(data[key][frameCounter], 2))
            if layout == "block2":
                blockValues["D_" + key].text = str(round(data[key][frameCounter], 2))
    # raise framecounter and save video at the end
    if frameCounter < len(colorData[list(colorData.keys())[0]]) - 1:
        labels["time"].text = str(time[frameCounter])[:10]
        frameCounter += 1
    elif frameCounter == len(colorData[list(colorData.keys())[0]]) - 1:
        labels["time"].text = str(time[frameCounter])[:10] + " (End)"
        if not recorded and record:
            save_video(t)
            recorded = True


def save_video(speed):
    width = sizeX
    height = sizeY - 20
    fps = 1 / speed
    if not os.path.exists("videos"):
        os.mkdir("videos")
    savePath = "video"
    counter = 1
    while os.path.exists("videos/" + savePath + ".avi"):
        savePath = "video" + "_" + str(counter)
        counter += 1
    fourcc = cv2.VideoWriter_fourcc(
        *"XVID"
    )  # FourCC is a 4-byte code used to specify the video codec.
    video = cv2.VideoWriter(
        "videos/" + savePath + ".avi", fourcc, float(fps), (width, height)
    )
    for frame_count in range(len(recording)):
        img = recording[frame_count]
        video.write(img)
    video.release()


def average_data(data, div):  # train -->(6524, 90)
    divIndices = {}
    for level in list(set(div["diversity level"])):
        divIndices[level] = div.loc[div["diversity level"] == level, "plotcode"].values
    for key in divIndices.keys():
        stack = []
        for x in divIndices[key]:
            stack.append(data[x])
        stack = np.nanmean(np.array(stack), axis=0)
        for x in divIndices[key]:
            data[x] = stack
    return data


def create_dataset_from_csv(df, frequency):
    if frequency == "1D":
        df["datetime"] = df["datetime"].astype("datetime64[D]")
        df = df.groupby(["datetime", "plotcode"], as_index=False).mean()
    a = df.sort_values(["plotcode", "datetime"]).reset_index(drop=True)
    time = a["datetime"].values
    out = {}
    for y in a.columns:
        if y == "datetime" or y == "plotcode":
            pass
        else:
            bucket = {}
            for x in list(set(a["plotcode"])):
                if (
                    x[-1] == "M" or x[-1] == "N"
                ):  # shorten plotcodes if they have additional letters.
                    bucket[x[:-1]] = a.loc[a["plotcode"] == x, y].values
                else:
                    bucket[x] = a.loc[a["plotcode"] == x, y].values
            out[y] = bucket
    return out, time
