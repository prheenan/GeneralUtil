# force floating point division. Can still use integer with //
from __future__ import division
# other good compatibility recquirements for python3
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
# This file is used for importing the common utilities classes.
import numpy as np
import matplotlib.pyplot as plt
import sys,copy,matplotlib

from GeneralUtil.python.PlotUtilities import *
from GeneralUtil.python.Plot import Annotations

default_font_dict = dict(fontsize=g_font_label,
                         fontweight='bold',
                         family="sans",
                         color='k',
                         horizontalalignment='center',
                         verticalalignment='lower',
                         bbox=dict(color='w',alpha=0))
                         
def_font_kwargs_y = copy.deepcopy(default_font_dict)
def_font_kwargs_y['horizontalalignment'] = 'right'
def_font_kwargs_y['verticalalignment'] = 'center'         

def font_kwargs_modified(x_kwargs=dict(),y_kwargs=dict()):
    """
    Returns the font kwargs 
    
    Args:
        <x/y>_kwargs: applied to the x and y font; overwrites them
    Returns:
        default_font_dict and def_font_kwargs, except overwritten by 
        <x/y>_kwargs. So, tuple of x and y 
    """
    to_ret_x = copy.deepcopy(default_font_dict)
    to_ret_y = copy.deepcopy(def_font_kwargs_y)
    for k,v in x_kwargs.items():
        to_ret_x[k] = v
    for k,v in y_kwargs.items():
        to_ret_y[k] = v
    return to_ret_x,to_ret_y

def round_to_n_sig_figs(x,n=1):
    """
    Rounds 'x' to n significant figures

    Args:
         x: what to round
         n: how many sig figs (e.g. n=1 means 51 --> 50, etc)
    Returns: rounded number 
    """
    return round(x, (n-1)-int(np.floor(np.log10(abs(x)))))


def _get_tick_locator_fixed(offset,width,lim=plt.xlim()):
    """
    given a (data-units) offset and width, returns tick so that
    (1) offset is a tick
    (2) each offset +/- (n * width) for n an integer within lim is a tick.

    Useful for matching ticks to a scale bar 

    Args:
         offset: point which should have a tick on it
         width: data units, length between ticks
         lim: to determine where the ticks should be 
    Returns:
         FixedLocator parameter
    """
    xmin,xmax = lim
    # determine how many widths to go before and after
    n_widths_before = int(np.ceil(abs((offset-xmin)/width)))
    width_before = n_widths_before * width
    n_widths_after = int(np.ceil(abs((xmax-offset)/width)))
    width_after = n_widths_after * width
    ticks_after = np.arange(start=offset,stop=offset+(width_after+width),
                            step=width)
    ticks_before = np.arange(start=offset,stop=offset-(width_before+width),
                             step=-width)
    ticks = list(ticks_before) + list(ticks_after)
    locator = FixedLocator(locs=ticks, nbins=None)
    return locator
    
def _scale_bar_and_ticks(ax,axis,lim,is_x=True,**kwargs):
    """
    convenience wrapper for create a scale bar with convenient ticks 
    
    Args:
        ax: like plt.gca()
        axis: something we can use 'set_major.minor_locator' on
        lim: the limits of the axis
    Returns:
        nothing
    """
    box,x,y = _scale_bar(ax=ax,**kwargs)
    if (is_x):       
        tick_spacing = abs(np.diff(x))
        offset = min(x)
    else:
        tick_spacing = abs(np.diff(y))
        offset = min(y)
    locator_x = _get_tick_locator_fixed(offset=offset,width=tick_spacing,
                                        lim=lim)
    locator_minor_x = _get_tick_locator_fixed(offset=offset+tick_spacing/2,
                                              width=tick_spacing,lim=lim)
    axis.set_major_locator(locator_x)
    axis.set_minor_locator(locator_minor_x) 
    """
    make sure the ticks are ontop of the data 
    See (e.g.):
stackoverflow.com/questions/19677963/matplotlib-keep-grid-lines-behind-the-graph-but-the-y-and-x-axis-above
    """
    ax.set_axisbelow(False)
    
def _y_scale_bar_and_ticks(ax=plt.gca(),**kwargs):
    """
    Convenience wrapper to make a scale bar and ticks
    
    Args:
        kwargs: passed to _scale_bar_and_ticks
    Returns:
        nothing
    """    
    _scale_bar_and_ticks(ax,ax.yaxis,ax.get_ylim(),is_x=False,**kwargs)   

def _x_scale_bar_and_ticks(ax=plt.gca(),**kwargs):
    """
    Convenience wrapper to make a scale bar and ticks
    
    Args:
        kwargs: passed to _scale_bar_and_ticks
    Returns:
        nothing
    """
    _scale_bar_and_ticks(ax,ax.xaxis,ax.get_xlim(),**kwargs)   
    
def rel_to_abs(ax,x,is_x):
    """
    Returns: x (in data coords) transformed to the relative [0,1] coordinates
             of the x/y axis of ax 
    """
    if (is_x):
        lim = ax.get_xlim()
    else:
        lim = ax.get_ylim()
    absolute = lim[0] + (lim[1] - lim[0]) * x
    return absolute
    
    
def offsets_and_ranges(width,height,offset_x,offset_y):
    """
    Returns the coordinates for the text and scale bar, given the parameters
    
    Args;
        width/height: of the bar
        offset_x,offset_y: of the text
    Returns: 
        tuple of <xy for text, xy endpoints for line>
    """
    bar_offset_x = width/2
    bar_offset_y = height/2 
    text_offset_x = offset_x  
    text_offset_y = offset_y
    xy_text = [text_offset_x,text_offset_y]   
    xy_line =  [ [text_offset_x - bar_offset_x,text_offset_y - bar_offset_y],
                [text_offset_x + bar_offset_x,text_offset_y + bar_offset_y]]
    return xy_text,xy_line                
    
def unit_format(val,unit,fmt="{:.0f}",value_function = lambda x:x):
    """
    Returns: the way we want to format the scale bar text; <val><space><unit>
    """
    val = value_function(val)
    # make sure the formatted string matches the actual length
    formatted = float(fmt.format(val))
    err_msg = "Formatted scalebar ({:.2g}) not close to true length ({:.2f})".\
          format(formatted,val)
    np.testing.assert_allclose(formatted,val,atol=0,err_msg=err_msg)
    # POST: the formatted value is accurate.
    return (fmt + " {:s}").format(val,unit) 
    
def x_scale_bar_and_ticks(unit,width,offset_x,offset_y,ax=plt.gca(),
                          unit_kwargs=dict(fmt="{:.0f}"),**kwargs):
    """
    See: y_scale_bar_and_ticks, except makes an x scale bar with a specified
    width
    """                                       
    xy_text,xy_line = offsets_and_ranges(width=width,height=0,
                                         offset_x=offset_x,offset_y=offset_y)
    text = unit_format(width,unit,**unit_kwargs)             
    return _x_scale_bar_and_ticks(ax=ax,xy_text=xy_text,xy_line=xy_line,
                                  text=text,**kwargs)
                                  
def x_and_y_to_abs(x_rel,y_rel,ax):
    """
    converts x and y to absolute units (asusming they are in [0,1] axes units)
    
    Args:
        <x/y>_rel: see rel_to_abs
        ax: which axis they are relative on
    Returns;
        the asbolute values of the x and y units...
    """
    offset_x = rel_to_abs(ax=ax,x=x_rel,is_x=True)
    offset_y = rel_to_abs(ax=ax,x=y_rel,is_x=False)
    return offset_x,offset_y
                                  
def x_scale_bar_and_ticks_relative(unit,width,offset_x,offset_y,
                                   ax=plt.gca(),**kw):
    """
    See: x_scale_bar_and_ticks, except offset_x and offset_y are in [0,1] 
    relative graph units 
    """
    offset_x,offset_y = x_and_y_to_abs(offset_x,offset_y,ax)
    return x_scale_bar_and_ticks(unit,width,offset_x,offset_y,ax=ax,**kw)  

def y_scale_bar_and_ticks_relative(unit,height,offset_x,offset_y,
                                   ax=plt.gca(),font_kwargs=def_font_kwargs_y,
                                   **kw):
    """
    See: y_scale_bar_and_ticks, except offset_x and offset_y are in [0,1] 
    relative graph units 
    """                                   
    offset_x,offset_y = x_and_y_to_abs(offset_x,offset_y,ax)
    return y_scale_bar_and_ticks(unit,height,offset_x,offset_y,ax=ax,
                                 font_kwargs=font_kwargs,**kw)                                    
 
                                  
def y_scale_bar_and_ticks(unit,height,offset_x,offset_y,ax=plt.gca(),
                          unit_kwargs=dict(),**kwargs):
    """
    ease-of-use function for making a y scale bar. figures out the units and 
    offsets
    
    Args;
        unit: of height
        height: of the scale bar 
        offset_<x/y>: where the text box should be, in absolute units
        **kwargs: see _y_scale_bar_and_ticks
    Returns:
        tuple of <annnotation, x coordinates of line, y coords of line>
    """                          
    xy_text,xy_line = offsets_and_ranges(width=0,height=height,
                                        offset_x=offset_x,offset_y=offset_y)
    text = unit_format(height,unit,**unit_kwargs)
    return _y_scale_bar_and_ticks(ax=ax,xy_text=xy_text,xy_line=xy_line,
                                  text=text,**kwargs)       
                                  

def crossed_x_and_y(offset_x,offset_y,x_kwargs,y_kwargs,ax=plt.gca(),
                    font_kwargs_y=None):
    """
    ease of use for making a 'crossed' x and y scale bar. 
    
    Args;
        offset_<x/y>: see _scale_bar
        <x_/y_>kwargs: passed to x_scale_bar_and_ticks,
        font_kwargs_y: option arguments for font_kwargs_y
    Returns:
        tuple of <annnotation, x coordinates of line, y coords of line>
    """
    assert ("height" in y_kwargs.keys()) , "Height not specified"
    assert ("width" in x_kwargs.keys()) , "Width not specified"
    width = x_kwargs['width']
    height = y_kwargs['height']
    if ('font_kwargs' not in x_kwargs):
        x_kwargs['font_kwargs'] = copy.deepcopy(default_font_dict)
    x_kwargs['font_kwargs']['verticalalignment']='top'
    x_scale_bar_and_ticks(offset_x=offset_x,offset_y=offset_y,ax=ax,**x_kwargs) 
    # make the y scale bar...
    if ('font_kwargs' not in y_kwargs):
        font_kw = copy.deepcopy(def_font_kwargs_y)
        y_kwargs['font_kwargs'] = font_kw        
    y_kwargs['font_kwargs']['rotation'] = 90
    y_scale_bar_and_ticks(offset_x=offset_x-width/2,offset_y=offset_y+height/2,
                          ax=ax,**y_kwargs)         


def crossed_x_and_y_relative(offset_x,offset_y,ax=plt.gca(),**kwargs):
    """
    See: crossed_x_and_y, except offsets are in axis units 
    """
    offset_x,offset_y = x_and_y_to_abs(offset_x,offset_y,ax=ax)
    return crossed_x_and_y(offset_x,offset_y,ax=ax,**kwargs)                          

    
def _scale_bar(text,xy_text,xy_line,ax=plt.gca(),
               line_kwargs=dict(linewidth=1.5,color='k'),
               font_kwargs=default_font_dict,
               fudge_text_pct=dict(x=0,y=0)):
    """
    Creates a scale bar using the specified, absolute x and y
    
    Args;
        text: to display
        xy_text: where the text should be
        xy_line: where the scalebar should be
        ax: the axis to use
        <line/font>_kwargs: passed to plot and annotate, respectively
        fudge_text_pct: as a percentage of the scale bar, how much to shift the 
        text. Useful for preventing overlap. 
    
    Returns:
        tuple of <annnotation, x coordinates of line, y coords of line>
    """
    x_draw = np.array([x[0] for x in xy_line])
    y_draw = np.array([x[1] for x in xy_line])    
    # shift the text, if need be.
    f_diff = lambda x: np.max(np.abs(np.diff(x_draw)))    
    x_range = f_diff(x_draw)
    y_range = f_diff(y_draw)
    x_text = xy_text[0]
    y_text = xy_text[1]    
    x_text += x_range * fudge_text_pct['x']
    y_text += y_range * fudge_text_pct['y']   
    # POST: shifted     
    xy_text = [x_text,y_text]
    t = Annotations._annotate(ax=ax,s=text,xy=xy_text,**font_kwargs)
    ax.plot(x_draw,y_draw,**line_kwargs)
    return t,x_draw,y_draw
