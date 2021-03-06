from __future__ import absolute_import, division, print_function

from glue.external.echo import keep_in_sync
from glue.core.layer_artist import LayerArtistBase
from glue.viewers.common.mpl_state import DeferredDrawCallbackProperty

# TODO: should use the built-in class for this, though we don't need
#       the _sync_style method, so just re-define here for now.


class MatplotlibLayerArtist(LayerArtistBase):

    zorder = DeferredDrawCallbackProperty()
    visible = DeferredDrawCallbackProperty()

    def __init__(self, axes, viewer_state, layer_state=None, layer=None):

        super(MatplotlibLayerArtist, self).__init__(layer)

        self.layer = layer or layer_state.layer

        # Keep a reference to the layer (data or subset) and axes
        self.axes = axes
        self._viewer_state = viewer_state

        # Set up a state object for the layer artist
        self.state = layer_state or self._layer_state_cls(viewer_state=viewer_state,
                                                          layer=self.layer)
        if self.state not in self._viewer_state.layers:
            self._viewer_state.layers.append(self.state)

        self.mpl_artists = []

        self.zorder = self.state.zorder
        self.visible = self.state.visible

        keep_in_sync(self, 'zorder', self.state, 'zorder')
        keep_in_sync(self, 'visible', self.state, 'visible')

    def clear(self):
        for artist in self.mpl_artists:
            try:
                artist.remove()
            except ValueError:  # already removed
                pass
        self.mpl_artists = []

    def redraw(self):
        self.axes.figure.canvas.draw()

    def __gluestate__(self, context):
        return dict(state=context.id(self.state))
