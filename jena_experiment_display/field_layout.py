import pyglet
from pyglet import shapes
import pickle
import pandas as pd
from layout_state import squares, naming, blockNames, blockValues, extreme, dividers

# Colors and sizes
BLUE = (0, 0, 160)
GREEN = (0, 128, 0)
RED = (128, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (227, 227, 227)
FONT_COLOR = (0, 0, 0, 255)
LIGHT_GREEN = (234, 247, 191)
BACKGROUND = (255, 255, 255)

nBatch = pyglet.graphics.Batch()
batch = pyglet.graphics.Batch()

sizeX = 1000
sizeY = sizeX
borderX = int(sizeX / 20)
borderY = int(sizeY / 30)
namingBorder = int(borderX / 10)
distanceX = int(borderX / 20)
distanceY = int(borderY / 20)
squareSize = int((sizeY - (sizeY / 40 * 2)) / 13)
legendSquareSize = int(squareSize / 4)

# BG and headers
background_box = shapes.BorderedRectangle(
    0, 0, sizeX, sizeY, border=1, color=BACKGROUND
)
background_box2 = shapes.BorderedRectangle(
    borderX * 0.5,
    sizeY - squareSize * 3,
    sizeX / 4.85,
    squareSize * 2.25,
    border=2,
    color=LIGHT_GREEN,
)
background_box.opacity = 224

labels = {}
labels["1"] = pyglet.text.Label(
    "The",
    font_name="Verdana",
    font_size=24,
    color=FONT_COLOR,
    italic=True,
    x=borderX * 0.6,
    y=sizeY - borderY * 2,
    anchor_x="left",
    anchor_y="top",
    batch=nBatch,
)
labels["4"] = pyglet.text.Label(
    "Jena",
    font_name="Verdana",
    font_size=24,
    italic=True,
    color=FONT_COLOR,
    x=borderX * 0.6,
    y=sizeY - borderY * 3.5,
    anchor_x="left",
    anchor_y="top",
    batch=nBatch,
)
labels["2"] = pyglet.text.Label(
    "experiment",
    font_name="Verdana",
    font_size=24,
    italic=True,
    color=FONT_COLOR,
    x=borderX * 0.6,
    y=sizeY - borderY * 5,
    anchor_x="left",
    anchor_y="top",
    batch=nBatch,
)
labels["3"] = pyglet.text.Label(
    "What is displayed?",
    font_name="Verdana",
    font_size=24,
    italic=True,
    color=FONT_COLOR,
    x=borderX * 0.7,
    y=sizeY - borderY * 8.5,
    anchor_x="left",
    anchor_y="top",
    batch=nBatch,
)

# image = image.load('sources/bg.jpg')

# container for all elements is shared in layout_state


def layout_diversity(fontsize):
    labels["time"] = pyglet.text.Label(
        "",
        font_name="Verdana",
        font_size=fontsize[0],
        italic=True,
        color=FONT_COLOR,
        x=borderX * 3,
        y=sizeY - borderY * 12.5,
        anchor_x="left",
        anchor_y="top",
        batch=nBatch,
    )
    data = pd.read_csv("sources/field_diversity.csv")
    data.loc[data["diversity level"] == -1, "diversity level"] = 0

    blocks = {}
    for plot in data["plotcode"].values:
        divLevel = data.loc[data["plotcode"] == plot, "diversity level"].values[0]
        if divLevel in blocks.keys():
            blocks[divLevel].append(plot)
        else:
            blocks[divLevel] = [plot]
    placement = {
        0: [borderY + squareSize * 9, sizeX / 2 + squareSize * 1.0],
        1: [borderY + squareSize * 9, sizeX / 2 + squareSize * 5.5],
        2: [borderY + squareSize * 4.5, sizeX / 2 + squareSize * 5.5],
        4: [borderY + squareSize * 0, sizeX / 2 + squareSize * 5.5],
        8: [borderY + squareSize * 0, sizeX / 2 + squareSize * 1.0],
        16: [borderY + squareSize * 4.5, sizeX / 2 + squareSize * 1.0],
    }
    for group in placement.keys():
        X = placement[group][1]
        Y = placement[group][0]
        counter = 0
        for plot in blocks[group]:
            squares[plot] = shapes.BorderedRectangle(
                X, Y, squareSize, squareSize, border=2, color=GREY, batch=batch
            )
            extreme[plot] = shapes.BorderedRectangle(
                X,
                Y,
                squareSize,
                squareSize,
                border=10,
                color=GREY,
                batch=batch,
                border_color=RED,
            )
            extreme[plot].visible = False
            naming[plot] = pyglet.text.Label(
                plot,
                font_name="Verdana",
                font_size=fontsize[1],
                color=FONT_COLOR,
                x=X + namingBorder,
                y=Y,
                anchor_x="left",
                anchor_y="bottom",
                batch=nBatch,
            )
            blockValues[plot] = pyglet.text.Label(
                "",
                font_name="Verdana",
                font_size=fontsize[2],
                color=FONT_COLOR,
                x=X + 0.5 * squareSize,
                y=Y + 0.5 * squareSize,
                anchor_x="center",
                anchor_y="center",
                batch=nBatch,
            )
            if counter < 3:
                Y += squareSize
                counter += 1
            else:
                Y = placement[group][0]
                X -= squareSize + distanceX
                counter = 0
    X = sizeX / 2 + squareSize * 1.0 - (squareSize + distanceX) * 3
    Y = borderY + squareSize * 9
    counter = 0
    group = blocks[60]
    for plot in group:
        squares[plot] = shapes.BorderedRectangle(
            X, Y, squareSize, squareSize, border=2, color=GREY, batch=batch
        )
        extreme[plot] = shapes.BorderedRectangle(
            X,
            Y,
            squareSize,
            squareSize,
            border=10,
            color=GREY,
            batch=batch,
            border_color=RED,
        )
        extreme[plot].visible = False
        naming[plot] = pyglet.text.Label(
            plot,
            font_name="Verdana",
            font_size=fontsize[1],
            color=FONT_COLOR,
            x=X + namingBorder,
            y=Y,
            anchor_x="left",
            anchor_y="bottom",
            batch=nBatch,
        )
        blockValues[plot] = pyglet.text.Label(
            "",
            font_name="Verdana",
            font_size=fontsize[2],
            color=FONT_COLOR,
            x=X + 0.5 * squareSize,
            y=Y + 0.5 * squareSize,
            anchor_x="center",
            anchor_y="center",
            batch=nBatch,
        )
        Y += squareSize
        counter = 0
    blockNames["0"] = pyglet.text.Label(
        "Diversity: 0",
        font_name="Verdana",
        font_size=fontsize[3],
        color=(0, 0, 0, 255),
        x=sizeX / 2 + squareSize * 1.0,
        y=borderY + squareSize * 9,
        anchor_x="left",
        anchor_y="top",
        batch=nBatch,
    )
    blockNames["1"] = pyglet.text.Label(
        "Diversity: 1",
        font_name="Verdana",
        font_size=fontsize[3],
        color=(0, 0, 0, 255),
        x=sizeX / 2 + squareSize * 5.5,
        y=borderY + squareSize * 9,
        anchor_x="left",
        anchor_y="top",
        batch=nBatch,
    )
    blockNames["2"] = pyglet.text.Label(
        "Diversity: 2",
        font_name="Verdana",
        font_size=fontsize[3],
        color=(0, 0, 0, 255),
        x=sizeX / 2 + squareSize * 5.5,
        y=borderY + squareSize * 4.5,
        anchor_x="left",
        anchor_y="top",
        batch=nBatch,
    )
    blockNames["4"] = pyglet.text.Label(
        "Diversity: 4",
        font_name="Verdana",
        font_size=fontsize[3],
        color=(0, 0, 0, 255),
        x=sizeX / 2 + squareSize * 2.5,
        y=borderY + squareSize * 4.0,
        anchor_x="left",
        anchor_y="bottom",
        batch=nBatch,
    )
    blockNames["8"] = pyglet.text.Label(
        "Diversity: 8",
        font_name="Verdana",
        font_size=fontsize[3],
        color=(0, 0, 0, 255),
        x=sizeX / 2 - squareSize * 2,
        y=borderY + squareSize * 4.0,
        anchor_x="left",
        anchor_y="bottom",
        batch=nBatch,
    )
    blockNames["16"] = pyglet.text.Label(
        "Diversity: 16",
        font_name="Verdana",
        font_size=fontsize[3],
        color=(0, 0, 0, 255),
        x=sizeX / 2 + squareSize * 1.0,
        y=borderY + squareSize * 4.5,
        anchor_x="left",
        anchor_y="top",
        batch=nBatch,
    )
    blockNames["60"] = pyglet.text.Label(
        "Diversity: 60",
        font_name="Verdana",
        font_size=fontsize[3],
        color=(0, 0, 0, 255),
        x=sizeX / 2 - squareSize * 2,
        y=borderY + squareSize * 9,
        anchor_x="left",
        anchor_y="top",
        batch=nBatch,
    )


def layout_real(fontsize):
    labels["time"] = pyglet.text.Label(
        "",
        font_name="Verdana",
        font_size=fontsize[0],
        italic=True,
        color=FONT_COLOR,
        x=borderX * 4,
        y=sizeY - borderY * 13.5,
        anchor_x="left",
        anchor_y="top",
        batch=nBatch,
    )
    allPlotCodes = pickle.load(open("sources/plotNames.p", "rb"))
    block4 = [x for x in allPlotCodes if "4A" in x]
    block3 = [x for x in allPlotCodes if "3A" in x]
    block2 = [x for x in allPlotCodes if "2A" in x]
    block1 = [x for x in allPlotCodes if "1A" in x]
    block3.append("3A18")  # empty plot
    block3.sort()
    X = sizeX / 2 - squareSize * 1.4
    Y = borderY
    counter = 0
    for plot in block4:
        squares[plot] = shapes.BorderedRectangle(
            X, Y, squareSize, squareSize, border=2, color=GREY, batch=batch
        )
        extreme[plot] = shapes.BorderedRectangle(
            X,
            Y,
            squareSize,
            squareSize,
            border=10,
            color=GREY,
            batch=batch,
            border_color=RED,
        )
        extreme[plot].visible = False
        naming[plot] = pyglet.text.Label(
            plot,
            font_name="Verdana",
            font_size=fontsize[1],
            color=FONT_COLOR,
            x=X + namingBorder,
            y=Y,
            anchor_x="left",
            anchor_y="bottom",
            batch=nBatch,
        )
        blockValues[plot] = pyglet.text.Label(
            "",
            font_name="Verdana",
            font_size=fontsize[2],
            color=FONT_COLOR,
            x=X + 0.5 * squareSize,
            y=Y + 0.5 * squareSize,
            anchor_x="center",
            anchor_y="center",
            batch=nBatch,
        )
        if counter < 3:
            Y += squareSize
            counter += 1
        else:
            Y = borderY
            X -= squareSize + distanceX
            counter = 0
    X = sizeX / 2 + squareSize * 1
    Y = borderY
    counter = 0
    for plot in block3:
        squares[plot] = shapes.BorderedRectangle(
            X, Y, squareSize, squareSize, border=2, color=GREY, batch=batch
        )
        extreme[plot] = shapes.BorderedRectangle(
            X,
            Y,
            squareSize,
            squareSize,
            border=10,
            color=GREY,
            batch=batch,
            border_color=RED,
        )
        extreme[plot].visible = False
        naming[plot] = pyglet.text.Label(
            plot,
            font_name="Verdana",
            font_size=fontsize[1],
            color=FONT_COLOR,
            x=X + namingBorder,
            y=Y,
            anchor_x="left",
            anchor_y="bottom",
            batch=nBatch,
        )
        blockValues[plot] = pyglet.text.Label(
            "",
            font_name="Verdana",
            font_size=fontsize[2],
            color=FONT_COLOR,
            x=X + 0.5 * squareSize,
            y=Y + 0.5 * squareSize,
            anchor_x="center",
            anchor_y="center",
            batch=nBatch,
        )
        if counter < 11:
            Y += squareSize
            counter += 1
        else:
            Y = borderY
            X -= squareSize + distanceX
            counter = 0
    X = sizeX / 2 + squareSize * 3.25
    Y = borderY + squareSize
    counter = 0
    for plot in block2:
        squares[plot] = shapes.BorderedRectangle(
            X, Y, squareSize, squareSize, border=2, color=GREY, batch=batch
        )
        extreme[plot] = shapes.BorderedRectangle(
            X,
            Y,
            squareSize,
            squareSize,
            border=10,
            color=GREY,
            batch=batch,
            border_color=RED,
        )
        extreme[plot].visible = False
        naming[plot] = pyglet.text.Label(
            plot,
            font_name="Verdana",
            font_size=fontsize[1],
            color=FONT_COLOR,
            x=X + namingBorder,
            y=Y,
            anchor_x="left",
            anchor_y="bottom",
            batch=nBatch,
        )
        blockValues[plot] = pyglet.text.Label(
            "",
            font_name="Verdana",
            font_size=fontsize[2],
            color=FONT_COLOR,
            x=X + 0.5 * squareSize,
            y=Y + 0.5 * squareSize,
            anchor_x="center",
            anchor_y="center",
            batch=nBatch,
        )
        if counter < 10:
            Y += squareSize
            counter += 1
        else:
            Y = borderY + squareSize
            X -= squareSize + distanceX
            counter = 0
    X = sizeX / 2 + squareSize * 5.5
    Y = borderY + squareSize * 2
    counter = 0
    for plot in block1:
        squares[plot] = shapes.BorderedRectangle(
            X, Y, squareSize, squareSize, border=2, color=GREY, batch=batch
        )
        extreme[plot] = shapes.BorderedRectangle(
            X,
            Y,
            squareSize,
            squareSize,
            border=10,
            color=GREY,
            batch=batch,
            border_color=RED,
        )
        extreme[plot].visible = False
        naming[plot] = pyglet.text.Label(
            plot,
            font_name="Verdana",
            font_size=fontsize[1],
            color=FONT_COLOR,
            x=X + namingBorder,
            y=Y,
            anchor_x="left",
            anchor_y="bottom",
            batch=nBatch,
        )
        blockValues[plot] = pyglet.text.Label(
            "",
            font_name="Verdana",
            font_size=fontsize[2],
            color=FONT_COLOR,
            x=X + 0.5 * squareSize,
            y=Y + 0.5 * squareSize,
            anchor_x="center",
            anchor_y="center",
            batch=nBatch,
        )
        if counter < 10:
            Y += squareSize
            counter += 1
        else:
            Y = borderY + squareSize * 2
            X -= squareSize + distanceX
            counter = 0
    extreme["3A18"].visible = False
    blockNames["4"] = pyglet.text.Label(
        "Block 4",
        font_name="Verdana",
        font_size=fontsize[3],
        color=(0, 0, 0, 255),
        x=sizeX / 2 - (squareSize * 5.5),
        y=borderY + 4 * squareSize,
        anchor_x="left",
        anchor_y="bottom",
        batch=nBatch,
    )
    blockNames["3"] = pyglet.text.Label(
        "Block 3",
        font_name="Verdana",
        font_size=fontsize[3],
        color=(0, 0, 0, 255),
        x=sizeX / 2,
        y=borderY + 12 * squareSize,
        anchor_x="left",
        anchor_y="bottom",
        batch=nBatch,
    )
    blockNames["2"] = pyglet.text.Label(
        "Block 2",
        font_name="Verdana",
        font_size=fontsize[3],
        color=(0, 0, 0, 255),
        x=sizeX / 2 + (squareSize * 2.25),
        y=borderY + 1 * squareSize,
        anchor_x="left",
        anchor_y="top",
        batch=nBatch,
    )
    blockNames["1"] = pyglet.text.Label(
        "Block 1",
        font_name="Verdana",
        font_size=fontsize[3],
        color=(0, 0, 0, 255),
        x=sizeX / 2 + (squareSize * 4.5),
        y=borderY + 2 * squareSize,
        anchor_x="left",
        anchor_y="top",
        batch=nBatch,
    )


def layout_block_2(fontsize):
    labels["time"] = pyglet.text.Label(
        "",
        font_name="Verdana",
        font_size=fontsize[0],
        italic=True,
        color=FONT_COLOR,
        x=borderX * 4,
        y=sizeY - borderY * 13.5,
        anchor_x="left",
        anchor_y="top",
        batch=nBatch,
    )
    data = pd.read_csv("sources/field_diversity.csv")
    # empty plots are displayed as zero also. 
    data.loc[data["diversity level"] == -1, "diversity level"] = 0
    blocks = {}
    for plot in data["plotcode"].values:
        divLevel = data.loc[data["plotcode"] == plot, "diversity level"].values[0]
        if "2A" in plot:
            if divLevel in blocks.keys():
                blocks[divLevel].append(plot)
            else:
                blocks[divLevel] = [plot]
    placement = {
        0: [borderY + squareSize * 10.5, sizeX / 2 - squareSize * 1.0],
        1: [borderY + squareSize * 9, sizeX / 2 - squareSize * 1.0],
        2: [borderY + squareSize * 7.5, sizeX / 2 - squareSize * 1.0],
        4: [borderY + squareSize * 6, sizeX / 2 - squareSize * 1.0],
        8: [borderY + squareSize * 4.5, sizeX / 2 - squareSize * 1.0],
        16: [borderY + squareSize * 3, sizeX / 2 - squareSize * 1.0],
        60: [borderY + squareSize * 1.5, sizeX / 2 - squareSize * 1.0],
    }
    
    for group in placement.keys():
        X = placement[group][1]
        Y = placement[group][0]
        counter = 0
        for plot in blocks[group]:
            squares[plot] = shapes.BorderedRectangle(
                X, Y, squareSize, squareSize, border=2, color=GREY, batch=batch
            )
            extreme[plot] = shapes.BorderedRectangle(
                X,
                Y,
                squareSize,
                squareSize,
                border=10,
                color=GREY,
                batch=batch,
                border_color=RED,
            )
            extreme[plot].visible = False
            naming[plot] = pyglet.text.Label(
                plot,
                font_name="Verdana",
                font_size=fontsize[1],
                color=FONT_COLOR,
                x=X + namingBorder,
                y=Y,
                anchor_x="left",
                anchor_y="bottom",
                batch=nBatch,
            )
            blockValues[plot] = pyglet.text.Label(
                "",
                font_name="Verdana",
                font_size=fontsize[2],
                color=FONT_COLOR,
                x=X + 0.5 * squareSize,
                y=Y + 0.5 * squareSize,
                anchor_x="center",
                anchor_y="center",
                batch=nBatch,
            )
            X += squareSize + distanceX
    blockNames["0"] = pyglet.text.Label(
        "Diversity: 0",
        font_name="Verdana",
        font_size=fontsize[3],
        color=(0, 0, 0, 255),
        x=sizeX / 2 - squareSize * 1,
        y=borderY + squareSize * 10.5,
        anchor_x="left",
        anchor_y="top",
        batch=nBatch,
    )
    blockNames["1"] = pyglet.text.Label(
        "Diversity: 1",
        font_name="Verdana",
        font_size=fontsize[3],
        color=(0, 0, 0, 255),
        x=sizeX / 2 - squareSize * 1,
        y=borderY + squareSize * 9,
        anchor_x="left",
        anchor_y="top",
        batch=nBatch,
    )
    blockNames["2"] = pyglet.text.Label(
        "Diversity: 2",
        font_name="Verdana",
        font_size=fontsize[3],
        color=(0, 0, 0, 255),
        x=sizeX / 2 - squareSize * 1,
        y=borderY + squareSize * 7.5,
        anchor_x="left",
        anchor_y="top",
        batch=nBatch,
    )
    blockNames["4"] = pyglet.text.Label(
        "Diversity: 4",
        font_name="Verdana",
        font_size=fontsize[3],
        color=(0, 0, 0, 255),
        x=sizeX / 2 - squareSize * 1,
        y=borderY + squareSize * 6.0,
        anchor_x="left",
        anchor_y="top",
        batch=nBatch,
    )
    blockNames["8"] = pyglet.text.Label(
        "Diversity: 8",
        font_name="Verdana",
        font_size=fontsize[3],
        color=(0, 0, 0, 255),
        x=sizeX / 2 - squareSize * 1,
        y=borderY + squareSize * 4.5,
        anchor_x="left",
        anchor_y="top",
        batch=nBatch,
    )
    blockNames["16"] = pyglet.text.Label(
        "Diversity: 16",
        font_name="Verdana",
        font_size=fontsize[3],
        color=(0, 0, 0, 255),
        x=sizeX / 2 - squareSize * 1,
        y=borderY + squareSize * 3,
        anchor_x="left",
        anchor_y="top",
        batch=nBatch,
    )
    blockNames["60"] = pyglet.text.Label(
        "Diversity: 60",
        font_name="Verdana",
        font_size=fontsize[3],
        color=(0, 0, 0, 255),
        x=sizeX / 2 - squareSize * 1,
        y=borderY + squareSize * 1.5,
        anchor_x="left",
        anchor_y="top",
        batch=nBatch,
    )
    allPlotCodes = pickle.load(open("sources/plotNames.p", "rb"))
    block2 = [x for x in allPlotCodes if "2A" in x]
    X = sizeX / 2 + squareSize * 5.5
    Y = borderY + squareSize * 1
    counter = 0
    for plot in block2:
        squares["D_" + plot] = shapes.BorderedRectangle(
            X, Y, squareSize, squareSize, border=2, color=GREY, batch=batch
        )
        extreme["D_" + plot] = shapes.BorderedRectangle(
            X,
            Y,
            squareSize,
            squareSize,
            border=10,
            color=GREY,
            batch=batch,
            border_color=RED,
        )
        extreme["D_" + plot].visible = False
        naming["D_" + plot] = pyglet.text.Label(
            plot,
            font_name="Verdana",
            font_size=fontsize[1],
            color=FONT_COLOR,
            x=X + namingBorder,
            y=Y,
            anchor_x="left",
            anchor_y="bottom",
            batch=nBatch,
        )
        blockValues["D_" + plot] = pyglet.text.Label(
            "",
            font_name="Verdana",
            font_size=fontsize[2],
            color=FONT_COLOR,
            x=X + 0.5 * squareSize,
            y=Y + 0.5 * squareSize,
            anchor_x="center",
            anchor_y="center",
            batch=nBatch,
        )
        if counter < 10:
            Y += squareSize
            counter += 1
        else:
            Y = borderY + squareSize
            X -= squareSize + distanceX
            counter = 0
    blockNames["2"] = pyglet.text.Label(
        "Block 2",
        font_name="Verdana",
        font_size=fontsize[2],
        color=(0, 0, 0, 255),
        x=sizeX / 2 + (squareSize * 4.5),
        y=borderY + 1 * squareSize,
        anchor_x="left",
        anchor_y="top",
        batch=nBatch,
    )
    blockNames["D_2"] = pyglet.text.Label(
        "Block 2 grouped",
        font_name="Verdana",
        font_size=fontsize[2],
        color=(0, 0, 0, 255),
        x=sizeX / 2 - (squareSize * 1),
        y=borderY + 1 * squareSize * 12.25,
        anchor_x="left",
        anchor_y="top",
        batch=nBatch,
    )
    # something doesnt woork here
    dividers["line"] = shapes.Line(
        sizeX / 2 + squareSize * 3.75,
        borderY + squareSize * 13,
        sizeX / 2 + squareSize * 3.75,
        borderY + squareSize * 0,
        color=(0, 0, 0),
        batch=nBatch,
        width=3,
    )
