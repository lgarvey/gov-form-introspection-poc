import pymupdf
from pymupdf.utils import getColor
from pymupdf import TEXT_ALIGN_CENTER
from collections import defaultdict

doc = pymupdf.open("SA100.pdf")

for page_num, page in enumerate(doc, 1):
    # iterate over each page

    output_pdf_name = f"SA100-page-{page_num}.pdf"

    paths = page.get_drawings()

    outpdf = pymupdf.open()
    outpage = outpdf.new_page(width=page.rect.width, height=page.rect.height)
    shape = outpage.new_shape()  # make a drawing canvas for the output page

    # these are used for highighting text box groups
    colours = [
        "red",
        "blue",
        "green",
        "orange",
        "purple",
        "pink",
        "black",
    ]

    # group the boxes by their y0 coord.  This will need some better logic to group only boxes that are close together horizdontally (maybe group by right or left column?)
    # as we'll encounter text boxes that are vertically aligned, but belong to different fields.
    y_grouped_rects = defaultdict(list)

    # find all the input rectangles and group
    for path in paths:
        # each text input box is in its own path
        user_input_rects = []
        for item in path["items"]:
            if item[0] == "re": # collect rectangles - operator "re"
                obj = item[1]
                if int(obj.width) == 13:    # this seems to be the width of input boxes on the SA100 form
                    y_grouped_rects[obj.y0].append(obj)


    # render the boxes on the page with a separate colour for each group
    for _, rects in y_grouped_rects.items():
        colour = getColor(colours[colour_index])
        colour_index = 0 if colour_index == len(colours) - 1 else colour_index + 1

        for index, rect in enumerate(rects):
            shape.draw_rect(rect)

            shape.finish(
                fill=(1.0, 1.0, 1.0),  # fill color
                color=colour,
                dashes='[] 0',  # line dashing
                even_odd=False,  # control color of overlaps
                closePath=False,  # whether to connect last and first point
                lineJoin=1, # how line joins should look like
                lineCap=1, # how line ends should look like
                # -------
                # reading this properties could yield `None`, which will raise an error: `or 0` is added to ensure compatibility
                width=path["width"] or 0,  # line width
                stroke_opacity=1.0,  # same value for both
                fill_opacity=1.0,  # opacity parameters
            )

    # fill in text
    colour_index = 0
    for _, rects in y_grouped_rects.items():
        for index, rect in enumerate(rects, 1):
            # https://pymupdf.readthedocs.io/en/latest/shape.html#Shape.insert_textbox
            shape.insert_textbox(rect, str(index), fontsize=9, align=TEXT_ALIGN_CENTER, border_width=0)

    shape.finish(color=getColor("black"), fill=getColor("red"))

    shape.commit()
    outpdf.save(output_pdf_name)
