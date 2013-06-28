#!/usr/bin/python

# treectrl.py

import os
import wx,h5py

class HdfTree(wx.Frame):

  def Open(self,fnHDF):
    self.fid = h5py.h5f.open(fnHDF)

  def Close(self):
    self.fid.close()
    del self.fid

  def __init__(self, parent, id, title):
    wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(650, 350))

    wxSplt = wx.SplitterWindow(self, -1)
    wxTree = wx.TreeCtrl(wxSplt, 1, wx.DefaultPosition, (-1,-1),  wx.TR_HAS_BUTTONS)
    wxTree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, id=1)

    il = wx.ImageList(16, 16)
    home    = il.Add(wx.Image("images/home.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap())
    folder  = il.Add(wx.Image("images/folder.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap())
    dataset = il.Add(wx.Image("images/dataset.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap())
    wxTree.AssignImageList(il)
    
    wxTxt = wx.StaticText(wxSplt, -1, '',(10,10) )#, style=wx.ALIGN_CENTRE)

    wxSplt.SplitVertically(wxTree, wxTxt)
    self.Centre()

    self.wxTree=wxTree
    self.display=wxTxt
  def __del__(self):
    self.Close()   

  def OnSelChanged(self, event):
      wxTree=self.wxTree
      wxNode =  event.GetItem()
      txt=wxTree.GetItemText(wxNode)
      data=wxTree.GetPyData(wxNode)
      #o=wxTree.GetItemData(wxNode)
      #print o.Data,wxTree.GetPyData(wxNode)
      #if type(gid)==h5py.h5g.GroupID:
      if data:
        t=type(data)
        if t==h5py.h5g.GroupID:
          pass
        elif t==h5py.h5d.DatasetID:
          l=[txt]
          l.append('shape: '+str(data.shape))
          tt=data.get_type()
          if type(tt)==h5py.h5t.TypeCompoundID:
            l.append('type: Compound')
          else:
            l.append('type: '+str(tt.dtype))
          
          pl=data.get_create_plist()
          txFcn=(
           ('chunk',h5py.h5p.PropDCID.get_chunk),
           ('fill time',h5py.h5p.PropDCID.get_fill_time),
           ('alloc_time',  h5py.h5p.PropDCID.get_alloc_time),
           #('class',       h5py.h5p.PropDCID.get_class),
           ('fill_time',   h5py.h5p.PropDCID.get_fill_time),
           #('fill_value',  h5py.h5p.PropDCID.get_fill_value),
           #('filter',      h5py.h5p.PropDCID.get_filter),
           #('filter_by_id',h5py.h5p.PropDCID.get_filter_by_id),
           ('layout',      h5py.h5p.PropDCID.get_layout),
           ('nfilters',    h5py.h5p.PropDCID.get_nfilters),
           ('obj_track_times', h5py.h5p.PropDCID.get_obj_track_times),
           )
          for tx,func in txFcn:
            try: v=func(pl)
            except ValueError as e: pass
            else: l.append(tx+': '+str(v))
                    
          txt='\n'.join(l)
        print t,data.id
      self.display.SetLabel(txt)

  def _ShowHirarchy(self,wxParent,gidParent,lvl):
    for gidStr in h5py.h5g.GroupIter(gidParent):
      gid = h5py.h5o.open(gidParent,gidStr)
      t=type(gid)
      if t==h5py.h5g.GroupID:
        image=1
      elif t==h5py.h5d.DatasetID:     
        image=2
      else:
        image=-1
      wxNode = self.wxTree.AppendItem(wxParent, gidStr,image=image,data=wx.TreeItemData(gid))
      if t==h5py.h5g.GroupID:
        self._ShowHirarchy(wxNode,gid,lvl+1)

  def ShowHirarchy(self):
    fn=os.path.basename(self.fid.name)
    wxNode = self.wxTree.AddRoot(fn,image=0)
    HdfTree._ShowHirarchy(self,wxNode,self.fid,0)
    self.wxTree.ExpandAll()

if __name__ == '__main__':
  class MyApp(wx.App):
      def OnInit(self):
          frame = HdfTree(None, -1, 'hdfTree')
          frame.Open('/home/zamofing_t/Documents/prj/libDetXR/python/libDetXR/e14472_00033.hdf5')
          frame.ShowHirarchy()
          frame.Show(True)
          self.SetTopWindow(frame)
          return True
  
  app = MyApp(0)
  app.MainLoop()
