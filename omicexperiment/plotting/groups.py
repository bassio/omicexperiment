import random
from math import isnan
from collections import OrderedDict, namedtuple
from lxml import etree
from pandas import Series, concat
from omicexperiment.plotting.plot_pygal import return_plot, return_plot_tree


PositionData = namedtuple("PositionData", 'x,y,x1,x2')

def return_y_position_group_label(tree):
  path0 = tree.xpath('//path[@class="guide line"]')[0]
  #label0 = path0.getnext()
  #y = ((float(rect0.attrib['y']) + float(rect0.attrib['height'])) \
  #          + float(label0.attrib['y']) 
  #      ) / 2
  #axis_x = tree.xpath('//g[@class="axis x"]')[0]
  y = float(path0.attrib['d'].split(" ")[2].split("v")[1])
  return y

def return_rects_first_and_last_x(rects):
  rect0 = rects[0]
  last_rect = rects[-1::][0]
  x_left = float(rect0.attrib['x'])
  x_right = float(last_rect.attrib['x']) + float(last_rect.attrib['width'])
  mid_x = (x_left + x_right) / 2 
  return (x_left, x_right)


def return_rects_middle_x(rects):
  xs = return_rects_first_and_last_x(rects)
  x_left = xs[0]
  x_right = xs[1]
  mid_x = (x_left + x_right) / 2 
  return (mid_x)


def return_rects_for_groups(tree, group_col):
  rects = tree.xpath('//rect[@class="rect reactive tooltip-trigger"]')
  index_values = group_col.value_counts().index.sort_values()
  
  rects_dict = OrderedDict()
  for index_value in index_values:
    rects_dict[index_value] = []
  
  #check for nan
  if len(group_col[group_col.isnull()]) > 0:
    rects_dict['nan'] = []
  
  for i, rect in enumerate(rects):
    rect_val = rect.getnext().getnext().getnext().getnext().text
    key = val = group_col[rect_val]
    try:
      rects_dict[key].append(rect)
    except:
      if isnan(key):
        rects_dict['nan'].append(rect)
        
  return rects_dict

def return_xlabels_for_groups(tree, group_col):
  paths = tree.xpath('//path[@class="guide line"]')
  
  labels = []
  
  for path in paths:
    labels.append(path.getnext())
    
  index_values = group_col.value_counts().index.sort_values()
  
  labels_dict = OrderedDict()
  for index_value in index_values:
    labels_dict[index_value] = []
  
  #check for nan
  if len(group_col[group_col.isnull()]) > 0:
    labels_dict['nan'] = []
  
  for i, lbl in enumerate(labels):
    lbl_val = lbl.text
    key = val = group_col[lbl_val]
    try:
      labels_dict[key].append(lbl)
    except:
      if isnan(key):
        labels_dict['nan'].append(lbl)
        
  return labels_dict


def group_label_positions(tree, group_col, pad):
  rects_dict = return_rects_for_groups(tree, group_col)
  
  pos_dict = OrderedDict()
  
  y = return_y_position_group_label(tree)
  
  try:
    rects_dict_iteritems = rects_dict.iteritems
  except AttributeError: #python3
    rects_dict_iteritems = rects_dict.items

  
  for i, kv in enumerate(rects_dict_iteritems()):
    k,grp_rects = kv
    x1,x2 = return_rects_first_and_last_x(grp_rects)
    mid_x = (x1 + x2) / 2
    if pad:
      x1,x2,mid_x = x1+(pad*i), x2+(pad*i),mid_x+(pad*i)
    pos_dict[k] = PositionData(x=mid_x,x1=x1,x2=x2,y=y)
  
  return pos_dict


def add_group_labels(tree, group_col, pad):
  axis_x = tree.xpath('//g[@class="axis x"]')[0]
  lbls_dict = group_label_positions(tree, group_col, pad)
  rand_grey = 200
  
  try:
    lbls_dict_iteritems = lbls_dict.iteritems
  except AttributeError: #python3
    lbls_dict_iteritems = lbls_dict.items

  
  for lbl, pos in lbls_dict_iteritems():
    
    l = etree.Element("line", x1=str(pos.x1), x2=str(pos.x2), y1=str(pos.y), y2=str(pos.y), style="stroke:rgb({x}, {x}, {x});stroke-width:1".format(x=str(rand_grey)))
    v1 = etree.Element("line", x1=str(pos.x1), x2=str(pos.x1), y1=str(pos.y-3), y2=str(pos.y+3), style="stroke:rgb({x}, {x}, {x});stroke-width:1".format(x=str(rand_grey)))
    v2 = etree.Element("line", x1=str(pos.x2), x2=str(pos.x2), y1=str(pos.y-3), y2=str(pos.y+3), style="stroke:rgb({x}, {x}, {x});stroke-width:1".format(x=str(rand_grey)))
    
    lbl_length = pos.x2 - pos.x1
    if lbl_length < 35 and len(str(lbl)) > 5:
        t_attr = {'lengthAdjust':"spacingAndGlyphs", 'textLength':str(lbl_length)}
    else:
        t_attr = {}
    t = etree.Element("text", x=str(pos[0]), y=str(pos[1]), **t_attr)
    t.text = str(lbl)
    
    axis_x.append(l)
    axis_x.append(v1)
    axis_x.append(v2)
    axis_x.append(t)
    rand_grey = random.randint(150,200)



def group_plot_tree(dataframe, mapping_group_col, include_nan=False, pad=10):
  group_col_name = mapping_group_col.name
  sorted_group_col = mapping_group_col.sort_values()
  vals = list(sorted_group_col.value_counts().index)
  
  if include_nan:
    vals.append('nan')
  else:
    sorted_group_col = sorted_group_col[sorted_group_col.notnull()]
  
  sorted_df = dataframe.reindex(columns=sorted_group_col.index)
  
  plot = return_plot(sorted_df)
  tree = return_plot_tree(plot)
  
  if pad != False:
    rects_dict = return_rects_for_groups(tree, sorted_group_col)
    for i, key in enumerate(rects_dict):
      for rect in rects_dict[key]:
        rect.attrib['transform'] = 'translate({},0)'.format(str(pad*i))
    
    lables_dict = return_xlabels_for_groups(tree, sorted_group_col)
    for i, key in enumerate(lables_dict):
      for lbl in lables_dict[key]:
        #the parent of the label here is the <g class='guides'> tag
        lbl.getparent().attrib['transform'] = 'translate({},0)'.format(str(pad*i))
    
  add_group_labels(tree, sorted_group_col, pad)
  
  return plot, tree

  