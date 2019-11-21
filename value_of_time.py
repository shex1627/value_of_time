# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.1.2
#   kernelspec:
#     display_name: default_ds_venv
#     language: python
#     name: default_ds_venv
# ---

from bokeh.plotting import figure, show
from bokeh.io import curdoc
from bokeh.layouts import layout, column
from bokeh.models import BasicTickFormatter, NumeralTickFormatter
from bokeh.models import ColumnDataSource, Div, Slider, Select, TextInput
from bokeh.models import HoverTool, Title, LabelSet

import numpy as np

max_yr = Slider(title="year span", start=1, end=20, value=5, step=1)
interest = Slider(title='yearly interest', start=0.01, end=0.5, value=0.05, step=0.01)
hourly_output = Slider(title='hourly output', start=5, end=200, value=50, step=5)
hour_wasted_per_day = Slider(title='hour wasted per day', start=1, end=24, value = 4, step=1)

# + {"active": ""}
# max_yr = 5 # values in 10 years
# interest = 0.05 # interest every year
# hourly_output = 50 # value of time per hour if not wasted, generally only money compounds 
# #saved_value_unit = ['day', 'week'] # for now, only do that daily / weekly
# hour_wasted_per_day = 4
# -

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(x=[], y=[], title=[]))

# +
hover = HoverTool(tooltips=[('year passed', '@x{0.00}'), ('output wasted', '@y{0.00}')], 
                  mode='mouse')

p = figure(plot_height=600, plot_width=700, x_axis_label='year', y_axis_label='$')
p.tools.append(hover)

# add a line renderer with legend and line thickness
p.line('x', 'y', source=source, legend="daily compound", line_width=2)
p.line('x', 'y2', source=source, legend="no compound", line_color = 'green', line_width=2)
p.yaxis.formatter = BasicTickFormatter(use_scientific=False)

p.legend.location = "top_left"


# +
def year_to_date(yr):
    return yr * 365

def update(principal, addon, r):
    compound = principal * (1 + r)
    return compound + addon

def compute_total_value_lost(hour_wasted_per_day, hourly_output, max_yr, interest):
    """ compount daily. """
    principal = 0
    value_saved_list = []
    for i in range(year_to_date(max_yr)):
        principal = update(principal, hour_wasted_per_day * hourly_output, interest/365)
        value_saved_list.append(principal)
    return value_saved_list

def update_plot():
    x = np.linspace(0, max_yr.value, year_to_date(max_yr.value))
    y = compute_total_value_lost(hour_wasted_per_day.value, hourly_output.value, max_yr.value, interest.value)
    y2 = compute_total_value_lost(hour_wasted_per_day.value, hourly_output.value, max_yr.value, 0)
    #p.title.text = f"Value lost if you waste {hour_wasted_per_day.value} hrs per day for {max_yr.value} year(s)"
    p.title.text = f"Value lost in {max_yr.value} yrs: compound daily: {y2[-1]}, no compound: {np.round(y[-1],2)}"
    source.data = dict(x=x, y=y, y2=y2)


# -

controls = [max_yr, interest, hourly_output, hour_wasted_per_day]
for control in controls:
    control.on_change('value', lambda attr, old, new: update_plot())

# initialization
update_plot()

# +
inputs = column(*controls, width=400, height=200)
inputs.sizing_mode = "fixed"
l = layout([
    [inputs, p],
])

update_plot()  # initial load of the data

curdoc().add_root(l)
curdoc().title = "Value of Time"
