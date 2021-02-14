"""
Utilities for reading data from GamessUS .log files.
* GamessSurf object loads data from ``RUNTYPE=SURFACE`` files.

Jonathan Gutow <gutow@uwosh.edu>
January 2021
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import k3d as k3d

class GamessSurf():
    """
    Loads a surface from a GamessUS ``RUNTYPE=SURFACE`` log file into a GamessSurf object.
    
    ``.plot()`` will automatically generate a 2-D or 3-D plot as appropriate for the surface.
    The 3-D plots use k3d so only work in Jupyter notebooks, but they are live.
    
    """
    
    def __init__(self,filepath):
        """
        Parameters
        ==========
        filepath: str containing the full path to the GamessUS .out (.log) file created by
        a Surface calculation.
        
        Returns
        =======
        Object: object of type GamessSurf.
    
        """
        self.filepath = filepath
        if self.issurfcalc():
            self.points = self.loadGAMESSsurf()
            self.coor1, self.coor2 = self._getcoordef()
        else:
            raise TypeError('File is not the output of a GamessUS surface calculation.')
    
    def loadGAMESSsurf(self):
        file = open(self.filepath,'r')
        notEOF = True
        points = []
        count = 0
        print('Reading file ',end='')
        while (notEOF):
            line = file.readline()
            if line == '':
                notEOF = False
            if line.find('SURFACE MAPPING GEOMETRY')>-1:
                line = file.readline()
                line = line.strip()
                ineq1 = line.find('=')
                ineq2 = line.rfind('=')
                coor1 = float(line[ineq1+1:ineq1+7])
                coor2 = float(line[ineq2+1:ineq2+7])
                line = file.readline().strip()
                parts = line.rsplit()
                energy = float(parts[len(parts)-1])
                points.append([coor1,coor2,energy])
                count+=1
                if count%100 == 0:
                    print('.',end='')
        file.close()
        return points

    def issurfcalc(self):
        """
        Returns
        =======
        Boolean: True if the calculation type should return a surface.
        """
        file = open(self.filepath,'r')
        linecount = 0
        while linecount < 700:
            line = file.readline()
            if line == '':
                #end of file
                linecount = 701
            if line.find('RUNTYP=SURFACE')>-1:
                file.close()
                return True
            linecount += 1
        file.close()   
        return False
    
    def _getcoordef(self):
        """
        Returns
        =======
        one,two: list of strings to label coordinates
        """
        file = open(self.filepath,'r')
        one =''
        two =''
        atomsv1 = []
        atomsv2 = []
        atomnums = []
        atomnames = []
        line = file.readline()
        CONT = True
        while (line !='') and CONT:
            if line.find('$SURF')>-1:
                pieces = line.split()
                for k in pieces:
                    if k.find('IVEC1')>-1:
                        ats = (k.split("="))[1].split(",")
                        atomsv1.append(int(ats[0]))
                        atomsv1.append(int(ats[1]))
                    if k.find('IVEC2')  >-1:
                        ats = (k.split("="))[1].split(",")
                        atomsv2.append(int(ats[0]))
                        atomsv2.append(int(ats[1]))
            if line.find('$DATA')>-1:
                atomnums.append(atomsv1[0])
                atomnames.append('')
                atomnums.append(atomsv1[1])
                atomnames.append('')
                if len(atomsv2)>0:
                    if atomsv2[0] not in atomnums:
                        atomnums.append(atomsv2[0])
                        atomnames.append('')
                    if atomsv2[1] not in atomnums:
                        atomnums.append(atomsv2[1])
                        atomnames.append('')
                line = file.readline()
                atomno = 0
                while line.find('$END')<0:
                    pieces = line.split()
                    nfloat = 0
                    if len(pieces) == 6:
                        for i in range(2, 6):
                            try:
                                float(pieces[i])
                                nfloat+=1
                            except:
                                pass
                    if nfloat == 4:
                        atomno += 1
                        atomstr = (pieces[1].split(">"))[1]
                    for i in range(len(atomnums)):
                        if atomno == atomnums[i]:
                            atomnames[i]=atomstr
                    line = file.readline()
                    print('.',end='')
                CONT = False
            line=file.readline()
        file.close()
        atomnodict = dict(zip(atomnums,atomnames))
        one = '\\Delta R_{'
        one += atomnodict[atomsv1[0]]+'_{('+str(atomsv1[0])+')}'
        one += atomnodict[atomsv1[1]]+'_{('+str(atomsv1[1])+')}}'
        if len(atomsv2)==2:
            two = '\\Delta R_{'
            two += atomnodict[atomsv2[0]]+'_{('+str(atomsv2[0])+')}'
            two += atomnodict[atomsv2[1]]+'_{('+str(atomsv2[1])+')}}'      
        return one, two   
    
    def asmeshgrid(self):
        """
        Takes an ordered lattice of 3-d points and extracts the 2-D mesh grid
        from the first two coordinates of the points and a list of heights from
        the last coordinate.
        
        Return
        ======
        x,y,z: lists of lists of float a mesh grid for x, y and z.
        """
        valmax = [0,0]
        valmin = [0,0]
        xvals = [k[0] for k in self.points]
        yvals = [k[1] for k in self.points]
        valmax[0] = np.max(xvals)
        valmin[0] = np.min(xvals)
        valmax[1] = np.max(yvals)
        valmin[1] = np.min(yvals)
        #print(valmin,valmax)
        x = []
        y = []
        z = []
        # check which is indexed first
        # assume a rectangular grid
        indexed_first = None
        if self.points[0][0]!=self.points[1][0]:
            indexed_first = 0
            indexed_second = 1
        else:
            indexed_first = 1
            indexed_second = 0
        tmpdim = 1
        up = self.points[0][indexed_first]<self.points[1][indexed_first]
        val = self.points[0][indexed_first]
        if up:
            while val != valmax[indexed_first]:
                tmpdim+=1
                val=self.points[tmpdim-1][indexed_first]
        else:
            while val != valmin[indexed_first]:
                tmpdim+=1
                val=self.points[tmpdim-1][indexed_first]
        dim = [0,0]
        dim[indexed_first] = tmpdim
        dim[indexed_second] = int(len(self.points)/tmpdim)
        tempx = []
        tempy = []
        tempz = []
        for i in range(len(self.points)):
            tempx.append(self.points[i][0])
            tempy.append(self.points[i][1])
            tempz.append(self.points[i][2])
            if (i+1)%dim[1] == 0:
                x.append(tempx)
                y.append(tempy)
                z.append(tempz)
                tempx =[]
                tempy =[]
                tempz =[]
        if indexed_first == 1:
            # Transpose to get ordering
            x = np.array(np.transpose(x),np.float32)
            y = np.array(np.transpose(y),np.float32)
            z = np.array(np.transpose(z),np.float32)
        return x, y, z
    
    def aspandas(self):
        x = []
        y = []
        z = []
        for k in self.points:
            x.append(k[0])
            y.append(k[1])
            z.append(k[2])
        return pd.DataFrame({self.coor1:x, self.coor2:y, 'Energy (au)':z})
    
    def mins(self):
        """
        Returns a list of points where z is at a minimum
        """
        mins = []
        ref = self.points[0][2]
        for k in self.points:
            if k[2]<ref:
                ref = k[2]
        for k in self.points:
            if k[2] == ref:
                mins.append(k)
        return mins        
                    
    def plot(self):
        """
        Produces either a surface plot (2-D PES) or a curve plot (1-D PES)
        """
        if (self.coor1 == '') or (self.coor2 == ''):
            return self._plot2D()
        else:
            return self._plot3D()
        pass
    
    def _plot2D(self):
        xindex = None
        if self.coor1 == '':
            xindex = 1
        else:
            xindex = 0
        plotdf = self.aspandas()
        xstr = '$'+plotdf.columns[xindex]+'\,(\AA)$'
        return plotdf.plot(x=plotdf.columns[xindex],y=plotdf.columns[2],
                           xlabel=xstr, ylabel='Energy (au)')
        
    def ask3dsurf(self):
        """
        Return
        ======
        surface: a k3d surface object.
        """
        mx,my,mz = self.asmeshgrid()
        surface = k3d.surface(mz,xmin=np.min(mx), xmax=np.max(mx), ymin=np.min(my), ymax=np.max(my))
        surface.color_map=k3d.colormaps.basic_color_maps.Rainbow
        surface.attribute=mz
        surface.color_range = [np.min(mz), np.max(mz)]
        return surface
    
    def ask3dplot(self):
        """
        Return
        ======
        plot: a k3d plot object containing the surface
        """
        plot = k3d.plot(axes=[self.coor1+' (Angs)',self.coor2+' (Angs)','Energy (au)'])
        surface = self.ask3dsurf()
        plot+=surface
        return plot
    
    def _plot3D(self):
        """
        Return
        ======
        live plot: a k3d live plot
        """
        plot = self.ask3dplot()
        return plot.display()
