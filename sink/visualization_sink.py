import logging

from sink.base_sink import BaseSink
import plotly.graph_objects as go


class PlotlyVisualizationSink(BaseSink):
    """
    Plot the data which should be passed as a Plotly data structure
    """
    fig: go.FigureWidget

    def __init__(self, fig=None, name="plot"):
        self.logger = logging.getLogger(name)
        self.fig = fig or go.FigureWidget(layout={"title": name})
        self.name = name
        super().__init__(name, on_next=self.update_plot)

    @property
    def figure(self) -> go.FigureWidget:
        return self.fig

    def update_plot(self, x):
        try:
            with self.fig.batch_update():
                self.fig.update({"data": x})
            self.logger.debug("plot updated")
        except Exception as ex:
            self.logger.error("failed to update plot", exc_info=ex)
