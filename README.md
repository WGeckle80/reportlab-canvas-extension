## Overview

ReportLab is a useful PDF creation API for Python.  The main website
is <https://www.reportlab.com/>, and the API reference can be found
at <https://www.reportlab.com/docs/reportlab-reference.pdf>.

Despite of the usefulness of the API, I found that the provided
`Canvas` class didn't suit my needs.  This extension class aims to
fix that by the following key inclusions:

* Drawing arrows
* Drawing lines based on polar coordinates
* Drawing rectangles based on their endpoints
* Proper anchoring of images and text

Other provided operations have been useful for my own projects.

