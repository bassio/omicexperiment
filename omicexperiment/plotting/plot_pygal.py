import sys
import codecs
from io import StringIO
from lxml import etree
import pygal
from pygal.style import DefaultStyle

default_config = pygal.Config()
default_config.x_label_rotation = 90
default_config.height = 500
default_config.top_margin = 5
default_config.legend_box_size = 2
default_config.show_y_guides = False

HTML_PYGAL = u"""
<!DOCTYPE html>
<html>
  <head>
  <script type="text/javascript" src="http://kozea.github.io/pygal.js/2.0.x/pygal-tooltips.min.js"></script>
    <!-- ... -->
  </head>
  <body>
    <div>
      {render}
    </div>
    <div>
      {table}
    </div>
  </body>
</html>
"""

HTML_PYGAL_NOJS = u"""
<!DOCTYPE html>
<html>
  <head>
    <!-- ... -->
  </head>
  <body>
    <div>
      {render}
    </div>
    <div>
      {table}
    </div>
  </body>
</html>
"""

custom_css = u"""
  {{ id }} rect.background,
  {{ id }} .plot > .background {
    fill: #F9F9F9;
  }
  {{ id }} text {
  }
  {{ id }}.legends .legend text {
  }
  {{ id }}.axis {
  }
  {{ id }}.axis text {
    font-size: 7px;
  }
  {{ id }}.axis.y text {
  }
  {{ id }}#tooltip text {
  }
  {{ id }}.dot {
  }
  {{ id }}.color-0 {
  }
  {{ id }} text {
  }
  
"""

default_config.css.append('inline:' + custom_css)

default_style = DefaultStyle()
default_style.label_font_size = 7
default_style.plot_background='#F9F9F9'
default_style.background='#F9F9F9'
default_style.legend_font_size = 7
default_config.style = default_style


def get_rect_attributes(rect):
  attrib_dict = {s.attrib['class']: s.text for s in rect.itersiblings()}
  prevrect = rect.getprevious()
  if prevrect.attrib['class'] == 'label':
      attrib_dict['label'] = prevrect.text    
  return attrib_dict

def get_tooltip_label(attrib_dict):
  LF = "\n"
  label = "" + attrib_dict['label'] + LF + \
          "Sample: " + attrib_dict['x_label'] + LF + \
          attrib_dict['value']
  return label


def return_plot(dataframe, config=default_config):
  x_labels = [str(c) for c in dataframe.columns]

  chart = pygal.StackedBar(config)
  chart.title = 'Microbiome'
  chart.x_labels = x_labels
  
  for otu in dataframe.index:
    vals = []
    for v in dataframe.loc[otu]:
      vals.append({'value': v, 'label': otu})
    chart.add(otu, vals)
  
  return chart


def return_plot_tree(plot):
  tree = plot.render_tree()
  rects = tree.xpath('//rect[@class="rect reactive tooltip-trigger"]')
  for r in rects:
    lbl = get_tooltip_label(get_rect_attributes(r))
    txt_element = etree.Element('title')
    txt_element.text = lbl
    r.append(txt_element)

  tree_root = tree.getroottree()
  
  return tree_root


def plot_table(dataframe, outputfile=None, config=default_config):
  
  dataframe = dataframe.rename(columns={c: str(c) for c in dataframe.columns})
  x_labels = dataframe.columns
  
  plot = return_plot(dataframe, config)
  plot_tree = return_plot_tree(plot)
  
  #s = StringIO()
  serialize_fn = str if sys.version_info[0] >= 3 else unicode
  plot_string = etree.tostring(plot_tree, encoding=serialize_fn, pretty_print=True)
  #plot_string = s.getvalue()
  #s.close()
  
  if outputfile is not None:
    output = HTML_PYGAL_NOJS.format(render=plot_string, table=plot.render_table(style=True, transpose=True))
    with codecs.open(outputfile, 'w','utf-8') as f:
      f.write(output)
    
  else:
    output = HTML_PYGAL_NOJS.format(render=plot_string, table=u"")

  return output

def plot_to_file(plot, plot_tree, outputfile):
  serialize_fn = str if sys.version_info[0] >= 3 else unicode
  plot_string = etree.tostring(plot_tree, encoding=serialize_fn, pretty_print=True)
  output = HTML_PYGAL_NOJS.format(render=plot_string, table=plot.render_table(style=True, transpose=True))
  with codecs.open(outputfile, 'w','utf-8') as f:
    f.write(output)

  return output

    