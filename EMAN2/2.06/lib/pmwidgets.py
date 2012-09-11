#!/usr/local/eman/2.06/Python/bin/python
# Copyright (c) 2000-2006 Baylor College of Medicine
#
# This software is issued under a joint BSD/GNU license. You may use the
# source code in this file under either license. However, note that the
# complete EMAN2 and SPARX software packages have some GPL dependencies,
# so you are responsible for compliance with the licenses of these packages
# if you opt to use BSD licensing. The warranty disclaimer below holds
# in either instance.
#
# This complete copyright notice must be included in any revised version of the
# source code. Additional authorship citations may be added, but existing
# author citations must be preserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston MA 02111-1307 USA
#
#

from EMAN2db import db_check_dict
import sys, math, weakref
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from emselector import EMSelectorDialog	# This will be replaced by something more sensible in the future
import re, os

class PMBaseWidget(QtGui.QWidget):
	""" A base widget upon which all the other PM widgets are derived """
	def __init__(self, name):
		QtGui.QWidget.__init__(self)
		
		self.postional = False
		self.name = name
		self.errormessage = None
		
	def getValue(self):
		raise NotImplementedError("Sub class must reimplemnt 'getValue' function")
	
	def setValue(self, value):
		raise NotImplementedError("Sub class must reimplemnt 'setValue' function")
		 
	def getName(self):
		return self.name
		
	def setPositional(self, position):
		self.postional = position
		
	def getPositional(self):
		return self.postional
		
	def getArgument(self):
		# If the value is None or blank then do not yeild an option. Obviously this will nver happen for Int bool or float
		if str(self.getValue()).upper() == "NONE" or str(self.getValue()).upper() == "":
			return ""
		else:
			""" There are two sorts of arguments: Posional and optional """
			if self.getPositional():
				return str(self.getValue())
			else:
				return "--%s=%s"%(self.getName(), str(self.getValue()))
	
	def setErrorMessage(self, message):
		self.errormessage = message
		
	def getErrorMessage(self):
		return self.errormessage
		
class PMIntEntryWidget(PMBaseWidget):
	""" A Widget for geting Int values. Type and range is checked """
	def __init__(self, name, value, lrange=None, urange=None, postional=False, initdefault=None):
		PMBaseWidget.__init__(self, name) 
		gridbox = QtGui.QGridLayout()
		label = QtGui.QLabel(name)
		self.intbox = QtGui.QLineEdit()
		gridbox.addWidget(label, 0, 0)
		gridbox.addWidget(self.intbox, 0, 1)
		self.setLayout(gridbox)

		self.value = None
		self.lrange = lrange
		self.urange = urange
		self.initdefault = initdefault
		self.setValue(value)
		self.setPositional(postional)

		QtCore.QObject.connect(self.intbox,QtCore.SIGNAL("editingFinished()"),self._on_intchanged)
		
	def _on_intchanged(self):
		if str(self.intbox.text()).upper() == "NONE":
			self.value = None
			self.setErrorMessage(None)
			return
		try:
			self.value = int(self.intbox.text())
			self.setErrorMessage(None)
			self._confirm_bounds()
		except ValueError:
			self.intbox.setText("") 
			self.setErrorMessage("Invalid type, Int neeeded in %s"%self.getName())
			self.emit(QtCore.SIGNAL("pmmessage(QString)"),"Invalid type, Int neeeded in %s"%self.getName())
			
	def _confirm_bounds(self):
		if self.lrange != None and (self.value < self.lrange):
			self.intbox.setText(str(self.lrange))
			self.emit(QtCore.SIGNAL("pmmessage(QString)"),"Value too low for '%s', clipping to '%d'"%(self.name,self.lrange))
		if self.urange != None and (self.value > self.urange):
			self.intbox.setText(str(self.urange))
			self.emit(QtCore.SIGNAL("pmmessage(QString)"),"Value too high for '%s', clipping to '%d'"%(self.name,self.urange))
			
	def getValue(self):
		return self.value
		
	def setValue(self, value):
		self.intbox.setText(str(value))
		self._on_intchanged()
		
	def setEnabled(self, state):
		self.intbox.setEnabled(state)
		
class PMFloatEntryWidget(PMBaseWidget):
	""" A Widget for geting Float values. Type and range is checked """
	def __init__(self, name, value, lrange=None, urange=None, postional=False, initdefault=None):
		PMBaseWidget.__init__(self, name) 
		gridbox = QtGui.QGridLayout()
		label = QtGui.QLabel(name)
		self.floatbox = QtGui.QLineEdit()
		gridbox.addWidget(label, 0, 0)
		gridbox.addWidget(self.floatbox, 0, 1)
		self.setLayout(gridbox)
		
		self.value = None
		self.lrange = lrange
		self.urange = urange
		self.initdefault = initdefault
		self.setValue(value)
		self.setPositional(postional)
		
		QtCore.QObject.connect(self.floatbox,QtCore.SIGNAL("editingFinished()"),self._on_floatchanged)
		
	def _on_floatchanged(self):
		if str(self.floatbox.text()).upper() == "NONE":
			self.value = None
			self.setErrorMessage(None)
			return
		try:
			self.value = float(self.floatbox.text())
			self.setErrorMessage(None)
			self._confirm_bounds()
		except ValueError:
			self.floatbox.setText("") 
			self.setErrorMessage("Invalid type, float needed in '%s'"%self.getName())
			self.emit(QtCore.SIGNAL("pmmessage(QString)"),"Invalid type, float needed in '%s'"%self.getName())
			
	def _confirm_bounds(self):
		if self.lrange and (self.value < self.lrange):
			self.floatbox.setText(str(self.lrange))
			self.emit(QtCore.SIGNAL("pmmessage(QString)"),"Value too low for '%s', clipping to '%f'"%(self.name,self.lrange))
		if self.urange and (self.value > self.urange):
			self.floatbox.setText(str(self.urange))
			self.emit(QtCore.SIGNAL("pmmessage(QString)"),"Value too high for '%s', clipping to '%f'"%(self.name,self.urange))
			
	def getValue(self):
		return self.value
		
	def setValue(self, value):
		self.floatbox.setText(str(value))
		self._on_floatchanged()
	
	def setEnabled(self, state):
		self.floatbox.setEnabled(state)
		
class PMStringEntryWidget(PMBaseWidget):
	""" A Widget for geting String values. Type is checked """
	def __init__(self, name, string, postional=False, initdefault=None):
		PMBaseWidget.__init__(self, name) 
		gridbox = QtGui.QGridLayout()
		label = QtGui.QLabel(name)
		self.stringbox = QtGui.QLineEdit()
		gridbox.addWidget(label, 0, 0)
		gridbox.addWidget(self.stringbox, 0, 1)
		self.setLayout(gridbox)
		
		self.initdefault = initdefault
		self.setValue(string)
		self.setPositional(postional)
		
		QtCore.QObject.connect(self.stringbox,QtCore.SIGNAL("editingFinished()"),self._on_stringchanged)
	
	def _on_stringchanged(self):
		self.string = str(self.stringbox.text())
		
	def getValue(self):
		# What to do with None tpye values? For strings, just set None to "". This should be equivilent
		return self.string
		
	def setValue(self, string):
		self.stringbox.setText(str(string))
		self._on_stringchanged()
		self.setErrorMessage(None)
	
	def setEnabled(self, state):
		self.stringbox.setEnabled(state)
		
class PMHeaderWidget(PMBaseWidget):
	""" A widget to add a header """
	def __init__(self, name, header):
		PMBaseWidget.__init__(self, name)
		gridbox = QtGui.QGridLayout()
		self.header = QtGui.QLabel()
		font = QtGui.QFont()
		font.setBold(True)
		self.header.setFont(font)
		gridbox.addWidget(self.header)
		self.setLayout(gridbox)

		self.setValue(header)
		
	def getValue(self):
		return str(self.header.text())
		
	def setValue(self, header):
		self.header.setText(header)
		self.setErrorMessage(None)
		
	def getArgument(self):
		""" Obvioulsy the hear does give an argument """
		return None

class PMBoolWidget(PMBaseWidget):
	""" A Widget for getting Bool values. Type is checked """
	def __init__(self, name, boolvalue, initdefault=None):
		PMBaseWidget.__init__(self, name)
		gridbox = QtGui.QGridLayout()
		self.boolbox = QtGui.QCheckBox(name)
		gridbox.addWidget(self.boolbox, 0, 0)
		self.setLayout(gridbox)
		

		self.boolvalue = boolvalue
		self.initdefault = initdefault
		self.setValue(self.boolvalue)
		
		QtCore.QObject.connect(self.boolbox,QtCore.SIGNAL("stateChanged(int)"),self._on_boolchanged)
	
	def _on_boolchanged(self):
		self.boolvalue = self.boolbox.isChecked()
		
	def getValue(self):
		return self.boolvalue
		
	def setValue(self, boolvalue):
		self.boolbox.setChecked(boolvalue)
		self. _on_boolchanged()
		self.setErrorMessage(None)
		
	def getArgument(self):
		return "--%s"%(self.getName())
		
class PMFileNameWidget(PMBaseWidget):
	""" A Widget for geting filenames. Type is checked """
	def __init__(self, name, filename, postional=True, initdefault=None, checkfileexist=True):
		PMBaseWidget.__init__(self, name) 
		gridbox = QtGui.QGridLayout()
		label = QtGui.QLabel(name)
		self.filenamebox = QtGui.QLineEdit()
		self.browsebutton = QtGui.QPushButton("Browse")
		gridbox.addWidget(label, 0, 0)
		gridbox.addWidget(self.filenamebox, 0, 1)
		gridbox.addWidget(self.browsebutton, 0, 2)
		self.setLayout(gridbox)

		self.initdefault = initdefault
		self.checkfileexist= checkfileexist
		self.setValue(filename)
		self.setPositional(postional)
		
		QtCore.QObject.connect(self.filenamebox,QtCore.SIGNAL("editingFinished()"),self._on_filenamechanged)
		QtCore.QObject.connect(self.browsebutton,QtCore.SIGNAL("clicked()"),self._on_clicked)
	
	def _on_filenamechanged(self):
		self.setValue(str(self.filenamebox.text()))
		
	def _on_clicked(self):
		print "Clicked"
		
	def getValue(self):
		return self.filename
		
	def setValue(self, filename):
		# Check to see if the file exists
		filename = str(filename)
		# In some cases a file is optional
		if self.checkfileexist:
			# We need to check if the field is blank
			if filename == "": 
				self._onBadFile(filename)
				return
			# In not blank then check to ensure each file is 'ok'. Not that a list of files is accepted
			if not self._checkfiles(filename): return
		
		# If all is well, then  we are happy
		self.filename = filename
		self.filenamebox.setText(filename)
		self.setErrorMessage(None)
		self.emit(QtCore.SIGNAL("pmfilename(QString)"),self.getValue())
	
	def _checkfiles(self, filename):
		files = filename.split()
		for f in files:
			if not os.access(f, os.F_OK) and not db_check_dict(f):
				self._onBadFile(f)
				# Display the rubbish file to the user
				self.filenamebox.setText(filename)
				return False
		return True
		
	def _onBadFile(self, filename):
		self.filename = None
		self.setErrorMessage("File '%s' from field '%s' does not exist"%(filename,self.getName()))
		self.emit(QtCore.SIGNAL("pmmessage(QString)"),"File '%s' from field '%s' does not exist"%(filename,self.getName()))
		
class PMComboWidget(PMBaseWidget):
	""" A Widget for combo boxes. Type is checked """
	def __init__(self, name, choices, default, postional=False, datatype=str, initdefault=None):
		PMBaseWidget.__init__(self, name) 
		gridbox = QtGui.QGridLayout()
		label = QtGui.QLabel(name)
		self.combobox = QtGui.QComboBox()
		gridbox.addWidget(label, 0, 0)
		gridbox.addWidget(self.combobox, 0, 1)
		self.setLayout(gridbox)

		self.initdefault = initdefault
		self.datatype=datatype	# Must be int, float or str
		
		for choice in choices:
			self.combobox.addItem(str(choice))
		self.setValue(default)
		self.setPositional(postional)
		
	def getValue(self):
		return self.datatype(self.combobox.currentText())
		
	def setValue(self, value):
		idx = self.combobox.findText(str(value))
		if idx > -1:
			self.combobox.setCurrentIndex(idx)
		self.setErrorMessage(None)
			
class PMComboParamsWidget(PMBaseWidget):
	""" A Widget for combo boxes. Type is checked. For the combobox with params the datatype is always str """
	def __init__(self, name, choices, default, postional=False, initdefault=None):
		PMBaseWidget.__init__(self, name) 
		gridbox = QtGui.QGridLayout()
		label = QtGui.QLabel(name)
		self.combobox = QtGui.QComboBox()
		plabel = QtGui.QLabel("params:")
		self.params = QtGui.QLineEdit()
		gridbox.addWidget(label, 0, 0)
		gridbox.addWidget(self.combobox, 0, 1)
		gridbox.addWidget(plabel, 0, 2)
		gridbox.addWidget(self.params, 0, 3)
		self.setLayout(gridbox)

		for choice in choices:
			self.combobox.addItem(str(choice))
		self.combobox.addItem('None')
		
		self.initdefault = initdefault
		self.setValue(default)
		self.setPositional(postional)
	
	def getValue(self):
		""" Return the value. Concatenate if necessary """
		if self.params.text() == "":
			return str(self.combobox.currentText())
		else:
			return str(self.combobox.currentText())+":"+self.params.text()
		
	def setValue(self, value):
		# First parse the value, as it may contain both a options and params
		values = self._parsedefault(value)
		# Next process the parsed value
		idx = self.combobox.findText(str(values[0]))
		if idx > -1:
			self.combobox.setCurrentIndex(idx)
		else:
			self.setErrorMessage("Value '%s' not found in combobox '%s'"%(values[0],self.getName()))
			return
		if len(values) == 2: self.params.setText(values[1])
		self.setErrorMessage(None)
			
	def _parsedefault(self, default):
		default=str(default)
		if default.find(":") != -1:
			return [default[:default.find(":")], default[default.find(":")+1:]]
		else:
			return [default]
		
class PMSymWidget(PMBaseWidget):
	""" A widget for getting/setting symmetry input """
	def __init__(self, name, default, initdefault=None):
		PMBaseWidget.__init__(self, name)
		gridbox = QtGui.QGridLayout()
		label = QtGui.QLabel(name)
		label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
		self.combobox = QtGui.QComboBox()
		self.symnumbox = PMIntEntryWidget("Symmetry Number", 0, lrange=0)
		gridbox.addWidget(label, 0, 0)
		gridbox.addWidget(self.combobox, 0, 1)
		gridbox.addWidget(self.symnumbox, 0, 2, 1, 2)
		self.setLayout(gridbox)
		
		for i in ['icos','oct','tet','c','d','h']: self.combobox.addItem(i)
		
		self.connect(self.symnumbox,QtCore.SIGNAL("pmmessage(QString)"),self._on_message)
		
		self.initdefault = initdefault
		self.setValue(default)
	
	def _on_message(self, message):
		self.emit(QtCore.SIGNAL("pmmessage(QString)"),message)
		
	def getValue(self):
		""" Return the symmetry value """
		return str(self.combobox.currentText())+str(self.symnumbox.getValue())
		
	def setValue(self, value):
		""" Set the value. For example c1 is split into c and 1 and then set """
		defsym = re.findall('[a-zA-Z]+', value)
		defsymnum = re.findall('[0-9]+', value)
		defsym = reduce(lambda x, y: x+y, defsym)
		defsymnum = reduce(lambda x, y: x+y, defsymnum)
		
		idx = self.combobox.findText(defsym)
		if idx > -1:
			self.combobox.setCurrentIndex(idx)
		else:
			self.setErrorMessage("'%s' not a valid symmetry!!!"%value)
			return
		self.symnumbox.setValue(defsymnum)
		self.setErrorMessage(None)
		
	def getErrorMessage(self):
		if self.errormessage: return self.errormessage
		if self.symnumbox.getErrorMessage(): return self.symnumbox.getErrorMessage()

class PMMultiSymWidget(PMBaseWidget):
	""" A widget for getting/setting symmetry input from multiple models and this widget is runtime dynamic """
	def __init__(self, name, initdefault=None):
		PMBaseWidget.__init__(self, name)
		self.gridbox = QtGui.QVBoxLayout()
		self.gridbox.setContentsMargins(0,0,0,0)
		self.stackedwidget = QtGui.QStackedWidget()
		self.multisymwidgetlist = []
		self.gridbox.addWidget(self.stackedwidget)
		self.setLayout(self.gridbox)
		self.lastsymvalue = None
		self.initdefault = initdefault
	
	def setValue(self, value):
		values = value.split(",")
		for i, widget in enumerate(self.multisymwidgetlist):
			if i > len(values) - 1: break	# Can add more defaults than exist!!!
			widget.setValue(values[i])
		self.lastsymvalue = value
		
	def getValue(self):
		multisym = ""
		for widget in self.multisymwidgetlist:
			multisym += ","+widget.getValue()
		multisym = multisym[1:]
		return multisym
		
	def update(self, files):
		if not files: return
		fileslist = str(files).split()
		amount = 0
		self.multisymwidgetlist = []
		# First remove the old widget
		if self.stackedwidget.currentIndex() == -1:
			widget = self.stackedwidget.widget(0)
			self.stackedwidget.removeWidget(widget)
			del(widget)
		# Then add new one
		multisym = QtGui.QWidget()
		vbox = QtGui.QVBoxLayout()
		for i,f in enumerate(fileslist):
			widget = PMSymWidget("Model%d"%i,"c1")
			self.multisymwidgetlist.append(widget)
			vbox.addWidget(widget)
			amount += 60	# A complete HACK
		if self.lastsymvalue: self.setValue(self.lastsymvalue)
		vbox.setContentsMargins(0,0,0,0)
		multisym.setLayout(vbox)
		self.stackedwidget.insertWidget(0, multisym)
		self.stackedwidget.setCurrentIndex(0)
		
		# Then resize the GUI widget, this was just hacked together
		self.setMinimumHeight(amount)
		self.setMaximumHeight(amount)
		
	def getErrorMessage(self):
		if self.errormessage: return self.errormessage
		for widget in self.multisymwidgetlist:
			if widget.getErrorMessage(): return widget.getErrorMessage()
			
class PMAutoMask3DWidget(PMBaseWidget):
	""" A Widget for getting automask 3D input """
	def __init__(self, name, default, initdefault=None):
		PMBaseWidget.__init__(self, name)
		gridbox = QtGui.QGridLayout()
		self.automask3dbool = QtGui.QCheckBox("Auto Mask 3D")
		self.paramsdict = {}
		self.paramsdict["threshold"] = PMFloatEntryWidget("Threshold", 0.8)
		self.paramsdict["nmaxseed"] = PMIntEntryWidget("NMax", 30)
		self.paramsdict["radius"] = PMIntEntryWidget("Radius", 30)
		self.paramsdict["nshells"] = PMIntEntryWidget("Mask Dilations", 5)
		self.paramsdict["nshellsgauss"] = PMIntEntryWidget("Post Gaussian Dialations", 5)
		gridbox.addWidget(self.automask3dbool, 0, 0)
		gridbox.addWidget(self.paramsdict["threshold"], 1, 0)
		gridbox.addWidget(self.paramsdict["nmaxseed"], 1, 1)
		gridbox.addWidget(self.paramsdict["radius"], 1, 2)
		gridbox.addWidget(self.paramsdict["nshells"], 2, 0)
		gridbox.addWidget(self.paramsdict["nshellsgauss"], 2, 1, 1, 2)
		self.setLayout(gridbox)
		self.setValue(default)
		self.initdefault = initdefault
		
		QtCore.QObject.connect(self.automask3dbool,QtCore.SIGNAL("stateChanged(int)"),self._on_boolchanged)
		self.connect(self.paramsdict["threshold"],QtCore.SIGNAL("pmmessage(QString)"),self._on_message)
		self.connect(self.paramsdict["nmaxseed"],QtCore.SIGNAL("pmmessage(QString)"),self._on_message)
		self.connect(self.paramsdict["radius"],QtCore.SIGNAL("pmmessage(QString)"),self._on_message)
		self.connect(self.paramsdict["nshells"],QtCore.SIGNAL("pmmessage(QString)"),self._on_message)
		self.connect(self.paramsdict["nshellsgauss"],QtCore.SIGNAL("pmmessage(QString)"),self._on_message)
		
	def _on_boolchanged(self):
		for widget in self.paramsdict.values():
			widget.setEnabled(self.automask3dbool.isChecked())
	
	def _on_message(self, message):
		self.emit(QtCore.SIGNAL("pmmessage(QString)"),message)
		
	def setValue(self, value):
		# if value is "" of None, set bool to false
		if not value:
			self.automask3dbool.setChecked(False)
			self._on_boolchanged()
			return
		# Otherwise parse input and set
		self.automask3dbool.setChecked(True)
		params = value.split(':')
		for param in params:
			key, val = param.split('=')
			self.paramsdict[key].setValue(val)
			
	def getValue(self):
		if not self.automask3dbool.isChecked(): return None
		value = ""
		# concatenate things
		for key in self.paramsdict.keys():
			value = value+ ":"+key+"="+str(self.paramsdict[key].getValue())
		value = value[1:]
		return value
		
	def getErrorMessage(self):
		if self.errormessage: return self.errormessage
		if self.paramsdict["threshold"].getErrorMessage(): return self.paramsdict["threshold"].getErrorMessage()
		if self.paramsdict["nmaxseed"].getErrorMessage(): return self.paramsdict["nmaxseed"].getErrorMessage()
		if self.paramsdict["radius"].getErrorMessage(): return self.paramsdict["radius"].getErrorMessage()
		if self.paramsdict["nshells"].getErrorMessage(): return self.paramsdict["nshells"].getErrorMessage()
		if self.paramsdict["nshellsgauss"].getErrorMessage(): return self.paramsdict["nshellsgauss"].getErrorMessage()
		
		
		
'''
class PMTableWidget(QtGui.QWidget):
	""" A Widget for generating a table """
	def __init__(self, name, columns, cwd):
		QtGui.QWidget.__init__(self) 
		self.cwd = cwd
		
		gridbox = QtGui.QGridLayout()
		boldfont = QtGui.QFont()
		boldfont.setBold(True)
		label = QtGui.QLabel(name)
		label.setFont(boldfont)
		gridbox.addWidget(label, 0, 0)
		
		# Build the table
		self.qttable = QtGui.QTableWidget(2,len(columns))
		colheaderlist = QtCore.QStringList()
		for col in columns:
			colheaderlist.append(str(col))
			
		self.qttable.setHorizontalHeaderLabels(colheaderlist)
		
		gridbox.addWidget(self.qttable, 1, 0)
		self.browsebutton = QtGui.QPushButton("Browse To Add")
		gridbox.addWidget(self.browsebutton, 2, 0)
		self.setLayout(gridbox)
		
		self.connect(self.browsebutton,QtCore.SIGNAL("clicked(bool)"),self._on_browse)
		
	def _on_browse(self):
		dd = EMSelectorDialog()
		dataitem = dd.exec_()
'''