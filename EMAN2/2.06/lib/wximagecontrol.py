#!/usr/local/eman/2.06/Python/bin/python
# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.4 on Fri Dec  9 01:54:49 2005

import wx
from math import *
from emimagecanvas import *

class ImageControl(wx.Dialog):
	def __init__(self, *args, **kwds):
		# begin wxGlade: ImageControl.__init__
		kwds["style"] = wx.DEFAULT_DIALOG_STYLE|wx.STAY_ON_TOP
		wx.Dialog.__init__(self, *args, **kwds)

		size = wx.Size(140,20)

		self.checkbox_1 = wx.CheckBox(self, -1, "FFT")
		self.label_4 = wx.StaticText(self, -1, "B:")
		self.sli_brt = wx.Slider(self, -1, 5000, 0, 10000, size=size)
		self.label_5 = wx.StaticText(self, -1, "C:")
		self.sli_cnt = wx.Slider(self, -1, 0, 0, 10000, size=size)
		self.label_6 = wx.StaticText(self, -1, "Min:")
		self.sli_min = wx.Slider(self, -1, 0, 0, 10000, size=size)
		self.label_7 = wx.StaticText(self, -1, "Max:")
		self.sli_max = wx.Slider(self, -1, 0, 0, 10000, size=size)

		self.label_8 = wx.StaticText(self, -1, "Scale:")
		self.sli_scale = wx.Slider(self, -1, 0, -1000, 1000, size=size)

		self.EMImageCanvas = EMImageCanvas(self)

		self.__set_properties()
		self.__do_layout()

		self.Bind(wx.EVT_CHECKBOX, self.check_fft, self.checkbox_1)
		self.Bind(wx.EVT_COMMAND_SCROLL, self.scr_b, self.sli_brt)
		self.Bind(wx.EVT_COMMAND_SCROLL, self.scr_c, self.sli_cnt)
		self.Bind(wx.EVT_COMMAND_SCROLL, self.scr_min, self.sli_min)
		self.Bind(wx.EVT_COMMAND_SCROLL, self.scr_max, self.sli_max)

		# end wxGlade

		self.Bind(wx.EVT_COMMAND_SCROLL, self.scr_scale, self.sli_scale)
		self.disb=0.0
		self.disc=45.0

	def __set_properties(self):
		# begin wxGlade: ImageControl.__set_properties
		self.SetTitle("Control Panel")
		self.SetSize((500, 500))
		# end wxGlade

	def __do_layout(self):
		# begin wxGlade: ImageControl.__do_layout

		grid_sizer_1 = self.grid_sizer_1 = wx.GridBagSizer(hgap=0, vgap=0)

		self.sizer = wx.BoxSizer(wx.HORIZONTAL)

		grid_sizer_1.Add(self.label_4,(1,0),(1,1),wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		grid_sizer_1.Add(self.sli_brt,(1,1),(1,3),wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)

		grid_sizer_1.Add(self.label_5,(2,0),(1,1),wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		grid_sizer_1.Add(self.sli_cnt,(2,1),(1,3),wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)

		grid_sizer_1.Add(self.label_6,(3,0),(1,1),wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		grid_sizer_1.Add(self.sli_min,(3,1),(1,3),wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)

		grid_sizer_1.Add(self.label_7,(4,0),(1,1),wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		grid_sizer_1.Add(self.sli_max,(4,1),(1,3),wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)

		grid_sizer_1.Add(self.label_8,(5,0),(1,1),wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)
		grid_sizer_1.Add(self.sli_scale,(5,1),(1,3),wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL)

		#grid_sizer_1.AddGrowableCol(1)
		#sizer.Add(grid_sizer_1, 1, wx.EXPAND, 0)
		#sizer_6.AddGrowableCol(0)
		#sizer_1.Add(sizer_6, 1, wx.EXPAND, 0)
	
		#sizer_1.Add(self.EMImageCanvas, 1, 0,wx.SIMPLE_BORDER)


		self.sizer.Add(self.grid_sizer_1,0,wx.ALIGN_LEFT|wx.ALL,border=5)
		self.sizer.Add(self.EMImageCanvas,1,wx.ALIGN_LEFT|wx.RAISED_BORDER|wx.ALIGN_CENTER_VERTICAL,border=5)

		self.SetSizer(self.sizer)
		self.SetAutoLayout(1)
		self.sizer.Fit(self)

		#self.Show(True)

		#self.SetAutoLayout(True)
		#self.SetSizer(sizer_1)
		#self.Layout()
		# end wxGlade

	def set_target(self,t):
		self.target=t
		self.EMImageCanvas.set_target(t)
		self.dismin=self.target.data.get_attr("minimum")
		self.dismax=self.target.data.get_attr("maximum")
		self.default_scale = self.target.scale

		self.update_minmax()

	def check_fft(self, event): # wxGlade: ImageControl.<event_handler>
		if self.target:
			self.target.setfft(event.IsChecked())
		event.Skip()

	def scr_scale(self, event): # wxGlade: ImageControl.<event_handler>
		if self.target:
			if event.GetPosition() <= 100 and event.GetPosition() > -100:
				newscale = 1.0
			elif event.GetPosition() <= -100:
				newscale = -(100.0/event.GetPosition())
			else:
				newscale = event.GetPosition() / 100.0

			self.target.scale = newscale
			self.EMImageCanvas.ReDraw()
			self.target.changed()
		event.Skip()

	def scr_b(self, event): # wxGlade: ImageControl.<event_handler>
		if self.target:
			self.disb=1.0-event.GetPosition()/5000.0		# brightness is from -1 to 1
			self.update_bc()
		event.Skip()

	def scr_c(self, event): # wxGlade: ImageControl.<event_handler>
		if self.target:
			self.disc=event.GetPosition()/10000.0*60.0+30.0	# contrast is an angle in degrees, adjust from 30 - 90
			self.update_bc()
		event.Skip()

	def scr_min(self, event): # wxGlade: ImageControl.<event_handler>
		if self.target:
			m0=self.target.data.get_attr("minimum")
			m1=self.target.data.get_attr("maximum")
			self.dismin=event.GetPosition()/10000.0*(m1-m0)+m0
			self.update_minmax()
			if self.dismax<=self.dismin : self.dismax=self.dismin+.00001*(m1-m0)
		event.Skip()

	def scr_max(self, event): # wxGlade: ImageControl.<event_handler>
		if self.target:
			m0=self.target.data.get_attr("minimum")
			m1=self.target.data.get_attr("maximum")
			self.dismax=event.GetPosition()/10000.0*(m1-m0)+m0
			if self.dismax<=self.dismin : self.dismin=self.dismax-.00001*(m1-m0)
			self.update_minmax()
		event.Skip()


	def update_bc(self):
		if self.disc==90.0 : self.disc=89.9999
		m0=self.target.data.get_attr("minimum")
		m1=self.target.data.get_attr("maximum")
		range=(m1-m0)/tan(self.disc*pi/180.0)
		mid=(m1+m0)/2.0+self.disb*(m1-m0)
		self.dismin=mid-range/2.0
		self.dismax=mid+range/2.0
		self.sli_min.SetValue((self.dismin-m0)/(m1-m0)*10000.0)
		self.sli_max.SetValue((self.dismax-m0)/(m1-m0)*10000.0)
		self.target.setminmax(self.dismin,self.dismax)
	
	def update_minmax(self):
		if self.disc==90.0 : self.disc=89.9999
		m0=self.target.data.get_attr("minimum")
		m1=self.target.data.get_attr("maximum")
		self.disb=((self.dismax+self.dismin)-(m1+m0))/(m1-m0)
		self.disc=atan((m1-m0)/(self.dismax-self.dismin))*180.0/pi
		self.disc=max(30.0,min(90.0,self.disc))
		self.sli_brt.SetValue(10000.0-(self.disb+1.0)*5000.0)
		self.sli_cnt.SetValue(10000.0*(self.disc-30.0)/60.0)

		if self.default_scale > 1:
			tmp = self.default_scale * 100
		else:
			tmp = - (1/self.default_scale) * 100
		self.sli_scale.SetMin(tmp)
		self.sli_scale.SetValue(tmp)

		self.target.setminmax(self.dismin,self.dismax)

	def update_canvas_per(self):
		if self.target:
			self.EMImageCanvas.x_per = self.target.x_per
			self.EMImageCanvas.y_per = self.target.y_per

			#print "update?: " + str(self.EMImageCanvas.x_per)

			self.EMImageCanvas.ReDraw()


# end of class ImageControl
