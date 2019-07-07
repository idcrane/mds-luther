import numpy as np
import matplotlib.pyplot as plt
from interactivenamepopper import NamePopperOnHover, NamePopperOnClick
from sklearn.linear_model import LinearRegression


class TwoVariableComparisonPlotter(object):

    def __init__(self, x_list, y_list, name_list, 
                 label_display_style="hover",
                 x_range = (None, None),
                 y_range = (None, None),
                 xlabel = None,
                 ylabel = None,
                 point_size=60,
                 interaction_proximity_x=None,
                 interaction_proximity_y=None):
        """label_display_style can be one of showall | click | hover"""
        self.x, self.y = np.array(x_list), np.array(y_list)
        self.x.shape = (len(self.x),1)
        self.y.shape = (len(self.y),1)
        self.names = name_list
        self.label_display_style = label_display_style
        self.xmin, self.xmax = x_range
        self.ymin, self.ymax = y_range
        self.xlabel, self.ylabel = xlabel, ylabel
        self.point_size=point_size
        self.interaction_proximity_x = interaction_proximity_x
        self.interaction_proximity_y = interaction_proximity_y
        self.set_color_scheme()
        self.initiate_figure()

    def set_color_scheme(self, 
                         point="#00A0B0",
                         name="#6A4A3C",
                         centerline = "#EB6841",
                         extratext = "#CC333F"):
        self.colors = {"point":point,
                       "name": name,
                       "centerline":centerline,
                       "extratext":extratext}

    def add_text(self, x, y, text):
        plt.annotate(text, (x,y), color=self.colors["extratext"])

    def fit_center_line(self):
        regression = LinearRegression(fit_intercept=False)
        self.linear_model = regression.fit(self.x,self.y)

    def initiate_figure(self):
        #with white frame instead of gray
        self.fig = plt.figure(facecolor="white")
        # remove alternate axes
        plt.axes().spines['top'].set_visible(False)
        plt.axes().spines['right'].set_visible(False)
        plt.axes().get_xaxis().tick_bottom()
        plt.axes().get_yaxis().tick_left()

    def set_axis_ranges_labels_and_ticks(self):
        # axis ranges and ticks
        if (self.xmin,self.xmax) != (None,None):
            xmin, xmax, xticks = self.start_stop_ticks_for_axis(self.x, 
                                                                self.xmin, 
                                                                self.xmax)
            plt.xticks( xticks )
            plt.axes().set_xlim([xmin,xmax])
        if (self.ymin,self.ymax) != (None,None):
            ymin, ymax, yticks = self.start_stop_ticks_for_axis(self.y, 
                                                                self.ymin, 
                                                                self.ymax)
            plt.yticks( yticks )
            plt.axes().set_ylim([ymin,ymax])
        # axis labels
        if self.xlabel:
            plt.xlabel(self.xlabel, fontsize=14, fontweight='bold')
        if self.ylabel:
            plt.ylabel(self.ylabel, fontsize=14, fontweight='bold')

    def set_interactive_proximity(self):
        # set how close you need to get to a point for hover/click to work
        xmin, xmax = min(self.x),max(self.x)
        ymin, ymax = min(self.y),max(self.y)
        if self.interaction_proximity_x is None:
            self.interaction_proximity_x = (xmax-xmin)/30.
        if self.interaction_proximity_y is None:
            self.interaction_proximity_y = (ymax-ymin)/30.



    def start_stop_ticks_for_axis(self, data, start, stop, num_ticks=5):
        if start is None:
            start =  0
        if stop is None:
            stop_order = 10**int(np.log10(np.amax(data)))
            stop =  max(0, stop_order * ((np.amax(data) // stop_order) + 1))
        step = (stop-start)/(num_ticks-1)
        ticks = np.arange(start, stop+2*step, step)
        return start, stop, ticks


    def put_point_labels(self):
        x_stdev = np.std(self.x) 
        name_poppers = []
        for name, xi, yi in zip(self.names, self.x, self.y):
            residual = yi - self.linear_model.predict(xi)
            label_location = (xi + 0.05*x_stdev, yi) 
            if self.label_display_style == "showall":
                plt.annotate(name, label_location, color=self.colors["name"])
            elif self.label_display_style == "click":
                popper = NamePopperOnClick(self.fig, label_location, 
                                           name, color=self.colors["name"], 
                                           x_perimeter = self.interaction_proximity_x,
                                           y_perimeter=self.interaction_proximity_y)
                name_poppers.append( popper )
            elif self.label_display_style == "hover":
                popper = NamePopperOnHover(self.fig, label_location, 
                                           name, color=self.colors["name"],
                                           x_perimeter = self.interaction_proximity_x,
                                           y_perimeter=self.interaction_proximity_y)
                name_poppers.append( popper )


    def plot_scatter_data_and_centerline(self):
        plt.scatter(self.x, self.y, s = self.point_size, color=self.colors["point"])
        plt.plot(sorted(self.x), sorted(self.linear_model.predict(self.x)), '--', 
                 color=self.colors["centerline"])
        
        
    def plot(self):
        self.fit_center_line()
        self.set_axis_ranges_labels_and_ticks()
        self.set_interactive_proximity()
        self.put_point_labels()
        self.plot_scatter_data_and_centerline()
        plt.show()
