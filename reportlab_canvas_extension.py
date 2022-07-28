#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Wyatt Geckle
# 7/28/22

"""Define extra methods or extend functionality of existing ones in the
   ReportLab Canvas class.
  
   All docstrings are directly copied, slightly modified, or
   otherwise derived from those in the ReportLab API Reference.
   https://www.reportlab.com/docs/reportlab-reference.pdf
  
   Tested in ReportLab version 3.6.10
   https://pypi.org/project/reportlab/
"""


import math

from reportlab.pdfgen.canvas import Canvas as StockCanvas
from reportlab.lib.utils import ImageReader
from reportlab.graphics.charts.textlabels import _text2Path


class Canvas(StockCanvas):
    """This is an extended ReportLab Canvas with additional features
    not provided by the official class.  Additions include:
        - drawing arrows
        - drawing lines based on polar coordinates
        - drawing rectangles based on their endpoints
        - proper anchoring of images and text."""
    
    def __init__(self, filename: str, **kwargs):
        """Initialize a canvas object and save the font size for
        later use."""
        
        super().__init__(filename, **kwargs)
        
        self.fontSize = 12  # Default ReportLab font is Helvetica 12
        
    def arrow(
            self, x1: float, y1: float, x2: float, y2: float,
            arrowheadlength: float = None):
        """Draw an arrow from (x1, y1) to (x2, y2) with arrowhead at
        (x2, y2).
        
        Arrowhead size is about 1/12 of the arrow length by default.
        
        Due to issues with the default end, the line cap is always
        round."""
        
        self.saveState()
        
        self.setLineCap(1)
        
        self.line(x1, y1, x2, y2)
        
        if arrowheadlength is None:
            arrowheadlength = 0.083333 * math.sqrt((x2 - x1)*(x2 - x1)
                                                   + (y2 - y1)*(y2 - y1))
        theta = math.atan2(y2 - y1, x2 - x1)
        
        self.lineAngle(x2, y2, arrowheadlength, theta + math.radians(150),
                       radians=True)
        self.lineAngle(x2, y2, arrowheadlength, theta - math.radians(150),
                       radians=True)
                       
        self.restoreState()
        
    def arrowAngle(
            self, x1: float, y1: float, r: float, theta: float,
            radians: bool = False,
            arrowheadlength: float = None) -> (float, float):
        """Draw an arrow from (x1, y1) to polar coordinates
        (r, theta) with arrowhead at (r, theta).
        
        theta is in degrees by default.
        
        Arrowhead size is about 1/12 of the arrow length by default.
        
        Due to issues with the default end, the line cap is always
        round.

        Returns the x and y coordinates of the arrow endpoint."""
        
        self.saveState()
        
        self.setLineCap(1)
        
        if not radians:
            theta = math.radians(theta)
            
        x2, y2 = self.lineAngle(x1, y1, r, theta, radians=True)
        
        if arrowheadlength is None:
            arrowheadlength = 0.083333 * math.sqrt((x2 - x1)*(x2 - x1)
                                                   + (y2 - y1)*(y2 - y1))
        
        self.lineAngle(x2, y2, arrowheadlength, theta + math.radians(150),
                       radians=True)
        self.lineAngle(x2, y2, arrowheadlength, theta - math.radians(150),
                       radians=True)
                       
        self.restoreState()

        return x2, y2

    def arrowPolar(
            self, x: float, y: float, r1: float, theta1: float,
            r2: float, theta2: float, radians: bool = False,
            arrowheadlength: float = None) -> (float, float):
        """Draw a line segment from polar coordinates (r1, theta1) to
        (r1 + dr, theta1 + dtheta), with (x, y) being the reference point.

        Angles are in degrees by default.
        
        Arrowhead size is about 1/12 of the arrow length by default.
        
        Returns the x and y coordinates of (r2, theta2)."""

        if not radians:
            theta1 = math.radians(theta1)
            theta2 = math.radians(theta2)

        x1 = r1*math.cos(theta1) + x
        y1 = r1*math.sin(theta1) + y

        x2 = r2*math.cos(theta2) + x
        y2 = r2*math.sin(theta2) + y

        self.arrow(x1, y1, x2, y2, arrowheadlength=arrowheadlength)

        return x2, y2
    
    def arrowPolarRelative(
            self, x: float, y: float, r1: float, theta1: float,
            dr: float, dtheta: float, radians: bool = False,
            arrowheadlength: float = None) -> (float, float):
        """Draw an arrow from polar coordinates (r1, theta1) to
        (r2, theta2), with (x, y) being the reference point.

        Angles are in degrees by default.
        
        Arrowhead size is about 1/12 of the arrow length by default.
        
        Returns the x and y coordinates of the arrow endpoint."""

        if not radians:
            theta1 = math.radians(theta1)
            theta2 = math.radians(theta2)

        x1 = r1*math.cos(theta1) + x
        y1 = r1*math.sin(theta1) + y

        return self.arrowAngle(x1, y1, dr, dtheta, radians=True,
                               arrowheadlength=arrowheadlength)

    def arrowRelative(
            self, x1: float, y1: float, dx: float, dy: float,
            arrowheadlength: float = None) -> (float, float):
        """Draw an arrow from (x1, y1) to (x1 + dx, y1 + dy) with
        arrowhead at (x1 + dx, y1 + dy).
        
        Arrowhead size is about 1/12 of the arrow length by default.
        
        Due to issues with the default end, the line cap is always
        round.

        Returns the x and y coordinates of the arrow endpoint."""

        x2 = x1 + dx
        y2 = y1 + dy

        self.arrow(x1, y1, x2, y2, arrowheadlength=arrowheadlength)

        return x2, y2
                   
    def drawAnchoredImage(
            self, image: (ImageReader, str), x: float, y: float,
            width: float = None, height: float = None, mask: list = None,
            anchor: str = 'c') -> (int, int):
        """Draws the image (ImageReader object or filename) as
        specified.
        
        "image" may be an image filename or an ImageReader object.
        
        x and y define the origin of the image you wish to draw.
        
        If width and height are not given, the width and height of the
        image in pixels is used at a scale of 1 point to 1 pixel.

        If either width or height are given, the image will be scaled
        based on the given dimention.

        If width and height are given, the image will be stretched to
        fill the given rectangle bounded by (x, y, x+width, y-height).

        If you supply negative widths and/or heights, it inverts them.
        
        The method returns the width and height of the underlying image,
        since this is often useful for layout algorithms and saves you
        work if you have not specified them yourself.
        
        The mask parameter supports transparent backgrounds.  It takes
        6 numbers and defines the range of RGB values which will be
        masked out or treated as transparent.  For example with
        [0,2,40,42,136,139], it will mask out any pixels with a Red
        value from 0-2, Green from 40-42 and Blue from 136-139
        (on a scale of 0-255).
        
        The origin of the image is placed at an anchor point:
            nw   n   ne
            w    c    e
            sw   s   se"""
        
        if isinstance(image, str):
            image = ImageReader(image)
            
        img_width, img_height = image.getSize()
        
        if width is None and height is None:
            width = img_width
            height = img_height
        elif width is None and height is not None:
            width = height * img_width // img_height
        elif height is None and width is not None:
            height = width * img_height // img_width
        
        if anchor[-1] == 'w':
            x_offset = 0
        elif anchor[-1] == 'e':
            x_offset = width
        else:
            x_offset = 0.5 * width
        
        if anchor[0] == 's':
            y_offset = 0
        elif anchor[0] == 'n':
            y_offset = height
        else:
            y_offset = 0.5 * height
        
        return self.drawImage(image, x - x_offset, y - y_offset,
                              width=width, height=height, mask=mask)
    
    def drawAnchoredString(
            self, x: float, y: float, text: str, anchor: str = 'c', **kwargs):
        """Draws a string in the current text styles with alignment
        defined by the anchor point.
        
        The origin of the text is placed at an anchor point:
            nw   n   ne
            w    c    e
            sw   s   se"""
        
        text_dims = _text2Path(text, fontSize=self.fontSize).getBounds()
        text_height = text_dims[3] - text_dims[1]
        
        if anchor[0] == 's':
            y_offset = 0
        elif anchor[0] == 'n':
            y_offset = text_height
        else:
            y_offset = 0.5 * text_height
            
        if anchor[-1] == 'w':
            self.drawString(x, y - y_offset, text, **kwargs)
            return
            
        if anchor[-1] == 'e':
            self.drawRightString(x, y - y_offset, text, **kwargs)
            return
            
        self.drawCentredString(x, y - y_offset, text, **kwargs)
                   
    def lineAngle(
            self, x1: float, y1: float, r: float, theta: float,
            radians: bool = False) -> (float, float):
        """Draw a line segment from (x1, y1) to polar coordinates
        (r, theta).
        
        theta is in degrees by default.

        Returns the x and y coordinates of the second point."""
        
        if not radians:
            theta = math.radians(theta)
            
        x2 = r*math.cos(theta) + x1
        y2 = r*math.sin(theta) + y1
        
        self.line(x1, y1, x2, y2)

        return x2, y2

    def lineAngleDashed(
            self, x1: float, y1: float, r: float, theta: float,
            radians: bool = False, num_dashes: int = None) -> (float, float):
        """Draw a dashed line from (x1, y1) to polar coordinates
        (r, theta)

        theta is in degrees by default.

        num_dashes depends on line length by default.

        Returns the x and y coordinates of the second point."""

        if not radians:
            theta = math.radians(theta)

        if num_dashes is None:
            # num_dashes should be at least 2.
            num_dashes = int(abs(r) / 30) + 2

        dash_length = r / (num_dashes*2 - 1)
        dash_base = dash_length * math.cos(theta)
        dash_height = dash_length * math.sin(theta)

        for i in range(num_dashes):
            self.lineRelative(2*i*dash_base + x1,
                              2*i*dash_height + y1,
                              dash_base,
                              dash_height)

        return ((2*num_dashes - 1)*dash_base + x1,
                (2*num_dashes - 1)*dash_height + y1)

    def lineDashed(
            self, x1: float, y1: float, x2: float, y2: float,
            num_dashes: int = None):
        """Draw a dashed line from (x1, y1) to (x2, y2).

        num_dashes depends on line length by default."""

        if num_dashes is None:
            length = math.sqrt((x2 - x1)*(x2 - x1) + (y2 - y1)*(y2 - y1))
            # num_dashes should be at least 2.
            num_dashes = int(length / 30) + 2

        dash_base = (x2 - x1) / (num_dashes*2 - 1)
        dash_height = (y2 - y1) / (num_dashes*2 - 1)

        for i in range(num_dashes):
            self.lineRelative(2*i*dash_base + x1,
                              2*i*dash_height + y1,
                              dash_base,
                              dash_height)

    def linePolar(
            self, x: float, y: float, r1: float, theta1: float,
            r2: float, theta2: float, radians: bool = False) -> (float, float):
        """Draw a line segment from polar coordinates (r1, theta1) to
        (r2, theta2), with (x, y) being the reference point.

        Angles are in degrees by default.
        
        Returns the x and y coordinates of (r2, theta2)."""

        if not radians:
            theta1 = math.radians(theta1)
            theta2 = math.radians(theta2)

        x1 = r1*math.cos(theta1) + x
        y1 = r1*math.sin(theta1) + y

        x2 = r2*math.cos(theta2) + x
        y2 = r2*math.sin(theta2) + y

        self.line(x1, y1, x2, y2)

        return x2, y2

    def linePolarDashed(
            self, x: float, y: float, r1: float, theta1: float,
            r2: float, theta2: float, radians: bool = False,
            num_dashes: int = None) -> (float, float):
        """Draw a dashed line from polar coordinates (r1, theta1) to
        (r2, theta2), with (x, y) being the reference point.

        Angles are in degrees by default.

        num_dashes depends on line length by default.

        Returns the x and y coordinates of (r2, theta2)."""

        if not radians:
            theta1 = math.radians(theta1)
            theta2 = math.radians(theta2)

        x1 = r1*math.cos(theta1) + x
        y1 = r1*math.sin(theta1) + y

        x2 = r2*math.cos(theta2) + x
        y2 = r2*math.sin(theta2) + y

        self.lineDashed(x1, y1, x2, y2, num_dashes=num_dashes)

        return x2, y2
    
    def linePolarRelative(
            self, x: float, y: float, r1: float, theta1: float,
            dr: float, dtheta: float, radians: bool = False) -> (float, float):
        """Draw a line segment from polar coordinates (r1, theta1) to
        (r1 + dr, theta1 + dtheta), with (x, y) being the reference
        point.

        Angles are in degrees by default.
        
        Returns the x and y coordinates of the second point."""

        if not radians:
            theta1 = math.radians(theta1)
            dtheta = math.radians(dtheta)

        x1 = r1*math.cos(theta1) + x
        y1 = r1*math.sin(theta1) + y

        return self.lineAngle(x1, y1, dr, dtheta, radians=True)

    def linePolarRelativeDashed(
            self, x: float, y: float, r1: float, theta1: float,
            dr: float, dtheta: float, radians: bool = False,
            num_dashes: int = None) -> (float, float):
        """Draw a line segment from polar coordinates (r1, theta1) to
        (r1 + dr, theta1 + dtheta), with (x, y) being the reference
        point.

        Angles are in degrees by default.
        
        num_dashes depends on line length by default.
        
        Returns the x and y coordinates of the second point."""
        
        if not radians:
            theta1 = math.radians(theta1)
            dtheta = math.radians(dtheta)

        x1 = r1*math.cos(theta1) + x
        y1 = r1*math.sin(theta1) + y

        return self.lineAngleDashed(x1, y1, dr, dtheta, radians=True,
                                    num_dashes=num_dashes)

    def lineRelative(
            self, x1: float, y1: float,
            dx: float, dy: float) -> (float, float):
        """Draw a line segment from (x1, y1) to (x1 + dx, y1 + dy).

        Returns the x and y coordinates of the second point."""

        x2 = x1 + dx
        y2 = y1 + dy

        self.line(x1, y1, x2, y2)

        return x2, y2

    def lineRelativeDashed(
            self, x1: float, y1: float, dx: float, dy: float,
            num_dashes: int = None) -> (float, float):
        """Draw a dashed line from (x1, y1) to (x1 + dx, y1 + dy).

        num_dashes depends on line length by default.

        Returns the x and y coordinates of the second point."""

        x2 = x1 + dx
        y2 = y1 + dy

        self.lineDashed(x1, y1, x2, y2, num_dashes=num_dashes)

        return x2, y2
        
    def rectCoords(
            self, x1: float, y1: float, x2: float, y2: float,
            stroke: bool = True, fill: bool = False):
        """Draw a rectangle with lower left corner at (x1, y1) and upper
        right corner at (x2, y2)."""
        
        self.rect(x1, y1, x2 - x1, y2 - y1, stroke=stroke, fill=fill)
        
    def setFont(self, psfontname: str, size: float, **kwargs):
        """Sets the font. If leading not specified, defaults to 1.2 x
        font size. Raises a readable exception if an illegal font
        is supplied. Font names are case-sensitive! Keeps track
        of font name and size for metrics.
        
        Saves font size to canvas object."""
        
        super().setFont(psfontname, size, **kwargs)
        
        self.fontSize = size
        
    def setFontSize(self, size: float = None, **kwargs):
        """Sets font size or leading without knowing the font face.
        
        Saves font size to canvas object."""
        
        super().setFontSize(size=size, **kwargs)
        
        if size is not None:
            self.fontSize = size

