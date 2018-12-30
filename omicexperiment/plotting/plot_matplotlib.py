import numpy as np
import pandas as pd
from matplotlib import pyplot

def return_cumsum_df(dataframe):
    flipped_df = dataframe.iloc[::-1]
    flipped_index = flipped_df.index
    flipped_columns = flipped_df.columns
    
    cumsum_df = pd.DataFrame(np.cumsum(flipped_df.as_matrix(), axis=0),
                             index=flipped_index,
                             columns=flipped_columns).iloc[::-1]
        
    return cumsum_df


def taxa_bar_plot(dataframe, figure=None):
    cumsum_df = return_cumsum_df(dataframe)
    
    if figure is None:
        fig = pyplot.figure()
    else:
        fig = None
    
    #set fig width
    min_width = 10
    width_as_per_number_of_columns = len(dataframe.columns) * 0.25
    
    if width_as_per_number_of_columns < 10:
        fig_width = min_width
    else:
        fig_width = width_as_per_number_of_columns
        
    fig_height = fig_width * (12/6)
    
    if fig_height > 18:
        fig_height = 18
    
    if fig_height < 12:
        fig_height = 12
    
    fig.set_size_inches(fig_width, fig_height)
    
    grid = pyplot.GridSpec(4, int(fig_width), wspace=0.2, hspace=0.1)
    main_ax = fig.add_subplot(grid[0, 5:])
    main_ax.set_ylim(0,dataframe.sum().max())
    main_ax.set_ylabel("Relative Abundance (%)")
    pyplot.xticks(rotation='vertical')

    bars = []
    for i, arr in enumerate(cumsum_df.as_matrix()):
        bar_ = main_ax.bar(cumsum_df.columns, arr)
        bars.append(bar_[0])
        
    ax_leg = fig.add_subplot(grid[0, :4])
    pyplot.axis('off')
    ax_leg.legend(bars,list(cumsum_df.index), loc='upper right')
    
    
    
    
    
    return fig
 
