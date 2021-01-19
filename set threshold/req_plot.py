import geoviews as gv
import geoviews.tile_sources as gvts
from geoviews import dim, opts
from matplotlib import pyplot as plt
import matplotlib.colors as mcolors
from bokeh.models import HoverTool
from bokeh.plotting import figure, output_file, show
from bokeh.models import Arrow, NormalHead, OpenHead, VeeHead
gv.extension('bokeh')


def get_color(data):    
    ##color mapping
    lst_col = mcolors.CSS4_COLORS
    lst_col = list(lst_col.values())
    keys = list(data['result'].unique())
    values = set(lst_col)
    dicti = dict(zip(keys,values))
    return data['result'].map(dicti).to_list()

def map_plot(data,result_cluster,color_cluster):
    charts_ = gv.Points(data, ['partner_longitude', 'partner_latitude'],
                                   ['origin', 'vol_cbm', 'weight_ton',result_cluster,color_cluster])
    tooltips = [
        ('so', '@origin'),
        ('vol', '@vol_cbm'),
        ('weight', '@weight_ton'),
        ('cluster', '@'+ str(result_cluster))
    ]
    hover = HoverTool(tooltips=tooltips)
    _plot = (gvts.CartoLight * charts_).opts(
        opts.Points(width=800, height=500, alpha=0.7,
                    show_legend=False,
#                     legend_position='left',
                    color=dim(str(color_cluster)), hover_line_color='black',  
                    line_color='black', xaxis=None, yaxis=None,
                    tools=[hover],size=20))
    return _plot