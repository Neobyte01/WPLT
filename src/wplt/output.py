from PIL import Image, ImageDraw, ImageFont
from itertools import pairwise
from .time_series import TimeSeries
from collections.abc import Iterable

FIGSIZE_PIXEL_SIZE = 32

BORDER_SIZE = 64
PADDING = 10

VIDEO_FPS = 24
VIDEO_LENGTH = 5

TICK_SIZE = 5   


class _ColorTable:
    COLORS = [(0, 128, 255), (255, 128, 0), (128, 255, 0)]

    def __init__(self):
        self.table = {}
        self.color_ix = 0

    def __getitem__(self, plot):
        if id(plot) not in self.table:
            self.table[id(plot)] = self.color_ix
            self.color_ix = (self.color_ix+1) % len(self.COLORS)
        
        return self.COLORS[self.table[id(plot)]]

line_color_table = _ColorTable()
scatter_color_table = _ColorTable()

def convert_to_image(figure):
    size = _get_size(figure)
    img = Image.new("RGB", size, color="white")

    _draw_c_plane(img, figure, size)

    for plot in figure.plots:
        plot_img = _plot_to_image(size, figure, plot.result, plot)
        img.paste(plot_img, (0, 0), plot_img)
    
    if figure.use_legend:
        _draw_legend(img, figure, size)

    size, img = _add_borders(img, figure, size)

    return img

def convert_to_video(figure):
    size = _get_size(figure)
    frames = [ Image.new("RGBA", size, color=(0, 0, 0, 0)) for _ in range(TimeSeries.TIME_RANGE) ]
    
    for fi in range(TimeSeries.TIME_RANGE):
        for plot in figure.plots:
            result = plot.result
            if isinstance(result, Iterable):
                result = result[fi]

            plot_img = _plot_to_image(size, figure, result, plot)
            frames[fi].paste(plot_img, (0, 0), plot_img)
    
    fg_img = Image.new("RGBA", size, color=(0, 0, 0, 0))
    if figure.use_legend:
        _draw_legend(fg_img, figure, size)
    
    bg_img = Image.new("RGB", size, color="white")
    _draw_c_plane(bg_img, figure, size)
    size, bg_img = _add_borders(bg_img, figure, size)

    video = []
    for frame in frames:
        final_frame = Image.new("RGB", size, color="white")
        final_frame.paste(bg_img, (0, 0))
        final_frame.paste(frame, (BORDER_SIZE, BORDER_SIZE), frame)
        final_frame.paste(fg_img, (BORDER_SIZE, BORDER_SIZE), fg_img)
        video.append(final_frame)

    return video

def preview_image(img):
    img.show()

def save_image(img):
    img.save("image.png")

def save_video(video):
    video[0].save("video.gif", save_all=True, append_images=video[1:])
        
def _get_size(figure):
    width = figure.figsize[0] * FIGSIZE_PIXEL_SIZE + PADDING * 2
    height = figure.figsize[1] * FIGSIZE_PIXEL_SIZE + PADDING * 2
    return (width, height)

def _add_borders(img, figure, size):
    width = size[0]+BORDER_SIZE*2
    height = size[1]+BORDER_SIZE*2

    img_pad = Image.new("RGB", (width, height), color="white")
    img_pad.paste(img, (BORDER_SIZE, BORDER_SIZE, width-BORDER_SIZE, height-BORDER_SIZE))
    _draw_borders(img_pad, figure, size)

    return (width, height), img_pad

def _plot_to_image(size, figure, coords, plot):
    img = Image.new("RGBA", size, color=(0, 0, 0, 0))
    img_draw = ImageDraw.Draw(img)
    
    X, Y = coords

    if plot.scatter:
        # Draw points as dots
        for coord in zip(X, Y):
            _draw_scatter_point(img_draw, coord, figure, plot, size, scatter_color_table[plot])
    else:
        # Draw line between neigbouring points
        for coord0, coord1 in pairwise(zip(X, Y)):
            _draw_plot_line(img_draw, coord0, coord1, figure, plot, size, line_color_table[plot])
        
    return img

def _draw_scatter_point(img_draw, coord, figure, plot, size, color):
    x, y = figure.c_plane.normalize_coord(coord)

    x *= size[0]-(2*PADDING)
    y = (1-y) * (size[1]-(2*PADDING))

    img_draw.ellipse((PADDING+x-plot.width, PADDING+y-plot.width, PADDING+x+plot.width, PADDING+y+plot.width), fill=color)

def _draw_plot_line(img_draw, coord0, coord1, figure, plot, size, color):
    x0, y0 = figure.c_plane.normalize_coord(coord0)
    x1, y1 = figure.c_plane.normalize_coord(coord1)

    x0 *= size[0]-(2*PADDING)
    x1 *= size[0]-(2*PADDING)
    y0 = (1-y0) * (size[1]-(2*PADDING))
    y1 = (1-y1) * (size[1]-(2*PADDING))

    img_draw.line((PADDING+x0, PADDING+y0, PADDING+x1, PADDING+y1), fill=color, width=plot.width)

def _draw_c_plane(img, figure, size):
    img_draw = ImageDraw.Draw(img)

    width = size[0] - 2*PADDING
    height = size[1] - 2*PADDING

    if figure.c_plane.grid:
        for xi in figure.c_plane.get_xsteps():
            xi, _ = figure.c_plane.normalize_coord((xi, 0))
            img_draw.line((PADDING+width*xi, 0, PADDING+width*xi, size[1]), fill=(210, 210, 210), width=1)

        for yi in figure.c_plane.get_ysteps():
            _, yi = figure.c_plane.normalize_coord((0, yi))
            img_draw.line((0, PADDING+height*yi, size[0], PADDING+height*yi), fill=(210, 210, 210), width=1)
    
    x, y = figure.c_plane.normalize_coord((0, 0))

    if figure.c_plane.x_axis:
        img_draw.line((0, PADDING+height*(1-y), size[0], PADDING+height*(1-y)), fill=(70, 70, 70), width=1)

    if figure.c_plane.y_axis:
        img_draw.line((PADDING+width*x, 0, PADDING+width*x, size[1]), fill=(70, 70, 70), width=1)
    
def _draw_legend(img, figure, size):
    img_draw = ImageDraw.Draw(img)

    plot_labels = [plot.label for plot in figure.plots if plot.label]

    CHAR_HEIGHT = 9
    CHAR_WIDTH = 6
    LEGEND_MARGIN = 7
    LEGEND_HPADDING = 15
    LEGEND_VPADDING = 13

    height = LEGEND_VPADDING*(len(plot_labels)+1) + CHAR_HEIGHT*len(plot_labels)
    width = LEGEND_HPADDING*2 + max(map(len, plot_labels))*CHAR_WIDTH

    img_draw.rectangle((LEGEND_MARGIN, LEGEND_MARGIN, width+LEGEND_MARGIN, height+LEGEND_MARGIN), fill=(255, 255, 255))

    for i, (label, plot) in enumerate(zip(plot_labels, figure.plots)):
        if plot.scatter:
            color = scatter_color_table[plot]
        else:
            color = line_color_table[plot]

        img_draw.text(
            (LEGEND_HPADDING+LEGEND_MARGIN, LEGEND_MARGIN+LEGEND_VPADDING*(i+1) + CHAR_HEIGHT*i), 
            label, fill=color, anchor="lt", font=ImageFont.truetype("assets/arial.ttf", 12)
        )

    img_draw.line((LEGEND_MARGIN, LEGEND_MARGIN, LEGEND_MARGIN+width, LEGEND_MARGIN), fill=(0, 0, 0, 255), width=1)
    img_draw.line((LEGEND_MARGIN, LEGEND_MARGIN+height, LEGEND_MARGIN, LEGEND_MARGIN), fill=(0, 0, 0, 255), width=1)
    img_draw.line((LEGEND_MARGIN, LEGEND_MARGIN+height, LEGEND_MARGIN+width, LEGEND_MARGIN+height), fill=(0, 0, 0, 255), width=1)
    img_draw.line((LEGEND_MARGIN+width, LEGEND_MARGIN, LEGEND_MARGIN+width, LEGEND_MARGIN+height), fill=(0, 0, 0, 255), width=1)

def _round_steps(num, start=10, decimals=-1):
    def update_decimals(old, new):
        nonlocal decimals

        # Determined the change in factors of ten, excluding rest
        old_cmp = old // (10**(-decimals))
        new_cmp = new // (10**(-decimals))

        # Compare change in relative to a
        if old_cmp > new_cmp:
            decimals += 1
        elif old_cmp < new_cmp:
            decimals -= 1 

    # Check for negative number
    if num < 0 and start > 0:
        start *= -1

    alts = [start/5, start/2, start*2, start*5]
    
    best_alt = start
    for alt in alts:
        if abs(alt - num) < abs(best_alt - num):
            best_alt = alt

    if best_alt == start:
        return start, decimals
    else:
        update_decimals(start, best_alt)
        return _round_steps(num, best_alt, decimals)

def _draw_borders(img, figure, size):    
    img_draw = ImageDraw.Draw(img)

    top_border      = BORDER_SIZE
    bottom_border   = size[1] + BORDER_SIZE
    left_border     = BORDER_SIZE
    right_border    = size[0] + BORDER_SIZE

    img_draw.line((left_border, top_border, right_border, top_border), fill=0, width=1)
    img_draw.line((left_border, top_border, left_border, bottom_border), fill=0, width=1)
    img_draw.line((left_border, bottom_border, right_border, bottom_border), fill=0, width=1)
    img_draw.line((right_border, top_border, right_border, bottom_border), fill=0, width=1)

    if figure.title_text:
        img_draw.text((BORDER_SIZE + size[0]/2, 28), figure.title_text, font=ImageFont.truetype("assets/arial.ttf", 16), anchor="mt", fill=0)

    for x in figure.c_plane.get_xsteps():
        (x_tick, _) = figure.c_plane.normalize_coord((x, 0))
        x_tick = BORDER_SIZE+PADDING + x_tick * (size[0]-(2*PADDING))
        y_tick = bottom_border
        
        img_draw.line((x_tick, y_tick+TICK_SIZE, x_tick, y_tick), fill=0, width=1)
        img_draw.text((x_tick, y_tick+20), str(x), fill=0, anchor="ms")

    for y in figure.c_plane.get_ysteps():
        x_tick = left_border
        (_, y_tick) = figure.c_plane.normalize_coord((0, y))
        y_tick = BORDER_SIZE+PADDING + (1-y_tick) * (size[1]-(2*PADDING))

        img_draw.line((x_tick, y_tick, x_tick-TICK_SIZE, y_tick), fill=0, width=1)
        img_draw.text((x_tick-10, y_tick+5), str(y), fill=0, anchor="rs")
