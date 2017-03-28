__version__="""M.Maris, 1.3 -  - 27 Nov 2012 - 26 Dec 2016 -"""
__DESCRIPTION__="""
A grid 2d is a 2x2 array representing a grid
At the moment no DS9 support is directly provided

Private: _PIXEL_LIST a list of pixels and _CENTER for the center of a map

"""

class fast_histogram :
   def __init__(self,x,levels=None,vmin=None,vmax=None,finite=False,nan=False) :
      """returns the unique values of an array x and their counts"""
      import numpy as np
      a=np.sort(x.reshape(x.size))
      self.vmin = a[0] if vmin == None else vmin
      self.vmax = a[-1] if vmax == None else vmax
      if levels == None :
	 self.u=np.unique(a)
	 self.step=None
      elif type(levels) == type(0) :
	 self.step = float(vmax-vmin)/float(levels)
	 self.u=np.arange(self.vmin,self.vmax+self.step,self.step)
      self.idx=np.zeros(len(self.u))
      self.nsamples=len(a)
      i=-1
      for v in self.u :
	 i+=1
	 self.idx[i]=a.searchsorted(v)
      self.levels=(self.u[1:]+self.u[:-1])*0.5
      self.dn=self.idx[1:]-self.idx[:-1]
      self.dn[-1]=self.nsamples-self.idx[-1]+1
      self.df=self.dn/float(self.nsamples)
      self.N=self.dn.cumsum()
      self.F=self.N/float(self.nsamples)
   def midlevels(self) :
      return (self.u[1:]+self.u[:-1])*0.5
   def width(self) :
      return (self.u[1:]-self.u[:-1])
   def polygonal(self) :
      pass

def Error(msg) : return Exception(msg)

class _PIXEL_LIST :
   def __init__(self,irows,icols) :
      """A pixel list for given indexes of rows and columns"""
      import numpy as np
      #if len(irows) != len(icols) :
         #raise "Unequal irows, icols"
         #return None
      self.irow = np.array(irows)
      self.icol = np.array(icols)
   def __len__(self) :
      return len(self.irow)
   def __getitem__(self,idx) :
      return (self.irow[idx],self.icol[idx])
   def dump(self,output) :
      import pickle
      pickle.dump(self.__dict__,output)
   def load(self,Input) :
      import pickle
      self.__dict__=pickle.load(Input)

class _CENTER :
   def __init__(self,center_long_deg,center_colat_deg,Input=None) :
      """Center of a map"""
      import _ANGLE
      import pickle
      if Input == None :
         self.long = _ANGLE(deg=center_long_deg)
         self.colat = _ANGLE(deg=center_colat_deg)
      else :
         self.__dict__=pickle.load(Input)
   def dump(self,output) :
      import pickle
      pickle.dump(output,self.__dict__)
   def load(self,Input) :
      import pickle
      self.__dict__=pickle.load(Input)
   def __str__(self,return_deg=True) :
      if return_deg :
         return "%e, %e" % (self.long.deg, self.colat.deg)
      else :
         return "%e, %e" % (self.long.rad, self.colat.rad)

class _ANGLE :
   def __init__(self,deg=None,rad=None,Input=None) :
      """An angle"""
      import pickle
      if Input == None :
         if (deg == None) and (rad==None) :
            self.deg = None
            self.rad = None
         else :
            if (deg != None) :
               self.deg = deg
               self.rad = deg/180.*np.pi
            else :
               self.rad = rad
               self.deg = rad*180./np.pi
      else :
         self.__dict__=pickle.load(Input)
   def __str__(self) :
      return "(%e,%e)" % (self.deg,self.rad)
   def __len__(self) :
      try :
         return len(self.deg)
      except :
         return 1
   def __str__(self) :
      if self.__len__() == 1 :
         return "%e, %e" % (self.deg, self.rad)
      else :
         ll = ["(%e, %e)" % (self.deg[0], self.rad[0])]
         ll.append("(%e, %e)" % (self.deg[-1], self.deg[-1]))
         return "["+ll[0]+"..."+ll[1]+"]"
   def dump(self,output) :
      import pickle
      pickle.dump(output,self.__dict__)
   def load(self,Input) :
      import pickle
      self.__dict__=pickle.load(Input)

import numpy as np
class _MAP :
   """A map"""
   def __init__(self,Nx, Ny,Namex = '', Namey='',dtype=np.float,value=0,Input=None) :
      import numpy as np
      import pickle
      if Input == None :
         self.m = np.zeros([Nx, Ny],dtype=dtype)+value
         self.Namex = Namex
         self.Namey = Namey
      else :
         self.__dict__=pickle.load(Input)
   def __getitem__(self,x,y) :
      return self.m[x,y]
   def dump(self,output) :
      import pickle
      pickle.dump(output,self.__dict__)
   def load(self,Input) :
      import pickle
      self.__dict__=pickle.load(Input)

class GridAxis :
   def __init__(self,*karg,**kopt) :
      """An axe of a map 
         axis()
         axis(GridAxis)
         axis(Struct)
         axis(string name)
         axis(pyfits hdu)
         axis(string name,string unit)
         axis(string name,string unit,array values)
         axis(string name,string unit,float min, float max, int n)
         axis(string name,string unit,float min, float max, float delta)
         axis(string name,string unit,list_of_strings)
         
         Keywords : period 
         
         See grid2d.__VERSION__ for versioning and grid2d.__DESCRIPTION__ for description
      """ 
      from numpy import nan,zeros,array,round,arange
      import copy
      import pyfits
      self.__dict__=self.new()
      if len(karg) == 0 : 
         return
      if len(karg) == 1 : 
         if type(karg[0]) == type({}) :
            for k in self.__dict__.keys() :
               try :
                  self.__dict__[k] = copy.deepcopy(karg[0][k])
               except :
                  print "Error: input structure has not key %s, does it represent an axis?"%k
            return
         elif type(karg[0]) == type('') :
            self.name=karg[0]
            return
         elif type(karg[0]) == type(pyfits.ImageHDU()) :
            self.v=karg[0].data*1
            self.n=len(self.v)
            self.min=self.v.min()
            self.max=self.v.max()
            self.delta=self.v[1]-self.v[0]
            self.closed=karg[0].header['closed']
            self.textual=karg[0].header['textual']
            self.dim=karg[0].header['dim']
            self.dimid=karg[0].header['dimid'].strip()
            self.unit=karg[0].header['unit'].strip()
            self.name=karg[0].header['name'].strip()
            try :
               self.sampling=karg[0].header['sampling'].strip()
            except :
               self.sampling='unknown'
            if kopt.has_key('period') :
               if kopt['period'] == True and type(kopt['period'])==type(True):
                  self.set_periodic()
               elif kopt['period'] != None and kopt['period'] != False and kopt['period'] != nan and kopt['period'] != 0 :
                  self.set_periodic(period=kopt['period'])
            return
         else :
            self=copy.deepcopy(karg[0])
            return
      self.name=karg[0]
      self.unit=karg[1]
      if len(karg) < 3 :
         return
      if type(karg[2]) == type(array([])) :
         if type(karg[2][0]) != type('') :
            self.v = 1.*karg[2]
            self.min = self.v.min()
            self.max = self.v.max()
            self.n = len(self.v)
            self.delta = self.v[1]-self.v[0]
         else :
            self.textual=True
            self.text = copy.deepcopy(array(karg[2]))
            self.v = arange(0,len(self.text))
            self.n = len(self.v)
            self.min = float(self.v.min())
            self.max = float(self.v.max())
            self.delta = 1.
      else :
         if len(karg) < 4 :
            print "error: not enough arguments"
            return
         self.min=karg[2]
         self.max=karg[3]
         if type(karg[4]) == type(1) :
            self.n=karg[4]
            self.delta=(karg[3]-karg[2])/float(karg[4])
            self.v=np.arange(self.min,self.max+self.delta,self.delta)
         else :
            self.delta=karg[4]
            self.n=int(round((karg[3]-karg[2])/float(karg[4])))
            self.v=np.arange(self.min,self.max+self.delta,self.delta)
      if kopt.has_key('period') :
         if kopt['period'] == True and type(kopt['period'])==type(True):
            self.set_periodic()
         elif kopt['period'] != None and kopt['period'] != False and kopt['period'] != nan and kopt['period'] != 0 :
            self.set_periodic(period=kopt['period'])
   def version(self) :
      "returns the class version"
      return "Formal Revision: 1.0 - 2012 Apr 1"
   def new(self) :
      from numpy import nan
      C = {}
      C['name']=''
      C['delta']=nan
      C['min']=nan
      C['max']=nan
      C['n']=0
      C['unit']=''
      C['v']=None
      C['closed']=False
      C['textual']=False
      C['text']=None
      C['dim']=None
      C['dimid']=''
      C['period_ticks']=-1
      C['sampling']='uniform'
      return C
   def toImageHDU(self,hduname,comments=[],dim=None,dimid=None,addchecksum=True) :
      "convert an axis into an image hdu"
      import pyfits
      import time
      if dim!=None :
         _dim=dim
      elif self.dim!=None :
         _dim=self.dim
      else :
         _dim=-1
      if dimid!=None and dimid!='' :
         _dimid=dimid
      elif self.dim!=None and self.dimid!='':
         _dimid=self.dimid
      else :
         _dimid=''
      hdu=pyfits.ImageHDU(self.v)
      hdu.name=hduname
      hdu.header.add_comment('Values of %s axis'%self.name)
      hdu.header.add_comment('HDU Created: %s'%time.asctime())
      hdu.header.add_comment(self.version())
      hdu.header.add_comment('NOTES:')
      hdu.header.add_comment('+If TEXTUAL is true in place of values indexes are added')
      hdu.header.add_comment('+DIM is the dimension of the array to which the axis refer')
      hdu.header.add_comment(' The slowest dimension to increase is the most lef')
      hdu.header.add_comment(' The slowest dimension to increase is the most lef')
      hdu.header.add_comment(' Example: in an array A[i,j,k] DIM=1 is i, DIM=2, is j, DIM=3 is k')
      hdu.header.add_comment(' i is slower than j that is slower than k')
      hdu.header.add_comment(' Usually in a 2d array A[i,j], i is referred as row, j as column')
      try :
         if len(comments) > 0 :
            if type(comments) == [] :
               for line in comments :
                  if len(line.strip()) > 0 :
                     hdu.header.add_comment(line.strip())
            else :
               for line in comments.split('\n') :
                  if len(line.strip()) > 0 :
                     hdu.header.add_comment(line.strip())
      except :
         pass
      hdu.header.update('dim',_dim,'dimension of array')
      hdu.header.update('dimid',_dimid,'row, col or other')
      hdu.header.update('name',self.name,'name of axis')
      hdu.header.update('unit',self.unit,'unit of axis')
      hdu.header.update('min',self.min,'minimum axis')
      hdu.header.update('max',self.max,'maximum axis')
      hdu.header.update('delta',self.delta,'step of axis (if uniform)')
      hdu.header.update('period',self.period,'period in ticks (<=0 no period)')
      hdu.header.update('n',self.n,'number of elements of axis')
      hdu.header.update('closed',self.closed,'true if closed')
      hdu.header.update('textual',self.textual,'true if textual')
      hdu.header.update('sampling',self.sampling,'kind of sampling, default uniform')
      if addchecksum :
         hdu.add_checksum()
      return hdu
   def right_close(self) :
      """ copyes the first row assuming it has the same value of the first, used to give maps with cyclicalBoundaries """
      from numpy import concatenate,ones,arange
      import copy
      if not self.textual :
         self.v =  concatenate([self.v,ones(1)*self.v[-1]+self.delta])
         self.n =  len(self.v)
         self.min =  self.v.min()
         self.max =  self.v.max()
         self.closed=True
      else :
         l=[]
         for k in self.text :
            l.append(k)
         l.append(self.text[0])
         self.text =  copy.deepcopy(l)
         self.v = arange(0,len(self.text))
         self.n = len(self.v)
         self.min = float(self.v.min())
         self.max = float(self.v.max())
         self.delta = 1.
         self.closed=True
   def set_periodic(self,period=None) :
      "makes periodic"
      import numpy as np
      if period!=None:
         self.period_ticks = np.floor(float(period)/self.delta)
      else :
         self.period_ticks = float(self.n)
   def is_periodic(self) :
      return self.period_ticks > 0
   def __len__(self) :
      return self.n
   def __call__(self,*arg) :
      if len(arg) == 0 :
         return self.__dict__
      elif len(arg) == 1 :
         return self.__dict__[arg[0]]
      else :
         return self.__dict__[arg[0]][arg[1]]
   def __getitem__(self,*arg) :
      if len(arg) == 0 :
         return self.__dict__
      elif len(arg) == 1 :
         return self.__dict__[arg[0]]
      elif len(arg) == 2 :
         return self.__dict__[arg[0]][arg[1]]
      elif len(arg) == 3 :
         return self.__dict__[arg[0]][arg[1]][arg[2]]
      elif len(arg) == 4 :
         return self.__dict__[arg[0]][arg[1]][arg[2]][arg[3]]
      else :
         l=self.__dict__[arg[0]]
         for ik in range(1,len(arg)) : 
            try :
               l=l[arg[ik]]
            except :
               print "Some error extracting element %d of "%ik,arg
               return None
   def __setitem__(self,*arg) :
      import copy
      if len(arg) == 1 :
         self.__dict__ = copy.deepcopy(arg[0])
      elif len(arg) == 2 :
         self.__dict__[arg[1]] = copy.deepcopy(arg[0])
      else :
         self.__dict__[arg[1]][arg[2]] = copy.deepcopy(arg[0])
   def keys() :
      return self.keys()

class MapGrid() :
   def __init__(self,*karg,**kopt) : #reference_x=None,reference_y=None,mapname=None)
      """
      A map gridded
      MpG = MapGrid() an empty map
      
      #deprecated methods
      MpG = MapGrid(mapname) a map loaded from a pickle file with name mapname
      MpG = MapGrid(nrows,ncols) a map with nrows, ncols
      #def __init__(self,mapname,xname,xmin,xmax,nx,xunit,yname,ymin,ymax,ny,yunit,reference_x=None,reference_y=None)
      
      #preferred methods
      MpG = MapGrid(pickle=mapname) a map loaded from a pickle file with name mapname
      MpG = MapGrid(Rows=nrows,Cols=ncols) a map with nrows, ncols
      MpG = MapGrid(Rows=numpy_array1d,Cols=numpy_array1d) a map with rows and cols listed as numpy 1d arrays
      MpG = MapGrid(Rows=GridAxisRows,Cols=GridAxisCols) a map with rows and cols specified by GridAxis objects
      MpG = MapGrid(model=numpy_array2d) a map with format specified by a 2D numpy array taken as model

      keyword mapname sets a name to a map
      """
      import numpy as np
      import pickle
      import copy
      _Verbose = kopt.has_key('Verbose')==True if kopt.has_key('Verbose') else False
      self.clean(__verbose__=_Verbose)
      #print len(karg)
      if len(karg) == 0 :
         kkopt=kopt.copy()
         if len(kopt) == 0 : 
            return
         if kopt.has_key('mapname') :
            self.mapname=kopt['mapname']
         if kopt.has_key('pickle') :
            self.getFromPickle(kopt['pickle'])
            return
         if kopt.has_key('fits') :
            self.getFromFits(kopt['fits'])
            return
         if kopt.has_key('model') :
            self.createBaseGrid_from_model(kopt['model'],**kopt)
            return
         if kopt.has_key('Rows') and kopt.has_key('Cols'):
            if type(kopt['Rows'])==type(0) and type(kopt['Cols'])==type(0) :
               self.createBaseGrid_from_nrowsncols(*karg,**kopt)
               return
            elif type(kopt['Rows'])==type(np.array([])) and type(kopt['Cols'])==type(np.array([])) :
               kkopt['Cols']=GridAxis('x','',kopt['Cols'])
               kkopt['Rows']=GridAxis('y','',kopt['Rows'])
               self.createBaseGrid_from_gridaxis(*karg,**kkopt)
               return
            elif kopt['Rows'].__class__==GridAxis().__class__ and kopt['Cols'].__class__==GridAxis().__class__ :
               self.createBaseGrid_from_gridaxis(*karg,**kopt)
               return
            elif type(kopt['Rows'])==type({}) and type(kopt['Cols'])==type({}) :
               kkopt=kopt.copy()
               kkopt['Rows'] = GridAxis(kopt['Rows'])
               kkopt['Cols'] = GridAxis(kopt['Cols'])
               self.createBaseGrid_from_gridaxis(*karg,**kkopt)
               return
            else :
               if _Verbose : print "Unknown signature, empy object created"
               return
         return
      if len(karg)==1 :
         kkopt = kopt.copy() 
         if type(karg[0]) == type('') :
            kkopt['pickle']=karg[0]
            self.getFromPickle(self,*karg,**kkopt)
            return
         elif type(karg[0]) == type(np.array()):
            kkopt['model']=karg[0]
            self.createBaseGrid_from_model(karg[0],**kkopt)
            return
         else :
            if _Verbose : print "Unknown signature, empy object created"
            return
      if len(karg)==2 :
         kkopt = kopt.copy() 
         if type(karg[0]) == type(0) and type(karg[1]) == type(0) :
            kkopt['Rows']=karg[1]
            kkopt['Cols']=karg[0]
            self.createBaseGrid_from_nrowsncols(*karg,**kkopt)
         elif karg[0].__class__==GridAxis().__class__ and karg[1].__class__==GridAxis().__class__ :
            kkopt['Rows']=karg[1]
            kkopt['Cols']=karg[0]
            self.createBaseGrid_from_gridaxis(*karg,**kkopt)
         elif type(karg[0]) == type(0) and type(karg[1]) == type(0) :
            kkopt['Rows']=karg[1]
            kkopt['Cols']=karg[0]
         return

   def isVerbose(self) : return self.__verbose__

   def newaxis(self) :
      return GridAxis().__dict__

   def clean(self,shape=None,__verbose__=False) :
      from collections import OrderedDict
      from numpy import nan,zeros
      self.info=OrderedDict()
      self.mapname = ''
      # sets the phi along the x axis of the grid i.e. the columns
      self.C = GridAxis().__dict__
      # sets the theta along the y axis of the grid  i.e. the rows
      self.R = GridAxis().__dict__
      # sets the remaining 
      self.naxis=2 if shape == None else len(list(shape))
      self.shape=[0,0] if shape == None else list(shape)
      self.center=zeros(2) if shape == None else np.array([int(shape[0]/2),int(shape[1]/2)])
      self.centerRow=-1 if shape == None else int(shape[0]/2)
      self.centerCol=-1 if shape == None else int(shape[1]/2)
      self.pickle_name = ''
      self.fits_name = ''
      self.M=OrderedDict()
      self.unit=OrderedDict()
      self.f=OrderedDict()
      self.ncols=self.shape[1]
      self.nrows=self.shape[0]
      self.map_info=OrderedDict()
      self.__verbose__=__verbose__

   def createBaseGrid_empty(self,*karg,**kopt) :
      """creates a base grid empty after a clean(shape=shape)"""
      #
      if kopt.has_key('mapname') : self.mapname=kopt['mapname']
      #
      self.C = GridAxis().__dict__
      self.R = GridAxis().__dict__
      xname = 'x' if not kopt.has_key('xname') else kopt['xname'] 
      yname = 'y' if not kopt.has_key('yname') else kopt['yname'] 
      xunit = '' if not kopt.has_key('xunit') else kopt['xunit'] 
      yunit = '' if not kopt.has_key('yunit') else kopt['yunit'] 
      self.set_col_scale(xname,xunit,np.arange(self.ncols))
      self.set_row_scale(yname,yunit,np.arange(self.nrows))
      #
      self.map_info['_col_index']={'comment':'index of cols','private':True}
      self.map_info['_col_values']={'comment':'values of cols','private':True}
      self.M['_col_index']=np.zeros([self.R['n'],self.C['n']],dtype='int')
      self.M['_col_values']=np.zeros([self.R['n'],self.C['n']],dtype='float')
      for ic in range(self.C['n']) : 
         self.M['_col_index'][:,ic] = ic
         self.M['_col_values'][:,ic] = self.C['v'][ic]
      #        
      self.map_info['_row_index']={'comment':'index of rows','private':True}
      self.map_info['_row_values']={'comment':'values of rows','private':True}
      self.M['_row_index']=np.zeros([self.R['n'],self.C['n']],dtype='int')
      self.M['_row_values']=np.zeros([self.R['n'],self.C['n']],dtype='float')
      for ir in range(self.R['n']) : 
         self.M['_row_index'][ir] = ir
         self.M['_row_values'][ir] = self.R['v'][ir]
         
   def createBaseGrid_from_model(self,*karg,**kopt) :
      """creates a base grid from a model map or a dictionary of model maps"""
      from collections import OrderedDict
      if kopt.has_key('verbose') : 
         if kopt['verbose'] :
            print "createBaseGrid from model",karg,kopt
      if type(kopt['model']) == type({}) or type(kopt['model']) == type(OrderedDict()) :
         lk=kopt['model'].keys()
         MapGrid.clean(self,shape=kopt['model'][lk[0]].shape)
         self.createBaseGrid_empty(*karg,**kopt)
         for k in lk :
            self.newmap(k,value=kopt['model'][k].copy())
            self.map_info[k]={'comment':'map '+k,'private':False}
         return
      MapGrid.clean(self,shape=kopt['model'].shape)
      self.createBaseGrid_empty(*karg,**kopt)
      self.newmap('model',value=kopt['model'].copy())
      self.map_info['model']={'comment':'model map','private':False}

   def createBaseGrid_from_nrowsncols(self,*karg,**kopt) :
      """creates a base grid"""
      if kopt.has_key('verbose') : 
         if kopt['verbose'] :
            print "createBaseGrid ",karg,kopt
      MapGrid.clean(self,shape=[kopt['Rows'],kopt['Cols']])
      self.createBaseGrid_empty(*karg,**kopt)

   def createBaseGrid_from_gridaxis(self,*karg,**kopt) :
      """creates a base grid"""
      if kopt.has_key('verbose') : 
         if kopt['verbose'] :
            print "createBaseGrid ",karg,kopt
      MapGrid.clean(self)
      #
      if kopt.has_key('mapname') : self.mapname=kopt['mapname']
      #
      self.C = kopt['Cols'].__dict__
      self.ncols=len(kopt['Cols'])
      #
      self.R = kopt['Rows'].__dict__
      self.nrows=len(kopt['Rows'])
      #
      self.map_info['_col_index']={'comment':'index of cols','private':True}
      self.map_info['_col_values']={'comment':'values of cols','private':True}
      self.M['_col_index']=np.zeros([self.R['n'],self.C['n']],dtype='int')
      self.M['_col_values']=np.zeros([self.R['n'],self.C['n']],dtype='float')
      for ic in range(self.C['n']) : 
         self.M['_col_index'][:,ic] = ic
         self.M['_col_values'][:,ic] = self.C['v'][ic]
      #
      self.map_info['_row_index']={'comment':'index of rows','private':True}
      self.map_info['_row_values']={'comment':'values of rows','private':True}
      self.M['_row_index']=np.zeros([self.R['n'],self.C['n']],dtype='int')
      self.M['_row_values']=np.zeros([self.R['n'],self.C['n']],dtype='float')
      for ir in range(self.R['n']) : 
         self.M['_row_index'][ir] = ir
         self.M['_row_values'][ir] = self.R['v'][ir]

   def createBaseGrid(self,*karg,**kopt) :
      """creates a base grid"""
      kkopt=kopt.copy()
      kkopt['Cols']=karg[1]
      kkopt['Rows']=karg[0]
      self.createBaseGrid_from_nrowsncols(*karg,**kkopt)

   def getFromPickle(self,*karg,**kopt) :
      """get from pickle file"""
      if type(karg[0]) == type('') :
         try :
            self=pickle.load(open(karg[0],'r'))
            self.picke_name=karg[0]
         except :
            raise Error('Pickle %s not found or unreadable'%karg[0])
            return

   def pickle(self,fname) :
      import pickle
      f=open(fname,'w')
      pickle.dump(self.__dict__,f)
      f.close()

   def load(self,fname) :
      import pickle
      self.__dict__= pickle.load(open(fname,'r'))

   def slice(self,row_min=0,row_max=-1,col_min=0,col_max=-1) :
      """extract a subgrid in the range [row_min:row_max,col_min:col_max] 
         row_max=-1 is the last row
         col_max=-1 is the last col
         the object has no longer closed cols and rows event if the source is closed
         if the number of rows is even the centerRow is int(floor(nrows/2))-1 and center[0] is v[centerRow]
         if it is odd the centerRow is int(floor(nrows/2)) and center[0] is v[centerRow]
         the same for cols and center[1]
      """
      import copy
      import numpy as np
      # copies the object but the matrices or vectors
      new = self.copy(skipFields=['R','C','M'])
      # resizes R
      new.R = copy.deepcopy(self.R)
      new.R['v']=self.R['v'][row_min:row_max]
      new.R['n']=len(new.R['v'])
      new.R['min']=new.R['v'].min()
      new.R['max']=new.R['v'].max()
      new.R['closed']=False
      # resizes C
      new.C = copy.deepcopy(self.C)
      new.C['v']=self.C['v'][col_min:col_max]
      new.C['n']=len(new.C['v'])
      new.C['min']=new.C['v'].min()
      new.C['max']=new.C['v'].max()
      new.C['closed']=False
      # resizes M
      for k in self.M.keys() :
         k1 = k if k!='_col_index' and k!='_row_index' else '_original'+k
         new.M[k1]=self.M[k][row_min:row_max,col_min:col_max]
      new.M['_col_index'] = new.M['_original_col_index']-col_min
      new.M['_row_index'] = new.M['_original_row_index']-row_min
      new.shape=[new.R['n'],new.C['n']]
      new.centerRow=int(np.floor(new.R['n']/2))-1*(np.mod(new.R['n'],2) == 0)
      new.centerCol=int(np.floor(new.C['n']/2))-1*(np.mod(new.C['n'],2) == 0)
      new.center[0]=new.R['v'][new.centerRow]
      new.center[1]=new.C['v'][new.centerCol]
      return new
   def slice_row(self,irow_list) :
      """creates a submap whose rows are listes in irow_list
      """
      import copy
      import numpy as np
      # copies the object but the matrices or vectors
      new = self.copy()
      # resizes R
      new.R = copy.deepcopy(self.R)
      new.R['v']=self.R['v'][irow_list]
      new.R['n']=len(new.R['v'])
      new.R['min']=new.R['v'].min()
      new.R['max']=new.R['v'].max()
      new.R['closed']=False
      # resizes M
      for k in self.M.keys() :
         k1 = k if k!='_row_index' else '_original'+k
         new.M[k1]=self.M[k][irow_list]
      new.M['_row_index'] = new.zeros(dtype='int')
      for k in range(new.R['n']) : new.M['_row_index'][k]=k
      new.shape=new.SHAPE()
      new.centerRow=int(np.floor(new.R['n']/2))-1*(np.mod(new.R['n'],2) == 0)
      new.centerCol=int(np.floor(new.C['n']/2))-1*(np.mod(new.C['n'],2) == 0)
      new.center[0]=new.R['v'][new.centerRow]
      new.center[1]=new.C['v'][new.centerCol]
      return new
   def submap(self,xmin,xmax,ymin,ymax) :
      """extracts a submap with xmin <= col.v <= xmax, ymin <= row.v <= ymax
         values are interpolated if needed
      """
      import numpy as np
      def local_interp(x,x0,x1,y0,y1) : return (y1-y0)*(x-x0)/(x1-x0)+y0
      def allowed_name(name) :
         return name != '_col_index' and  name != '_row_index' and name != '_original_col_index' and name != '_original_row_index'
      # find the columns list
      #    elements selected are those for which xmin <= col.v <= xmax
      #    if xmin is midway the points in the list of values includes one point at left
      #    if xmax is midway the points in the list of values includes one point at right
      flag = np.ones(self.C['n'])
      if xmin != None : flag *= xmin <= self.C['v'] 
      if xmax != None : flag *= self.C['v'] <= xmax
      idxC=np.where(flag)[0]
      if len(idxC) == 0 :
         #idxC=np.array([np.where(xmin <= self.C['v'])[0][0]])
         raise Error("Error, extremes outside boundary, or both within an interval")
         return None
      xminXT=False ; xmaxXT=False  
      if xmin < self.C['v'][idxC[0]] and idxC[0] > 0 : 
         idxC=np.concatenate((np.array([idxC[0]-1]),idxC))
         xminXT=True
      if self.C['v'][idxC[-1]] < xmax and idxC[-1] < self.C['n']-1 : 
         idxC=np.concatenate((idxC,np.array([idxC[-1]+1])))
         xmaxXT=True
      # find the rows list
      #    elements selected are those for which ymin <= row.v <= ymax
      #    if ymin is midway the points in the list of values includes one point at left
      #    if ymax is midway the points in the list of values includes one point at right
      flag = np.ones(self.R['n'])
      if ymin != None : flag *= ymin <= self.R['v'] 
      if ymax != None : flag *= self.R['v'] <= ymax
      idxR=np.where(flag)[0]
      if len(idxR) == 0 :
         #idxR=np.array([np.where(ymin <= self.R['v'])[0][0]])
         raise Error("Error, extremes outside boundary, or both within an interval")
         return None
      yminXT=False ; ymaxXT=False  
      if ymin < self.R['v'][idxR[0]] and idxR[0] > 0 : 
         idxR=np.concatenate((np.array([idxR[0]-1]),idxR))
         yminXT=True
      if self.R['v'][idxR[-1]] < ymax and idxR[-1] < self.R['n']-1 : 
         idxR=np.concatenate((idxR,np.array([idxR[-1]+1])))
         ymaxXT=True
      # extracts sliced map
      new = self.slice(row_min=idxR[0],row_max=idxR[-1]+1,col_min=idxC[0],col_max=idxC[-1]+1)
      # if needed interpolates values at midway
      if xminXT :
         for k in self.M.keys() :
            if allowed_name(k) :
               new.M[k][:,0]=local_interp(xmin,new.C['v'][0],new.C['v'][1],new.M[k][:,0],new.M[k][:,1])
         new.C['v'][0] = xmin 
      if xmaxXT :
         for k in self.M.keys() :
            if allowed_name(k) :
               new.M[k][:,-1]=local_interp(xmax,new.C['v'][-2],new.C['v'][-1],new.M[k][:,-2],new.M[k][:,-1])
         new.C['v'][-1] = xmax 
      if xminXT or xmaxXT : new.C['sampling']=['not-uniform']
      if yminXT :
         for k in self.M.keys() :
            if allowed_name(k) :
               new.M[k][0,:]=local_interp(ymin,new.R['v'][0],new.R['v'][1],new.M[k][0,:],new.M[k][1,:])
         new.R['v'][0] = ymin 
      if ymaxXT :
         for k in self.M.keys() :
            if allowed_name(k) :
               new.M[k][-1,:]=local_interp(ymax,new.R['v'][-2],new.R['v'][-1],new.M[k][-2,:],new.M[k][-1,:])
         new.R['v'][-1] = ymax 
      if yminXT or ymaxXT : new.R['sampling']=['not-uniform']
      return new
   def __len__(self) :
      return self.shape[0]*self.shape[1]
   def __getitem__(self,*args) :
      if len(args) == 1 :
         try :
            return self.M[args[0]]
         except :
            raise Error("invalid argument")
      elif len(args) == 2 :
         try :
            return self.M[args[0]][args[1]]
         except :
            raise Error("invalid argument")
      elif len(args) == 3 :
         try :
            return self.M[args[0]][args[1]][args[2]]
         except :
            raise Error("invalid argument")
      elif len(args) == 4 :
         try :
            return self.M[args[0]][args[1]][args[2]]
         except :
            raise Error("invalid argument")
      else :
         if len(l) > self.naxis :
            raise Error("invalid argument")
         l=self.__dict__[args[0]]
         for ik in range(1,len(args)) : 
            try :
               l=l[args[ik]]
            except :
               raise Error(("Some error extracting element %d of "%ik)+str(args))
   def __setitem__(self,*args) :
      import copy
      if len(args) == 2 :
         try :
            self.M[args[0]]=copy.deepcopy(args[1])
         except :
            raise Error("invalid argument")
      elif len(args) == 3 :
         try :
            self.M[args[0]][args[1]]=copy.deepcopy(args[2])
         except :
            raise Error("invalid argument")
      elif len(args) == 4 :
         try :
            self.M[args[0]][args[1]][args[2]]=copy.deepcopy(args[3])
         except :
            raise Error("invalid argument")
      else :
         raise Error("invalid argument")
   def refresh(self) :
      if self.naxis == 2 :
         self.shape=(self.R['n'],self.C['n'])
      elif self.naxis == 3 :
         self.shape=(self.R['n'],self.C['n'],self.Z['n'])
      else :
         raise Error("Inconsistent naxis")
   def idx2colrow(self,idx) :
      "given a idx (a pixel number) returns corresponding col,row "
      import numpy as np
      return np.mod(idx,self.shape[1]),idx/self.shape[1]
   def colrow2idx(self,col,row) :
      "given col,row returns corresponding a idx (a pixel number) "
      import numpy as np
      return col+row*self.shape[1]
   def xy2colrow(self,x,y) :
     """xy to col row"""
     return (x-self.C['min'])/self.C['delta'],(y-self.R['min'])/self.R['delta']
   def colrow2xy(self,col,row) :
     """xy to col row"""
     return self.C['min']+col*self.C['delta'],self.R['min']+row*self.R['delta']
   def SHAPE(self) :
      return [self.R['n'],self.C['n']]
   def zeros(self,dtype='float',maxdim=None) :
      from numpy import zeros
      ii=self.naxis if (self.naxis <= maxdim) or (maxdim<=0) or maxdim==None else maxdim
      return zeros(list(self.SHAPE()),dtype=dtype)
      #return zeros(list(self.shape)[0:(maxdim+1)],dtype=dtype)
   def newmap(self,name,unit='',value=None,dtype='float',comment='') :
     from numpy import nan,zeros
     self.M[name] = self.zeros(dtype=dtype)
     self.unit[name] = unit
     if value == None :
        if type(dtype) == type('') :
           if dtype.strip() !='int' :
              self.M[name] += nan
        else :
           if dtype != type(1) :
              self.M[name] += nan
     else :
        self.M[name] += value
   def clean_matrices(self):
      self.M={}
      self.newmap('_row_values')
      self.newmap('_row_index',dtype='int')
      self.newmap('_col_values')
      self.newmap('_col_index',dtype='int')
   def set_row_periodic(self,period=None) :
      "makes Row periodic"
      import numpy as np
      self.R['period_ticks']=False
      if period!=None:
         self.R['period_ticks'] = np.floor(float(period)/self.R['delta'])
      else :
         self.R['period_ticks'] = float(self.R['n'])
   def set_row_scale(self,*karg,**kopt) :
      """ set_row_scale(string name)
         set_row_scale(string name,string unit)
         set_row_scale(string name,string unit,array values)
         set_row_scale(string name,string unit,float min, float max, int n)
         set_row_scale(string name,string unit,float min, float max, float delta)
         keywords:
            period = period of the row variable, default FALSE
      """ 
      from numpy import nan,zeros,array,round
      self.R['period_ticks']=False
      self.R['closed']=False
      self.R['name']=karg[0]
      if len(karg) < 2 :
         return
      self.R['unit']=karg[1]
      if len(karg) < 3 :
         return
      self.shape[0]=0
      if type(karg[2]) == type(array([])) :
         self.R['v'] = 1.*karg[2]
         self.R['min'] = self.R['v'].min()
         self.R['max'] = self.R['v'].max()
         self.R['n'] = len(self.R['v'])
         self.R['delta'] = self.R['v'][1]-self.R['v'][0]
      else :
         if len(karg) < 4 :
            raise Error("error: not enough arguments")
            return
         self.R['min']=karg[2]
         self.R['max']=karg[3]
         if type(karg[4]) == type(1) :
            self.R['n']=karg[4]
            self.R['delta']=(karg[3]-karg[2])/float(karg[4])
         else :
            self.R['delta']=karg[4]
            self.R['n']=int(round((karg[3]-karg[2])/float(karg[4])))
      self.shape[0]=self.R['n']*1
      if self.shape[0]*self.shape[1] > 0:
         self.clean_matrices()
      if kopt.has_key('periodic') :
         periodic = kopt['periodic']
         if periodic != None and period != False:
            if periodic == True :
               self.R['period_ticks']=float(self.R['n'])
            else :
               self.R['period_ticks']=periodic/float(self.R['step'])
         else :
            self.R['period_ticks']=False
   def set_col_periodic(self,period=None) :
      "makes Col periodic"
      import numpy as np
      self.C['period_ticks']=False
      if period!=None:
         self.C['period_ticks'] = np.floor(float(period)/self.C['delta'])
      else :
         self.C['period_ticks'] = float(self.C['n'])
   def set_col_scale(self,*karg,**kopt) :
      """ set_col_scale(string name)
         set_col_scale(string name,string unit)
         set_col_scale(string name,string unit,array values)
         set_col_scale(string name,string unit,float min, float max, int n)
         set_col_scale(string name,string unit,float min, float max, float delta)
      """ 
      from numpy import nan,zeros,array,round
      self.C['period_ticks']=-1
      self.C['closed']=False
      self.C['name']=karg[0]
      if len(karg) < 2 :
         return
      self.C['unit']=karg[1]
      if len(karg) < 3 :
         return
      self.shape[1]=0
      if type(karg[2]) == type(array([])) :
         self.C['v'] = 1.*karg[2]
         self.C['min'] = self.C['v'].min()
         self.C['max'] = self.C['v'].max()
         self.C['n'] = len(self.C['v'])
         self.C['delta'] = self.C['v'][1]-self.C['v'][0]
      else :
         if len(karg) < 4 :
            raise Error("error: not enough arguments")
            return
         self.C['min']=karg[2]
         self.C['max']=karg[3]
         if type(karg[5]) == type(1) :
            self.C['n']=karg[4]
            self.C['delta']=(karg[3]-karg[2])/float(karg[4])
         else :
            self.C['delta']=karg[4]
            self.C['n']=int(round((karg[3]-karg[2])/float(karg[4])))
      self.shape[1]=self.C['n']*1
      if self.shape[0]*self.shape[1] > 0:
         self.clean_matrices()
      if kopt.has_key('periodic') :
         periodic = kopt['periodic']
         if periodic != None and period != False:
            if periodic == True :
               self.C['period_ticks']=float(self.C['n'])
            else :
               self.C['period_ticks']=periodic/float(self.C['step'])
         else :
            self.C['period_ticks']=False
   def right_close_row(self,period=False) :
      """ copyes the first row assuming it has the same value of the first, used to give maps with cyclicalBoundaries """
      from numpy import concatenate,ones
      self.R['v'] =  concatenate([self.R['v'],ones(1)*self.R['v'][-1]+self.R['delta']])
      self.R['n'] =  len(self.R['v'])
      self.R['min'] =  self.R['v'].min()
      self.R['max'] =  self.R['v'].max()
      self.R['closed']=True
      if period != None and period != False:
         if period == True :
            self.R['period_ticks']=float(self.R['n'])
         else :
            self.R['period_ticks']=period/float(self.R['step'])
      else :
         self.R['period_ticks']=False
      self.shape[0]=len(self.R['v'])
      if self.M!=None and self.M!={}:
         for k in self.M.keys() :
            self.M[k]=concatenate([self.M[k],self.M[k][0:1]])
   def right_close_col(self,period=False,right_col_value=None) :
      """ copyes the first row assuming it has the same value of the first, used to give maps with cyclicalBoundaries """
      from numpy import concatenate,ones,array,zeros
      import copy
      self.C['v'] =  concatenate([self.C['v'],ones(1)*self.C['v'][-1]+self.C['delta']])
      if right_col_value != None :
         try :
            self.C['v'][-1]=float(right_col_value)
         except :
            pass
      self.C['n'] =  len(self.C['v'])
      self.C['min'] =  self.C['v'].min()
      self.C['max'] =  self.C['v'].max()
      self.C['closed']=True
      if period != None and period != False:
         if period == True :
            self.C['period_ticks']=float(self.C['n'])
         else :
            self.C['period_ticks']=period/float(self.C['step'])
      else :
         self.C['period_ticks']=False
      self.shape[1]=len(self.C['v'])
      if self.M!=None and self.M!={} :
         for k in self.M.keys() :
            M=copy.deepcopy(self.M[k])
            self.M[k]=zeros(M.shape+array([0,1]))
            if k=='_row_values' :
               for r in range(self.R['n']) :
                  self.M[k][r]=concatenate([M[r,:],M[r,0]*ones(1)])
            elif k=='_col_values' :
               for r in range(self.R['n']) :
                  self.M[k][r]=concatenate([M[r,:],M[r,-1]+self.C['delta']*ones(1)])
                  if right_col_value != None :
                     try :
                        self.M[k][r][-1]=float(right_col_value)
                     except :
                        pass
            elif k=='_row_index' :
               for r in range(self.R['n']) :
                  self.M[k][r]=concatenate([M[r,:],M[r,0]*ones(1)])
            elif k=='_col_index' :
               for r in range(self.R['n']) :
                  self.M[k][r]=concatenate([M[r,:],M[r,-1]+ones(1)])
            else :
               for r in range(self.R['n']) :
                  self.M[k][r]=concatenate([M[r,:],M[r,0:1]])
   def keys(self,private=False,all=False) :
      p = []
      for k in self.M.keys() :
         if k[0]!='_' :
            if not private :
               p.append(k)
         else :
            if private or all :
               p.append(k)
      return p
   def has_key(self,name) :
      from numpy import array
      return self.M.has_key(name)
   def transpose(self) :
      import copy
      from numpy import transpose
      if self.naxis != 2 :
         raise Error("transpose is defined just for naxis=2")
      M = MapGrid()
      M.info = copy.deepcopy(self.info)
      M.unit = copy.deepcopy(self.unit)
      M.R = copy.deepcopy(self.C)
      M.C = copy.deepcopy(self.R)
      M.shape=[M.R['n'],M.C['n']]
      for k in self.M.keys() :
         M.M[k]=transpose(self.M[k])
      return M
   def create_interpolation_function(self,*args,**kargs) :
      """Creates the interpolation (2d) functions"""
      from scipy import interpolate
      from numpy import array
      if self.naxis != 2 :
         raise Error("create_interpolation_function is defined just for naxis=2")
      try :
         kind=kargs['kind']
      except :
         kind='linear'
      if (array(['linear','cubic','quintic'])==kind).sum() == 0 :
         print "Kind %s not allowed"%kind
         return None
      if self.f != type({}) :
         self.f={}
      if len(args) == 0 :
         ln=self.keys()
      else :
         ln = args
      for k in ln :
         self.f[k]=interpolate.interp2d(self.R['v'],self.C['v'],self.M[k],kind=kind)
   def interpolate(self,name,x_col,y_row) :
      from numpy import array
      if self.naxis != 2 :
         raise Error("interpolate is defined just for naxis=2")
      if self.f != type({}) :
         self.f={}
      if not self.f.has_key(name) :
         try :
            print 'creating',
            self.create_interpolation_function(name)
         except :
            print "Matrix %s not found in creating interpolation function"%name
      else :
         try :
            return self.f[k](y_row,x_col)
         except :
            raise Error("Matrix %s not found or out of bounds"%name)
            return None
   def copy(self,skipFields=None) :
      import copy
      import numpy as np
      if skipFields == None or skipFields == '' or skipFields == [] : return copy.deepcopy(self)
      _skipFields=[]
      for k in [skipFields] if type(skipFields) == type('') else skipFields :
         if k.strip() != '' : _skipFields.append(k.strip())
      _skipFields = np.array(['']) if len(_skipFields) == 0 else np.array(_skipFields) 
      new=MapGrid()
      for k in self.__dict__.keys() :
         if (_skipFields == k).sum() == 0 :
            new.__dict__[k]=copy.deepcopy(self.__dict__[k])
      return new
   def rowClip(self,row,offset) :
      """applies a clipping to row number, return clippedRow,flagBad
      flagBad = -10 : under flow
      flagBad = -1 : overflow      """
      if self.R['period_ticks']>0 : 
         return np.mod(row+offset,self.R['period_ticks']),np.zeros(len(row))
      else :
         row1=row+offset
         bad = -10*(row1<0)-(self.R['n']-1<row1)
         return row1*(bad==0),bad
   def colClip(self,col,offset) :
      """applies a clipping to col number, return clippedRow,flagBad
      flagBad = -10 : under flow
      flagBad = -1 : overflow"""
      if self.C['period_ticks']>0 : 
         return np.mod(col+offset,self.C['period_ticks']),np.zeros(len(col))
      else :
         col1=col+offset
         bad = -10*(col1<0)-(self.C['n']-1<col1)
         return col1*(bad==0),bad
   def XY2RowCol(self,x_col,y_row) :
      import numpy as np
      return (y_row-self.R['min'])/self.R['delta'],(x_col-self.C['min'])/self.C['delta']
   def RowCol2XY(self,row,col) :
      return col*self.C['delta']+self.C['min'],row*self.R['delta']+self.R['min']
   def downgrade(self,FactorR,FactorC) :
      """reduces resolution of a given factor
         values outside the resampled points are removed
      """
      if self.naxis != 2 : raise Error("downgrade is defined just for naxis=2")
      import copy
      import numpy as np
      new=self.copy()
      new.clean()
      try :
         new.info=copy.deepcopy(self.info)
      except : 
         pass
      try :
         new.Info=copy.deepcopy(self.Info)
      except : 
         pass
      for k in ['unit','name','dim','dimid','textual'] :
         new.C[k]=copy.deepcopy(self.C[k])
         new.R[k]=copy.deepcopy(self.R[k])
      idxC=np.where(np.mod(np.arange(self.C['n'],dtype='int'),int(FactorC))==0)[0]
      new.C['v']=self.C['v'][idxC]
      new.C['n']=len(idxC)
      new.C['min']=new.C['v'].min()
      new.C['max']=new.C['v'].max()
      new.C['delta']=new.C['v'][0:2].ptp()
      idxR=np.where(np.mod(np.arange(self.R['n'],dtype='int'),int(FactorR))==0)[0]
      new.R['v']=self.R['v'][idxR]
      new.R['n']=len(idxR)
      new.R['min']=new.R['v'].min()
      new.R['max']=new.R['v'].max()
      new.R['delta']=new.R['v'][0:2].ptp()
      ROWS=np.array(copy.deepcopy(self.M['_row_index']),dtype='int')
      COLS=np.array(copy.deepcopy(self.M['_col_index']),dtype='int')
      shape2=copy.deepcopy(ROWS.shape)
      shape1=shape2[0]*shape2[1]
      ROWS.shape=shape1
      COLS.shape=shape1
      flagROWS=np.mod(ROWS,int(FactorR))==0
      flagCOLS=np.mod(COLS,int(FactorC))==0
      idxRC=np.where(flagROWS*flagCOLS)[0]
      for k in self.M.keys() :
         aa=copy.deepcopy(self.M[k])
         aa.shape=shape1
         if k!='_row_index' and k!='_col_index' :
            new.M[k]=aa[idxRC]
         else :
            new.M[k]=np.array(aa[idxRC]/FactorR,dtype='int')
      for k in new.M.keys() : new.M[k].shape=(new.R['n'],new.C['n'])
      new.shape=(new.R['n'],new.C['n'])
      new.center=np.zeros(2)
      new.centerRow=self.centerRow/FactorR
      new.centerCol=self.centerCol/FactorC
      new.pickle_name = ''
      new.unit=copy.deepcopy(self.unit)
      self.f={}
      return new
   def bilinearXY(self,component,x_col,y_row,returnVal=None,returnDelta=False) :
      """
         interpolates a 2d map by using bilinear interpolation
         clips to zero all the components outside the limits of the map
         unless /returNaN is set in which case returns NaN
         periodicColumns = True column indexes are considered periodic
         periodicRows = True row indexes are considered periodic
         if returnDelta=True returns result,deltaX,deltaY (default False)
      """
      if self.naxis != 2 : raise Error("bilinearXY is defined just for naxis=2")
      from numpy import mod,nan,zeros,array,round,arange,floor,where
      if returnVal == None :
         retVal = nan
      else :
         retVal = returnVal*1
      row,col = self.XY2RowCol(x_col,y_row)
      #
      drow=mod(row,1)
      dcol=mod(col,1)
      row00,badR00=self.rowClip(array(floor(row),dtype='int'),0)
      row01 = row00
      row10,badR10 = self.rowClip(row00,1)
      row11 = row10
      #
      col00,badC00=self.colClip(array(floor(col),dtype='int'),0)
      col00=array(col00,dtype='int')
      col10=col00
      col01,badC01=self.colClip(col00,1)
      col01=array(col01,dtype='int')
      col11=col01
      #
      if type(component)==type('') :
         V00 = self.M[component][row00,col00]
         V01 = self.M[component][row01,col01]
         V10 = self.M[component][row10,col10]
         V11 = self.M[component][row11,col11]
      else :
         V00 = component[row00,col00]
         V01 = component[row01,col01]
         V10 = component[row10,col10]
         V11 = component[row11,col11]
      A=V00+dcol*(V01-V00)*(badC01==0)
      B=V10+dcol*(V11-V10)*(badC01==0)
      result=(badR10==0)*drow*(B-A)+A
      result[where(badR00!=0)[0]]=retVal
      result[where(badC00!=0)[0]]=retVal
      result[where((badR10!=0)*(drow > 0))[0]]=retVal
      result[where((badC01!=0)*(dcol > 0))[0]]=retVal
      if returnDelta : 
         return result,dcol,drow
      return result
   def imshow(self,component,**karg) :
      from matplotlib import pyplot as plt
      from scipy import interp
      from matplotlib import cm
      #
      kkarg=karg.copy()
      if not kkarg.has_key('bar') : kkarg['bar']=False
      if not kkarg.has_key('cmap') : kkarg['cmap']='hsv'
      if not kkarg.has_key('dbi') : kkarg['dbi']=False
      if not kkarg.has_key('log') : kkarg['log']=False
      if not kkarg.has_key('slices') : kkarg['slices']=None
      if not kkarg.has_key('xticks') : kkarg['xticks']=True
      if not kkarg.has_key('yticks') : kkarg['yticks']=True
      if not kkarg.has_key('maptitle') : kkarg['maptitle']=None
      if not kkarg.has_key('vmin') : kkarg['vmin']=None
      if not kkarg.has_key('vmax') : kkarg['vmax']=None
      if not kkarg.has_key('interpolation') : kkarg['interpolation']=None
      if not kkarg.has_key('newfig') : kkarg['newfig']=True
      if not kkarg.has_key('DrawOrShow') : kkarg['DrawOrShow']='show'
      #
      DrawOrShow=kkarg.pop('DrawOrShow')
      #
      cmap=kkarg.pop('cmap')
      if type(cmap) == type("") :
         try :
            _cm=cm.__dict__[cmap]
         except :
            if self.isVerbose() :
               print "required cmap ",cmap," no found, replaced with 'hsv'"
               print "allowed values "
               print cm.__dict__.keys()
      else :
         _cm=cmap
      #
      xticks=kkarg.pop('xticks')
      if xticks.__class__!=[].__class__ and xticks.__class__!=().__class__ and xticks.__class__!=np.array([]).__class__ : 
         _xticks=xticks!= None and xticks!= False 
      else :
         _xticks=True
      yticks=kkarg.pop('yticks')
      if yticks.__class__!=[].__class__ and yticks.__class__!=().__class__ and yticks.__class__!=np.array([]).__class__ :
         _yticks = yticks!= None and yticks!= False 
      else :
         _yticks=True
      #
      newfig=kkarg.pop('newfig')
      maptitle=kkarg.pop('maptitle')
      slices=kkarg.pop('slices')
      dbi=kkarg.pop('dbi')
      log=kkarg.pop('log')
      bar=kkarg.pop('bar')
      #
      if newfig : plt.figure()
      #
      kkarg['cmap']=_cm
      kkarg['origin']='lower'
      if type(component) == type('') :
         if self.naxis != 2 and slicep==None : raise Error("imshow() needs to define the slice")
         if self.isVerbose() :
            print 'component is a string ',
            print component
         title=component+''
         if type(maptitle) == type('') : title = maptitle+title
         if self.isVerbose() : print title
         if self.naxis == 2 :
            mm = self[component]
         elif self.naxis == 3 :
            mm = self[component][:,:,slices]
         else :
            raise Error("imshow() for naxis not 2 or 3")
         if dbi :
            plt.imshow(10*np.log10(mm),**kkarg)
            title+=', dbi'
         elif log :
            plt.imshow(np.log10(mm),**kkarg)
            title+=', log'
         else :
            plt.imshow(mm,**kkarg)
      else :
         if self.isVerbose() : print 'component is an array'
         title=''
         if type(maptitle) == type('') : title = maptitle
         if self.isVerbose() : print title
         if dbi :
            plt.imshow(10*np.log10(component),**kkarg)
            title+=', dbi'
         elif log :
            plt.imshow(np.log10(component),**kkarg)
            title+=', log'
         else :
            plt.imshow(component,**kkarg)
      if bar!=False and bar !='' and bar != None: 
         if bar == True or bar == 'v' or bar == 'V' :
            plt.colorbar(orientation='vertical')
         else :
            plt.colorbar(orientation='horizontal')
      a=self.C['name'].strip()
      if _xticks  :
         if self.C['unit'].strip() != '' :
            a+=' ['+self.C['unit'].strip()+']'
         else :
            a+=' [pixel]'
      plt.xlabel(a)
      a=self.R['name'].strip()
      if _yticks :
         if self.R['unit'].strip() != '' :
            a+=' ['+self.R['unit'].strip()+']'
         else :
            a+=' [pixel]'
      plt.ylabel(a)
      if xticks.__class__!=[].__class__ and xticks.__class__!=().__class__ and xticks.__class__!=np.array([]).__class__ :
         if type(xticks)==type(0) or type(xticks)==type(0.):
            xt=np.arange(0,self.C['n'],self.C['n']/int(xticks))
         else :
            xt=np.arange(0,self.C['n'],self.C['n']/4)
      else :
         xt=np.array(xticks)
      xt1=np.arange(self.C['n'])
      if _xticks:
         yt1=self.M['_col_values'][0]
      else :
         yt1=self.M['_col_index'][0]
      plt.xticks(xt,interp(xt,xt1,yt1))
      if yticks.__class__!=[].__class__ and yticks.__class__!=().__class__ and yticks.__class__!=np.array([]).__class__ :
         if type(yticks)==type(0) or type(yticks)==type(0.):
            xt=np.arange(0,self.R['n'],self.R['n']/int(yticks))
         else :
            xt=np.arange(0,self.R['n'],self.R['n']/4)
      else :
         xt=np.array(yticks)
      xt1=np.arange(self.R['n'])
      if _yticks :
         yt1=self.M['_row_values'][:,0]
      else :
         yt1=self.M['_row_index'][:,0]
      plt.yticks(xt,interp(xt,xt1,yt1))
      plt.title(title)
      if DrawOrShow.lower().strip()=='show' :
         plt.show()
      else :
         plt.draw()
   def contour(self,arg,Levels=None,labelLevels=True,lw=2,colors='k') :
      """overlaps a contour plot over an imshow
      returns Contours Object and Labels Object
      """
      from matplotlib import pyplot as plt
      CS=plt.contour(self['_col_index'],self['_row_index'],self[arg],Levels,linewidth=lw,colors=colors)
      if not labelLevels :
         return CS, None
      h=plt.clabel(CS)
      return CS,h
   def radius(self,shape1=False,row0=0.,col0=0.) :
      """returns a map with the radii of the map with respect to the center"""
      if shape1 :
         r=((self.M['_row_values']-self.center[0]-row0)**2+(self.M['_col_values']-self.center[0]-col0)**2)**0.5
         r.shape=r.shape[0]*r.shape[1]
         return r
      return ((self.M['_row_values']-self.center[0]-row0)**2+(self.M['_col_values']-self.center[0]-col0)**2)**0.5
   def gaussian(self,sigma,row0=0.,col0=0.,normalized=True) :
      """returns a gaussian based on map
            
         normalized = True (default) to have a distribution whose integral is 1
      """
      import numpy as np
      return np.exp(-0.5*(self.radius(row0=row0,col0=col0)/sigma)**2)*(1./(2*np.pi*sigma**2) if normalized else 1.)
   def elliptic_gaussian(self,sigma_xx,sigma_yy,row0=0.,col0=0.,normalized=True,sigma_xy=None) :
         """returns a elliptical gaussian based on map
            given sigma_xx, sigma_xy and sigma_yy (squared values)
            sigma_xy is passed as a keyword, defaul 0
            
            normalized = True (default) to have a distribution whose integral is 1
         """
         import numpy as np
         X = (self.M['_row_values']-self.center[0]-row0)
         Y = (self.M['_col_values']-self.center[0]-col0)
         a=X**2/sigma_xx
         b=X*Y/sigma_xy if sigma_xy != None else 0.
         c=Y**2/sigma_yy
         if normalized :
            n=sigma_xx*sigma_yy 
            n+=-sigma_xy*sigma_xy if sigma_xy != None else 0.
            n=2*np.pi*n**0.5
         else :
            n=1
         return np.exp(-0.5*(a+b+c))/n
   def cutted_map(self,mapname,innerCut=None,outerCut=None,cuttedValue=0.,acceptOutside=False):
      """returns a map cutted in circle for radii smaller than a innerCut or larger than outerCut
         acceptOutside=True reverses the logic
      """
      if self.naxis != 2 : raise Error("cutted_map is defined just for naxis=2")
      import numpy as np
      import copy
      if type(mapname) == type('') :
         cmap=copy.deepcopy(self[mapname])
      else :
         cmap=copy.deepcopy(mapname)
      if outerCut == None and innerCut == None : return cmap
      shape2=cmap.shape
      shape1=cmap.shape[0]*cmap.shape[1]
      radius=self.radius()
      radius.shape=shape1
      flag=np.zeros(len(radius))
      if outerCut != None :
         flag+=outerCut<radius
      if innerCut != None :
         flag+=radius < innerCut
      if acceptOutside : flag = flag==0
      idx=np.where(flag!=0)[0]
      if len(idx) == 0 :
         return cmap
      elif len(idx) == shape1 :
         return cmap*0+cuttedValue
      else :
         cmap.shape=shape1
         cmap[idx]=cuttedValue
         cmap.shape=shape2
         return cmap
   def cellArea(self) :
      "returns the area of a cell"
      return self.C['delta']*self.R['delta']
   def trapz2dWeights(self) :
      "returns the trapezoidal integration weights matrix"
      weights=np.ones([self.C['n'],self.R['n']])*4.
      weights[0:self.C['n'],0]=2.
      weights[0:self.C['n'],self.R['n']-1]=2.
      weights[0,0:self.R['n']]=2.
      weights[self.C['n']-1,0:self.R['n']]=2.
      weights[0,0]=1.
      weights[self.C['n']-1,0]=1.
      weights[self.C['n']-1,self.R['n']-1]=1.
      weights[0,self.R['n']-1]=1.
      return weights
   def trapz2d(self,mapname,doNotScaleByCellArea=False,sortArray=True,returnItg=False,innerCut=None,outerCut=None) :
      """returns the trapzd 2d integration of a map
         doNotScaleByCellArea = True the result is not multiplied by the area of the cell
      """
      import numpy as np
      w=self.trapz2dWeights()*0.25
      if not doNotScaleByCellArea : w*=self.cellArea()
      if type(mapname) == type('') :
         itg=self.cutted_map(w*self[mapname],innerCut=innerCut,outerCut=outerCut,cuttedValue=0.)
      else :
         itg=self.cutted_map(w*mapname,innerCut=innerCut,outerCut=outerCut,cuttedValue=0.)
      if returnItg : return itg
      itg.shape=itg.shape[0]*itg.shape[1]
      if sortArray : return np.sort(itg).sum()
      return itg.sum()
   def simpson2dWeights(self,scaledWeights=False) :
      """returns the sympson integration weights matrix
         simpson integration for a matrix M is (weights*M).sum()*cellArea/9,
         if scaledWeights == False (default) the weighted matrix is not scaled by cellArea/9, otherwise it is scaled
      """
      import numpy as np
      from numpy import where,mod
      w=[]
      row=np.zeros(self.C['n']) ; idx=np.arange(len(row)) ; row[where(mod(idx,2))[0]]=4 ; row[where(mod(idx,2)==0)[0]]=2 ; row[0]=1; row[-1]=1 ; w.append(row)
      for r in range(1,self.R['n']-2) :
         if mod(r,2)==1 :
            row=np.zeros(self.C['n']) ; idx=np.arange(len(row)) ; row[where(mod(idx,2))[0]]=16 ; row[where(mod(idx,2)==0)[0]]=8 ; row[0]=4; row[-1]=4 ; w.append(row)
         else : 
            row=np.zeros(self.C['n']) ; idx=np.arange(len(row)) ; row[where(mod(idx,2))[0]]=8 ; row[where(mod(idx,2)==0)[0]]=4 ; row[0]=2; row[-1]=2 ; w.append(row)
      row=np.zeros(self.C['n']) ; idx=np.arange(len(row)) ; row[where(mod(idx,2))[0]]=16 ; row[where(mod(idx,2)==0)[0]]=8 ; row[0]=4; row[-1]=4 ; w.append(row)
      row=np.zeros(self.C['n']) ; idx=np.arange(len(row)) ; row[where(mod(idx,2))[0]]=4 ; row[where(mod(idx,2)==0)[0]]=2 ; row[0]=1; row[-1]=1 ; w.append(row)
      if scaledWeights : return np.array(w)*self.cellArea()/9.
      return np.array(w)
   def simpson2d(self,mapname,doNotScaleByCellArea=False,sortArray=True,returnItg=False,innerCut=None,outerCut=None) :
      """returns the sympson 2d integration of a map
         doNotScaleByCellArea = True the result is not multiplied by the area of the cell
      """
      import numpy as np
      w=self.simpson2dWeights()*1./9.
      if not doNotScaleByCellArea : w*=self.cellArea()
      if type(mapname) == type('') :
         itg=self.cutted_map(w*self[mapname],innerCut=innerCut,outerCut=outerCut,cuttedValue=0.)
      else :
         itg=self.cutted_map(w*mapname,innerCut=innerCut,outerCut=outerCut,cuttedValue=0.)
      if returnItg : return itg
      itg.shape=itg.shape[0]*itg.shape[1]
      if sortArray : return np.sort(itg).sum()
      return itg.sum()
   def copy_map(self,mapname) :
      "returns a copy of map mapname"
      import copy 
      try :
         return copy.deepcopy(self.M[mapname])
      except :
         return
   def add_dbi_map(self,mapname,newmap_name=None) :
      "adds the dbi map of the mapname map, the name of the new map is dbi-mapname"
      import numpy as np
      _new = newmap_name if newmap_name!=None and newmap_name!='' else 'dbi-'+mapname
      try :
         self.M[_new]=10*np.log10(self[mapname])
      except :
         raise Error("Impossible to create %s "%_new)
         return None
      if self.isVerbose() : "Created %s "%_new
      return _new
   def minimax(self,mapname) :
      "return min and max values of map mapname avoiding NaN and infinite numbers"
      import numpy as np
      a=self.copy_map(mapname)
      if a == None : return None
      a.shape=a.shape[0]*a.shape[1]
      idx=np.where(np.isfinite(a)*(1-np.isnan(a)))[0]
      if idx == None : return None
      if len(idx) == 0 : return None
      return a[idx].min(),a[idx].max()
   def finitePixels(self,mapname,return_idx=False) :
      "returns the list of pixels which are finite"
      import numpy as np
      a=self.copy_map(mapname)
      if a == None : return None
      a.shape=a.shape[0]*a.shape[1]
      idx=np.where(np.isfinite(a)*(1-np.isnan(a)))[0]
      return idx
   def histogram(mapName,levels=None,vmin=None,vmax=None,finite=False,nan=False) :
      "returns a fast_histogram object of a map"
      return fast_histogram(self[mapName],levels=levels,vmin=vmin,vmax=vmax,finite=finite,nan=nan)
   def map2fitsTableColumn(self,arg,fits_type='D') :
      "converts a map into a 2d fits column"
      import pyfits
      fmt=str(self.shape[1])+fits_type
      try :
         unit=self.unit[arg]
      except :
         unit='none'
      return pyfits.Column(name=arg,unit=unit,format=fmt,array=self[arg])
   def row_fft(self,argument,axis=-1,return_freq=False,shifted=False) :
      """returns the row by row FFT of 'argument'
         argument can be either a name or matrix
         if return_freq=True returns just the frequencies
         if shifted=True applies fftshift to have 0 freq at center
      """
      import numpy as np
      if return_freq :
         rf=np.fft.fftfreq(self.SHAPE()[self.C['n']]) 
         if shifted :
            rf=np.fft.fftshift(rf) 
         return rf
      f=self.zeros()*1j
      if type(argument) == type('') :
         for k in range(self.R['n']) :
            f[k]=np.fft.fft(self[argument][k])
      else :
         for k in range(self.R['n']) :
            f[k]=np.fft.fft(argument[k],axis=-1)
      if shifted :
         for k in range(self.R['n']) :
            f[k]=np.fft.fftshift(f[k],axis=-1) 
      return f
   def row_ifft(self,argument) :
      """returns the row by row IFFT of 'argument'
         argument can be either a name or matrix
      """
      import numpy as np
      ift=self.zeros()*1j
      if type(argument) == type('') :
         for k in range(self.R['n']) :
            ift[k]=np.fft.ifft(self[argument][k])
      else :
         for k in range(self.R['n']) :
            ift[k]=np.fft.ifft(argument[k],axis=-1)
      return ift
   def fitsTable(self,*arg,**karg) :
      """convert to a fits table
         doNotAddPrivateTables = True only tables which are not private are added
         exclude = list of tables to be excluded
      """
      import pyfits
      import time
      if karg.has_key('doNotAddPrivateTables') :
         if karg['doNotAddPrivateTables'] :
            lsn=[]
         else :
            lsn=self.keys(private=True)
      else :
         lsn=self.keys(private=True)
      if karg.has_key('exclude') :
         excluded=karg['exclude']
         if len(excluded) == 0 : excluded=None
      else :
         excluded=None
      if len(arg) == 0 :
         for k in self.keys() :
            lsn.append(k)
      else :
         for k in arg :
            lsn.append(k)
      if excluded == None :
         names=lsn
      else :
         names=[]
         for k in lsn :
            try :
               excluded.index(k)
            except :
               names.append(k)
      if self.isVerbose() :
         print names
         print excluded
      thdu=[]
      for k in names :
         thdu.append(self.map2fitsTableColumn(k))
      fthdu=pyfits.new_table(pyfits.ColDefs(thdu))
      # those general
      fthdu.update_ext_name(self.mapname)
      fthdu.header.update('mapname',self.mapname,'name of the map')
      fthdu.header.update('created',time.asctime())
      fthdu.header.update('row_name',self.R['name'],'name of row')
      fthdu.header.update('row_n',self.shape[0],'number of rows in a map')
      fthdu.header.update('row_unit',self.R['unit'],'unit of row')
      fthdu.header.update('row_min',self.R['min'],'row min value')
      fthdu.header.update('row_max',self.R['max'],'row max value')
      fthdu.header.update('row_step',self.R['delta'],'row step')
      fthdu.header.update('col_name',self.C['name'],'name of col')
      fthdu.header.update('col_n',self.shape[1],'number of cols in a map')
      fthdu.header.update('col_unit',self.C['unit'],'unit of row')
      fthdu.header.update('col_min',self.C['min'],'col min value')
      fthdu.header.update('col_max',self.C['max'],'col max value')
      fthdu.header.update('col_step',self.C['delta'],'col step')
      fthdu.header.update('raster','n','if y maps are rastered')
      fthdu.header.add_comment('MapGrid binTable FITS format')
      fthdu.header.add_comment('MapGrid ')
      fthdu.header.add_comment('  a collection of 2D maps')
      fthdu.header.add_comment('  rows are Y values, cols are X values')
      fthdu.header.add_comment('  a table is made of row_n x col_n elements')
      fthdu.header.add_comment('  first element i 0')
      fthdu.header.add_comment('  row is increasing faster')
      fthdu.header.add_comment('  it is assumed rows and cols are sampled uniformly')
      fthdu.header.add_comment('  but this is not granted, in this case look at')
      fthdu.header.add_comment('  _row_values, _col_values tables')
      fthdu.header.add_comment('MapGrid binTable FITS format')
      fthdu.header.add_comment('  each map is a column of the FITS table')
      fthdu.header.add_comment('  see RASTER keyword to know wether 2D')
      fthdu.header.add_comment('  maps are stored in raster fashion')
      fthdu.header.add_comment('  if rasterized columns are 1D ')
      fthdu.header.add_comment('  rows sequentially concatenated')
      return fthdu
   def get_fitsTable(self,filename,ihdu=1,Verbose=False) :
      """gets a fits table"""
      import numpy as np
      import pyfits
      self._p=pyfits.open(filename)
      self._h=self._p[ihdu].header 
      self.mapname=self._h['mapname']
      #
      for k in self.C.keys() :
         nname='col_'+k 
         try :
            self.C[k]=self._h[nname]
         except :
            nname='hierarch col_'+k 
            try :
               self.C[k]=self._h[nname]
            except :
               pass
      self.C['v']=np.arange(self.C['n'])/float(self.C['n'])*(self.C['max']-self.C['min'])+self.C['min']
      try :
         if not np.isfinite(self.C['delta']) :
            self.C['delta']=self.C['v'][1]-self.C['v'][0]
      except :
         self.C['delta']=self.C['v'][1]-self.C['v'][0]
      #
      for k in self.R.keys() :
         nname='row_'+k 
         try :
            self.R[k]=self._h[nname]
         except :
            nname='hierarch row_'+k 
            try :
               self.R[k]=self._h[nname]
            except :
               pass
      self.R['v']=np.arange(self.R['n'])/float(self.R['n'])*(self.R['max']-self.R['min'])+self.R['min']
      try :
         if not np.isfinite(self.R['delta']) :
            self.R['delta']=self.R['v'][1]-self.R['v'][0]
      except :
         self.R['delta']=self.R['v'][1]-self.R['v'][0]
      self.shape=self.SHAPE()
      #
      for iaxis in range(1,self._h['TFIELDS']+1) :
         kTYPE='TTYPE%d'%iaxis
         kUNIT='TUNIT%d'%iaxis
         nn=self._h[kTYPE].strip()
         try :
            uu=self._h[kUNIT].strip() 
         except :
            uu=''
         if Verbose == True : print iaxis,kTYPE,nn,kUNIT,uu,
         self.newmap(nn,value=self._p[ihdu].data[nn],unit=uu)
         if Verbose == True : print self[nn].shape,self.SHAPE()
      #
      try :
         self.R['v']=self['_row_values'][:,0]
         self.R['v'].shape=self.R['v'].size
         self.R['delta']=self.R['v'][1]-self.R['v'][0]
      except :
         pass
      #
      try :
         self.C['v']=self['_col_values'][0]
         self.C['v'].shape=self.C['v'].size
         self.C['delta']=self.C['v'][1]-self.C['v'][0]
      except :
         pass

   
class IndexHDU :
   def __init__(self,hdu) :
      import copy
      if hdu == None :
         return
      self.extname=copy.deepcopy(hdu.data['extname'])
      self.extnum=copy.deepcopy(hdu.data['extnum'])
      self.type=copy.deepcopy(hdu.data['type'])
      self.comment=copy.deepcopy(hdu.data['comment'])
   def __len__(self):
      return len(self.extname)
   def __getitem__(self,i) :
      import numpy
      if type(i) == type('') :
         idx=numpy.where(self.extname==i)[0]
         if len(idx) == 0 :
            return []
         return [self.extname[idx],self.extnum[idx],self.type[idx],self.comment[idx]]
      try :
         idx=i
         return [self.extname[idx],self.extnum[idx],self.type[idx],self.comment[idx]]
      except :
         return []
   def __str__(self) :
      for k in range(len(self)) :
         print self[k]
   def keys(self,pubblic=True) :
      import numpy as np
      _P=np.array(['ROWIDX','ROWVAL','COLIDX','COLVAL','XAXIS','YAXIS','ZAXIS','PRIMARY','DESCRIPTION','INMAPS'])
      if pubblic :
         l=[]
         for k in self.extname :
            if (k.strip().upper() == _P).sum()==0 :
               l.append(k.strip())
         return l
      return self.extname

class DescriptionHDU :
   "Handles a Description HDU"
   def __init__(self,hdu) :
      import copy
      import numpy
      try :
         self.name = copy.deepcopy(hdu.data['info'])
         self.text = copy.deepcopy(hdu.data['text'])
         self.comment = copy.deepcopy(hdu.data['comment'])
      except :
         self.name = []
         self.text = []
         self.comment = []
   def __len__(self):
      return len(self.name)
   def __getitem__(self,i) :
      import numpy
      if type(i) == type('') :
         idx=numpy.where(self.name==i)[0]
         if len(idx) == 0 :
            return []
         return [self.name[idx],self.text[idx],self.comment[idx]]
      try :
         idx=i
         return [self.name[idx],self.text[idx],self.comment[idx]]
      except :
         return []
   def __str__(self) :
      for k in range(len(self)) :
         print self[k]
   def keys(self,pubblic=True) :
      return self.name
   def toDict(self) :
      return self.__dict__

class MapGridCube(MapGrid) :
   def __init__(self,*karg,**kopt) : 
      import numpy as np
      import pickle
      import pyfits
      import copy
      import time
      if type(karg[0]) == type('') :
         tic=time.time()
         self.load(karg[0])
         tic=time.time()-tic
         self.info['MapGridCube:ReadoutTime']=tic
         return
      if type(karg[0]) == type(pyfits.HDUList()) :
         MapGrid.__init__(self) 
         self.clean()
         hduIndex='index'
         self.Index=IndexHDU(karg[0]['index'])
         D=DescriptionHDU(karg[0]['description'])
         for k in D.keys() :
            self.info[k]=D[k][1][0]
         self.C=GridAxis(karg[0]['xaxis']).__dict__
         self.R=GridAxis(karg[0]['yaxis']).__dict__
         self.Z=GridAxis(karg[0]['zaxis']).__dict__
         self.shape=(self.Z['n'],self.R['n'],self.C['n'])
         self.M['_row_index']=copy.deepcopy(karg[0]['rowidx'].data)
         self.unit['_row_index']=''
         self.M['_row_values']=copy.deepcopy(karg[0]['rowval'].data)
         self.unit['_row_values']=self.R['unit']
         self.M['_col_index']=copy.deepcopy(karg[0]['colidx'].data)
         self.unit['_col_index']=''
         self.M['_col_values']=copy.deepcopy(karg[0]['colval'].data)
         self.unit['_col_values']=self.C['unit']
         for k in self.Index.keys(pubblic=True) :
            try :
               if karg[0][k].header['xtension'].strip().upper()=='IMAGE' :
                  try :
                     name = karg[0][k].header['name']
                  except :
                     name=k
                  self.M[name]=copy.deepcopy(karg[0][k].data)
                  try :
                     self.unit[name]=karg[0][k].header['unit']
                  except :
                     self.unit[name]=''
            except :
               pass
         return
      if len(karg) == 3 :
         if type(karg[0]) == type(karg[1]) and type(karg[0]) == type(karg[2]) and karg[0].__class__ == GridAxis().__class__ :
            MapGrid.__init__(self,*karg[0:2],**kopt) 
            self.Z=karg[2].__dict__
            self.shape=(self.R['n'],self.C['n'],self.Z['n'])
            self.nslices=self.Z['n']
            return
      self.Index=None
      MapGrid.__init__(self,*karg,**kopt) 
   def clean(self) :
      from numpy import nan,zeros
      MapGrid.clean(self)
      # the z axis splits the planes
      self.Z = self.newaxis()
      self.naxis=3
      self.shape=(0,0,0)
   def refresh(self) :
      "used to refresh interal constants"
      self.shape=(self.Z['n'],self.R['n'],self.C['n'])
   def isflat(self,name) :
      if type(name) == type('') :
         return len(self.M[name].shape) == 2 
      return len(name.shape) == 2 
   def newmap(self,name,unit='',value=None,dtype='float',flat=False) :
     from numpy import nan,zeros
     if flat : 
        self.M[name] = zeros([self.R['n'],self.C['n']],dtype=dtype)
     else :
        self.M[name] = zeros([self.Z['n'],self.R['n'],self.C['n']],dtype=dtype)
     self.unit[name] = unit
     if value == None :
        if type(dtype) == type('') :
           if dtype.strip() !='int' :
              self.M[name] += nan
        else :
           if dtype != type(1) :
              self.M[name] += nan
     else :
        self.M[name] += value
   def transpose(self) :
      import copy
      from numpy import transpose
      M = MapGridCube()
      M.info = copy.deepcopy(self.info)
      M.unit = copy.deepcopy(self.unit)
      M.R = copy.deepcopy(self.C)
      M.C = copy.deepcopy(self.R)
      M.Z = copy.deepcopy(self.Z)
      M.shape=[M.Z['n'],M.R['n'],M.C['n']]
      for k in self.M.keys() :
         if self.isflat(k) : 
            M.M[k]=transpose(self.M[k][iz])
         for iz in range(M.Z['n']) :
            M.M[k][iz]=transpose(self.M[k][iz])
      return M
   def __getitem__(self,*args) :
      print args,len(args)
      if len(args) == 1 :
         try :
            return self.M[args[0]]
         except :
            raise Error("invalid argument")
      elif len(args) == 2 :
         try :
            return self.M[args[0]][args[1]]
         except :
            raise Error("invalid argument")
      elif len(args) == 3 :
         try :
            return self.M[args[0]][args[1]][args[2]]
         except :
            raise Error("invalid argument")
      elif len(args) == 4 :
         try :
            return self.M[args[0]][args[1]][args[2]][args[3]]
         except :
            raise Error("invalid argument")
      else :
         raise Error("invalid argument")
   def __setitem__(self,*args) :
      if len(args) == 2 :
         try :
            self.M[args[0]]=copy.deepcopy(args[1])
         except :
            raise Error("invalid argument")
      elif len(args) == 3 :
         try :
            self.M[args[0]][args[1]]=copy.deepcopy(args[2])
         except :
            raise Error("invalid argument")
      elif len(args) == 4 :
         try :
            self.M[args[0]][args[1]][args[2]]=copy.deepcopy(args[3])
         except :
            raise Error("invalid argument")
      elif len(args) == 5 :
         try :
            self.M[args[0]][args[1]][args[2]][args[3]]=copy.deepcopy(args[4])
         except :
            raise Error("invalid argument")
      else :
         raise Error("invalid argument")
   def set_z_scale(self,*karg) :
      """ set_z_scale(string name)
         set_z_scale(string name,string unit)
         set_z_scale(string name,string unit,array values)
         set_z_scale(string name,string unit,float min, float max, int n)
         set_z_scale(string name,string unit,float min, float max, float delta)
      """ 
      from numpy import nan,zeros,array,round
      self.Z['closed']=False
      self.Z['name']=karg[0]
      if len(karg) < 2 :
         return
      self.Z['unit']=karg[1]
      if len(karg) < 3 :
         return
      self.shape[0]=0
      if type(karg[2]) == type(array([])) :
         self.Z['v'] = 1.*karg[2]
         self.Z['min'] = self.Z['v'].min()
         self.Z['max'] = self.Z['v'].max()
         self.Z['n'] = len(self.Z['v'])
         self.Z['delta'] = self.Z['v'][1]-self.Z['v'][0]
      else :
         if len(karg) < 4 :
            print "error: not enough arguments"
            return
         self.Z['min']=karg[2]
         self.Z['max']=karg[3]
         if type(karg[4]) == type(1) :
            self.Z['n']=karg[4]
            self.Z['delta']=(karg[3]-karg[2])/float(karg[4])
         else :
            self.Z['delta']=karg[4]
            self.Z['n']=int(round((karg[3]-karg[2])/float(karg[4])))
      self.shape[0]=self.Z['n']*1
      if self.shape[0]*self.shape[1] > 0:
         self.clean_matrices()
   def bilinearXY(self,component,x_col,y_row,returnVal=None,returnDelta=False) :
      naxis=self.naxis
      self.naxis = 2
      f=MapGrid.bilinearXY(self,component,x_col,y_row,returnVal=returnVal,returnDelta=returnDelta) 
      self.naxis = naxis
      return f
   def profile(self,name,x1_col,y1_col,x2_col,y2_col,nsmp=100) :
      "returns a profile along a line"
      #computes line coefficients
      import numpy as np
      l=np.arange(nsmp)/float(nsmp-1)
      x_col=(x2_col-x1_col)*l+x1_col
      y_col=(y2_col-y1_col)*l+y1_col
      f=self.bilinearXY(name,x_col,y_col)
      return {'l':l,'x':x_col,'y':y_col,'p':f}
   
if __name__=='__main__' :
   import numpy as np
   
   #test creation empty map
   print "test creation empty map"
   GMEmpty = MapGrid(mapname='GMEmpty')
   
   #test creation map with shape [100,200]
   GM12=MapGrid(Rows=100,Cols=200,mapname='GM12')

   #test creation map with GridAxis
   GMD12=MapGrid(Cols=GridAxis('x','deg',np.arange(0.,360.,1.),periodic=True),Rows=GridAxis('y','deg',np.arange(-18.,19.,1.)),mapname='GMD12')

   #test creation map with GridAxis
   GMA12=MapGrid(Cols=np.arange(-10,11,1.),Rows=np.arange(22,-1,-1),mapname='GMA12')

   #test creation map with model
   GMM12=MapGrid(model=GMA12['_row_values']**2+GMA12['_col_values']**2)
   
   stop
   
   GM=MapGrid(GridAxis('x','deg',arange(0.,360.,1.,period=True)),GridAxis('y','deg',arange(-18.,19.,1.)))
   GM.M['sinCol']=np.sin(np.deg2rad(GM['_col_values'])) 

   print "Test X_col interpolation"
   x_col=arange(0.,360.1,0.1)
   Test1={}
   Test1['interpolated']=GM.bilinearXY('sinCol',x_col,0.*x_col)
   Test1['calculated']=np.sin(np.deg2rad(x_col))
   Test1['simulated interpolation']=(np.sin(np.deg2rad(np.floor(x_col)+1))-np.sin(np.deg2rad(np.floor(x_col))))*(x_col-np.floor(x_col))/1.+np.sin(np.deg2rad(np.floor(x_col)))
   Test1['interpolated-calculated']=Test1['interpolated']-Test1['calculated']
   Test1['simulated interpolation-calculated']=Test1['simulated interpolation']-Test1['calculated']
   Test1['simulated interpolation-interpolated']=Test1['simulated interpolation']-Test1['interpolated']
   
   for k in ['interpolated-calculated', 'simulated interpolation-calculated', 'simulated interpolation-interpolated'] :
      print "abs(%20s) = %e,%e"%(k,abs(Test1[k]).min(),abs(Test1[k]).max())
   print

   print "Test X_col and Y_col interpolation"
   y_row=0.1*arange(361,dtype='int')+GM.R['min']
   x_col2=y_row*0.+90.
   GM.M['AsinCol']=np.sin(np.deg2rad(GM['_col_values']))*GM['_row_values']
   Test2={}
   Test2['interpolated']=GM.bilinearXY('AsinCol',x_col2,y_row)
   Test2['calculated']=np.sin(np.deg2rad(x_col2))*y_row
   #Test2['simulated interpolation']=((np.floor(x_col2)+1)*np.sin(np.deg2rad(np.floor(x_col2)+1))-np.floor(x_col2)*np.sin(np.deg2rad(np.floor(x_col2))))*(x_col2-np.floor(x_col2))/1.+np.floor(x_col2)*np.sin(np.deg2rad(np.floor(x_col2)))
   Test2['interpolated-calculated']=Test2['interpolated']-Test2['calculated']
   #Test2['simulated interpolation-calculated']=Test2['simulated interpolation']-Test2['calculated']
   #Test2['simulated interpolation-interpolated']=Test2['simulated interpolation']-Test2['interpolated']
   #for k in ['interpolated-calculated', 'simulated interpolation-calculated', 'simulated interpolation-interpolated'] :
   for k in ['interpolated-calculated' ] :
      print "abs(%20s) = %e,%e"%(k,abs(Test2[k]).min(),abs(Test2[k]).max())
   
   
