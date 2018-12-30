from bokeh.plotting import figure
from bokeh.models import Legend, LegendItem, HoverTool, ColumnDataSource
from bokeh.core.properties import value


def plot_interactive(dataframe):
    observations = list(dataframe.index)
    samples_or_groups = list(dataframe.columns)
    
    
    transposed_df = dataframe.T
    
    if not transposed_df.index.name:
        x_label = 'index'
    else:
        x_label = transposed_df.index.name
        
    source=ColumnDataSource(transposed_df)
    
    from bokeh.plotting import figure
    p = figure(x_range=samples_or_groups,
               y_range=(0,transposed_df.sum(axis=1).max())
              )
    
    from bokeh.palettes import Category20
    import itertools
    palette = Category20
    max_color_palette = max(list(palette.keys()))
    
    if len(observations) <= max_color_palette \
    and len(observations) in palette:
            colours = palette[len(observations)]
    
    else:
        colours = []
        for i, c in enumerate(itertools.cycle(palette[max_color_palette])):
            colours.append(c)
            if i + 1 == len(observations): break
            
                    
    vbars = p.vbar_stack(observations,
                         x=x_label,
                         color=colours,
                         legend=None,
                         width=0.8,
                         source=source)

    p.ygrid.grid_line_color = None
    legend_items = [LegendItem(label=x, renderers=[renderer]) 
                    for x, renderer in zip(transposed_df.columns, vbars)]
    legend = Legend(items=legend_items, location=(10,200))
    p.add_layout(legend, 'left')
    p.legend.location = 'top_right'

    for renderer in vbars:
        r_name = renderer.name
        p.add_tools(HoverTool(
        tooltips=[
            ( x_label, '@{' + x_label + '}' ),
            ( 'taxon', '$name: @{' + r_name + '}' ), # use @{ } for field names with spaces
        ],

        formatters={
            x_label: 'printf',
            'taxon': 'printf'
        },
        toggleable=False,
        renderers=[renderer]))

    p.toolbar.logo = None
    p.toolbar_location = "above"
    
    p.xaxis.major_label_orientation = "vertical"
    
    #set fig width
    min_width = 600
    width_as_per_number_of_columns = len(samples_or_groups) * 12
    
    if width_as_per_number_of_columns < 500:
        p.width = min_width
    else:
        p.width = width_as_per_number_of_columns
    
    return p
 
