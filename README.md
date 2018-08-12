# labeltext
A derivative labeling software (in development) from labelme (https://github.com/wkentaro/labelme). Add special features for easier text annotation.

--------------------------

## Requirement

- Ubuntu / macOS/ Windows
- Python3
- [PyQt5](http://www.riverbankcomputing.co.uk/software/pyqt/intro)
- [OpenCV3.4](https://pypi.org/project/opencv-python/)

## Installation

We recommand you to set up the virtual environment first to prevent conflict between projects. See [virtualenv](https://virtualenv.pypa.io/en/stable/).

### Ubuntu
```bash
pip install pyqt5
pip install opencv-python
git clone https://github.com/runyuz/labeltext
tar -zxvf labeltext.tar.gz
cd labeltext
pip install -e .   # install the project

labelme    # start annotation
```

### macOS
```bash
# You can set up the virtual environment first to prevent conflict between projects (not necessary)
cd PROJECTPATH
python3 -m venv env
source env/bin/activate # activate the virtual environment
# macOS Sierra
brew install pyqt  # maybe pyqt5
pip install -e .    # in the project directory

labelme # open gui and start annotation
```

### Windows
```bash
pip install pyqt5
pip install opencv-python
# download the source code and extract
cd PROJECTPATH
pip install -e .   # install the project

labelme    # start annotation
```

## Usage
Please read readme of the original repository labelme https://github.com/wkentaro/labelme first.

+ Allow two ways of annotation: polygons and rectangle (bounding box).
+ The `shortcut` is set in the `config` file.
+ We have turned on `auto_save` (save the change to local disk automatically) and `track` function in default config.

### Basic Usage
<img src="https://github.com/runyuz/labeltext/blob/master/tutorial/Label.gif?raw=true" width="70%" />

+ Double click the label list to edit the label.

## New Features

### Shape Flags
Flags can be set for each annotation(label). It will be saved as a dictionary in the output `JSON` file. You are allowed to set multiple choices for each flag. You can edit the flags in `config`. <br>

<img src="https://github.com/runyuz/labeltext/blob/master/tutorial/LabelFlag.png?raw=true" width="33%" />

### MultiSelect
Hold `SHIFT` and click the item to select multiple items. Support deletion of all selected items. <br>

<img src="https://github.com/runyuz/labeltext/blob/master/tutorial/MultiSelect.gif?raw=true" width="70%" />

### Track
Tracking is implemented with [Lucas-Kanade Optical Flow](https://docs.opencv.org/3.1.0/d7/d8b/tutorial_py_lucas_kanade.html) and [Good Features to Track](https://docs.opencv.org/3.4/d4/d8c/tutorial_py_shi_tomasi.html). <br>

Tracking allows easier annotation for videos. If the `track` flag in `config` is set to be true (default), and there is no annotation for the current canvas, the annotation for the previous frame (previous picture you are annotating) will be tracked. If the tracking is successful, the annotation will be kept. <br>

<img src="https://github.com/runyuz/labeltext/blob/master/tutorial/Track.gif?raw=true" width="70%" />


#### Copy Selected Labels
If tracking fails for certain labels, or you add another label in one frame but the following frames have already be annotated, you can copy all the selected labels in one frame to another frame with the function `Duplicate Polygons between Frame`. If `track` flag is set, the tracking algorithm will be implemented. Even if tracking fails, the label will be kept in its previous place. <br>

<img src="https://github.com/runyuz/labeltext/blob/master/tutorial/CopyBetweenFrame.gif?raw=true" width="70%" />

### Scale
The annotation polygon can be scaled by holding `SHIFT` and moving the vertex. For a shape, the first vertex of the shape is hollow and all the other ones are solid. If you move a vertex, all vertices (except for the first one) will be scaled with respect to the first vertex. <br>

<img src="https://github.com/runyuz/labeltext/blob/master/tutorial/Scale.gif?raw=true" width="70%" />

