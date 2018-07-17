from qtpy import QT_VERSION
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

QT5 = QT_VERSION[0] == '5'  # NOQA

from labelme.lib import labelValidator
from labelme.lib import newIcon


# TODO(unknown):
# - Calculate optimal position so as not to go out of screen area.


class LabelQLineEdit(QtWidgets.QLineEdit):

    def setListWidget(self, list_widget):
        self.list_widget = list_widget

	# 方向键选择 label
    def keyPressEvent(self, e):
        if e.key() in [QtCore.Qt.Key_Up, QtCore.Qt.Key_Down]:
            self.list_widget.keyPressEvent(e)
        else:
            super(LabelQLineEdit, self).keyPressEvent(e)


class LabelDialog(QtWidgets.QDialog):

    def __init__(self, text="Enter object label", parent=None, labels=None,
                 sort_labels=True, show_text_field=True):
        super(LabelDialog, self).__init__(parent)
        # label: labelLabel+edit
        self.labelLabel = QtWidgets.QLabel('Label:', self)
        self.edit = LabelQLineEdit()
        self.edit.setPlaceholderText(text)	# 默认提示语
        self.edit.setValidator(labelValidator())  # 输入检查
        # editingFinished: the Return or Enter key is pressed or the line edit loses focus
        # postProcess 检查有效性，然后设为edit.text()
        self.edit.editingFinished.connect(self.postProcess)
        subLayout1 = QtWidgets.QHBoxLayout()
        subLayout1.addWidget(self.labelLabel)
        subLayout1.addWidget(self.edit)
        layout = QtWidgets.QVBoxLayout()
        if show_text_field:
            layout.addLayout(subLayout1)
        # language: languageLabel+language
        self.languageLabel = QtWidgets.QLabel('Language:', self)
        self.language = QtWidgets.QComboBox(self)
        self.language.addItem('Chinese')
        self.language.addItem('English')
        self.language.addItem('Other')
        subLayout2 = QtWidgets.QHBoxLayout()
        subLayout2.addWidget(self.languageLabel)
        subLayout2.addWidget(self.language)
        layout.addLayout(subLayout2)
        # quanlity: quanlityLabel+quanlity
        self.quanlityLabel = QtWidgets.QLabel('Quanlity:', self)
        self.quanlity = QtWidgets.QComboBox(self)
        self.quanlity.addItem('print')
        self.quanlity.addItem('write')
        self.quanlity.addItem('other')
        subLayout3 = QtWidgets.QHBoxLayout()
        subLayout3.addWidget(self.quanlityLabel)
        subLayout3.addWidget(self.quanlity)
        layout.addLayout(subLayout3)
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
        if hasattr(text, 'strip'):
            text = text.strip()
        else:
            text = text.trimmed()
        if text:
            self.accept()

    def postProcess(self):
        text = self.edit.text()
        if hasattr(text, 'strip'):
            text = text.strip()
        else:
            text = text.trimmed()
        self.edit.setText(text)

    def popUp(self, text=None, move=True):
        # if text is None, the previous label in self.edit is kept
        if text is None:
            text = self.edit.text()
        self.edit.setText(text)
        self.edit.setSelection(0, len(text))  # 全选
        items = self.labelList.findItems(text, QtCore.Qt.MatchFixedString)
        if items:
            assert len(items) == 1
            self.labelList.setCurrentItem(items[0])
            row = self.labelList.row(items[0])
            self.edit.completer().setCurrentRow(row)
        self.edit.setFocus(QtCore.Qt.PopupFocusReason)  # 可直接编辑
        if move:
            self.move(QtGui.QCursor.pos())  # 移动鼠标到ok
        return self.edit.text() if self.exec_() else None   # 返回编辑过的label
