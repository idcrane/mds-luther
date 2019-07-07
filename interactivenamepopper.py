import matplotlib
import matplotlib.pyplot as plt


matplotlib.use("MacOSX")


class NamePopper(object):
    """ Base class for setting up name popping in matplotlib.
        Uses matplotlib's event handlers.
        These event handlers need the platform to be specified
        with matplotlib.use()
    """

    def __init__(self, fig, point, name, color='black',
                 x_perimeter=30, y_perimeter=90):
        self.fig =fig
        self.x, self.y = point
        self.name = name
        self.color = color
        self.x_perimeter=x_perimeter
        self.y_perimeter=y_perimeter
        self.popped = False


    def event_is_close(self, event):
        return abs(self.x-event.xdata) < self.x_perimeter and \
            abs(self.y-event.ydata) < self.y_perimeter


class NamePopperOnClick(NamePopper):
    """ Name pops when you click close to a point.
        It stays until you click again. """

    def __init__(self, *args, **kwargs):
        super(NamePopperOnClick, self).__init__(*args, **kwargs)
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self)


    def __call__(self, event):
        return self.pop_on_click(event)

    def pop_on_click(self, event):
        if self.event_is_close(event):
            if not self.popped:
                self.popped_text = plt.annotate(self.name,
                                                (self.x,self.y),
                                                color=self.color)
                self.popped = True
            else:
                self.popped_text.remove()
                self.popped = False
            self.fig.canvas.draw()



class NamePopperOnHover(NamePopper):
    """ Names pop while you hover close to a point.
        Disappears when you move away.
    """

    def __init__(self, *args, **kwargs):
        super(NamePopperOnHover, self).__init__(*args, **kwargs)
        self.cid = self.fig.canvas.mpl_connect('motion_notify_event', self)

    def __call__(self, event):
        return self.pop_on_hover(event)


    def pop_on_hover(self, event):
        if event.xdata and event.ydata and self.event_is_close(event):
            if not self.popped:
                self.popped_text = plt.annotate(self.name, (self.x,self.y), color=self.color)
                self.popped = True
                self.fig.canvas.draw()
        elif self.popped:
            self.popped_text.remove()
            self.popped = False
            self.fig.canvas.draw()

############
