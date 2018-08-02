from qtpy import QT_VERSION
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

QT5 = QT_VERSION[0] == '5'  # NOQA

from labelme.lib import labelValidator
from labelme.lib import newIcon


# TODO(unknown):
# - Calculate optimal position so as not to go out of screen area.

def wordsValidator():
    return QtGui.QRegExpValidator(QtCore.QRegExp(r'^[^ \t][0-9]+'), None)

class LabelQLineEdit(QtWidgets.QLineEdit):

    def setListWidget(self, list_widget):
        self.list_widget = list_widget

	# 方向键选择 label
    def keyPressEvent(self, e):
        if e.key() in [QtCore.Qt.Key_Up, QtCore.Qt.Key_Down]:
            self.list_widget.keyPressEvent(e)
        else:
            super(LabelQLineEdit, self).keyPressEvent(e)

class SelectBox(QtWidgets.QGroupBox):
    def __init__(self, title, *content):
        super(SelectBox, self).__init__(title)

        self.selectItem = []
        self.buttonGroup = QtWidgets.QButtonGroup()
        layout = QtWidgets.QHBoxLayout()
        for i in range(len(content)):
            self.selectItem.append(QtWidgets.QRadioButton(content[i]))
            layout.addWidget(self.selectItem[i])
            self.buttonGroup.addButton(self.selectItem[i])

        self.selectItem[0].setChecked(True)  # 默认选第一个
        self._content = content[0]
        self.buttonGroup.buttonClicked.connect(self.contentChange)
        # self.setFlat(True)

        self.setLayout(layout)
    
    def contentChange(self):
        self._content = self.buttonGroup.checkedButton().text()

    @property 
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value
        for item in self.selectItem:
            if item.text() == value:
                item.setChecked(True)


class LabelDialog(QtWidgets.QDialog):

    def __init__(self, text="Enter object label", 
                 words="Enter number of letters",
                 parent=None, labels=None,
                 sort_labels=True, show_text_field=True):
        super(LabelDialog, self).__init__(parent)

        # label: labelLabel+edit
        self.labelLabel = QtWidgets.QLabel('Label:', self)
        self.edit = LabelQLineEdit()
        self.edit.setPlaceholderText(text)	# 默认提示语
        self.edit.setValidator(labelValidator())  # 输入检查
        # editingFinished: the Return or Enter key is pressed or the line edit loses focus
        # postProcess 检查有效性，然后设为edit.text()
        self.edit.editingFinished.connect(self.editPostProcess)
        labelLayout = QtWidgets.QHBoxLayout()
        labelLayout.addWidget(self.labelLabel)
        labelLayout.addWidget(self.edit)
        layout = QtWidgets.QVBoxLayout()
        if show_text_field:
            layout.addLayout(labelLayout)

        # words
        self.wordsLabel = QtWidgets.QLabel('Letters:', self)
        self.words = QtWidgets.QLineEdit()
        self.words.setPlaceholderText(words)
        self.words.setValidator(wordsValidator())
        self.words.editingFinished.connect(self.wordsPostProcess)
        wordsLayout = QtWidgets.QHBoxLayout()
        wordsLayout.addWidget(self.wordsLabel)
        wordsLayout.addWidget(self.words)
        layout.addLayout(wordsLayout)

        # quanlity
        self.quanlity = SelectBox('Quanlity', 'High', 'Middle', 'Low')
        self.quanlity.setParent(self)
        layout.addWidget(self.quanlity)

        # language
        self.language = SelectBox('Language', 'Chinese', 'English', 'Other')
        self.language.setParent(self)
        layout.addWidget(self.language)

        # font
        self.font = SelectBox('Font', 'print', 'write')
        self.font.setParent(self)
        layout.addWidget(self.font)

        # buttons
        self.buttonBox = bb = QtWidgets.QDialogButtonBox(  # presents buttons in a layout that is appropriate to the current widget style
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal,
            self,
        )
        bb.button(bb.Ok).setIcon(newIcon('done'))
        bb.button(bb.Cancel).setIcon(newIcon('undo'))
        bb.accepted.connect(self.validate)  # 检查有效性，然后接受
        bb.rejected.connect(self.reject)
        layout.addWidget(bb)
        # label_list
        self.labelList = QtWidgets.QListWidget()
        self._sort_labels = sort_labels
        if labels:
            self.labelList.addItems(labels)
        if self._sort_labels:
            self.labelList.sortItems()
        else:
            self.labelList.setDragDropMode(
                QtGui.QAbstractItemView.InternalMove)	# ??
        self.labelList.currentItemChanged.connect(self.labelSelected)
        self.edit.setListWidget(self.labelList)  # edit 和 labelList 关联
        layout.addWidget(self.labelList)
        self.setLayout(layout)
        # completion(自动补全)
        completer = QtWidgets.QCompleter()
        completer.setCompletionMode(QtWidgets.QCompleter.InlineCompletion)
        completer.setModel(self.labelList.model())
        self.edit.setCompleter(completer)

    def addLabelHistory(self, label):
        if self.labelList.findItems(label, QtCore.Qt.MatchExactly):
            return
        self.labelList.addItem(label)
        if self._sort_labels:
            self.labelList.sortItems()

    def labelSelected(self, item):
        self.edit.setText(item.text())

    def validate(self):
        text = self.edit.text()
        word = self.words.text()
        if hasattr(text, 'strip'):
            text = text.strip()
        else:
            text = text.trimmed()
        if hasattr(word, 'strip'):
            word = word.strip()
        else:
            word = word.trimmed()
        # Make sure the letter length is not empty   
        if text and word:
            self.accept()

    def editPostProcess(self):
        text = self.edit.text()
        if hasattr(text, 'strip'):
            text = text.strip()
        else:
            text = text.trimmed()
        self.edit.setText(text)

    def wordsPostProcess(self):
        num = self.words.text()
        if hasattr(num, 'strip'):
            num = num.strip()
        else:
            num = num.trimmed()
        self.words.setText(num)

    def popUp(self, text=None, words=None, quanlity=None, language=None, font=None, move=True):
        # if text is None, the previous label in self.edit is kept
        # edit
        if text is None:
            text = self.edit.text()
        self.edit.setText(text)
        self.edit.setSelection(0, len(text))  # 全选
        # labelList
        items = self.labelList.findItems(text, QtCore.Qt.MatchFixedString)
        if items:
            assert len(items) == 1
            self.labelList.setCurrentItem(items[0])
            row = self.labelList.row(items[0])
            self.edit.completer().setCurrentRow(row)
        self.edit.setFocus(QtCore.Qt.PopupFocusReason)  # 可直接编辑
        # move
        if move:
            self.move(QtGui.QCursor.pos())  # 移动鼠标到ok
        # words
        if words is not None:
            self.words.setText(str(words))
        # quanlity
        if quanlity is not None:
            self.quanlity.content = quanlity
        # language
        if language is not None:
            self.language.content = language
        # font
        if font is not None:
            self.font.content = font
        return (self.edit.text(), int(self.words.text()), self.quanlity.content, self.language.content, self.font.content)\
            if self.exec_() else None   # 返回编辑过的label
