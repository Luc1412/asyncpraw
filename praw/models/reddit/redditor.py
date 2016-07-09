"""Provide the Redditor class."""
from json import dumps

from ...const import API_PATH
from ..listing.mixins import RedditorListingMixin
from .base import RedditBase
from .mixins import GildableMixin, MessageableMixin


class Redditor(RedditBase, GildableMixin, MessageableMixin,
               RedditorListingMixin):
    """A class representing the users of reddit."""

    EQ_FIELD = 'name'

    @classmethod
    def from_data(cls, reddit, data):
        """Return an instance of Redditor, bool, or None from ``data``."""
        if isinstance(data, bool):
            return data
        elif data in [None, '', '[deleted]']:
            return None
        else:
            return cls(reddit, data)

    def __init__(self, reddit, name=None, _data=None):
        """Initialize a Redditor instance.

        :param reddit: An instance of :class:`~.Reddit`.
        :param name: The name of the redditor.

        """
        if bool(name) == bool(_data):
            raise TypeError('Either `name` or `_data` must be provided.')
        super(Redditor, self).__init__(reddit, _data)
        self._listing_use_sort = True
        if name:
            self.name = name
        self._path = API_PATH['user'].format(user=self.name)

    def _info_path(self):
        return API_PATH['user_about'].format(user=self.name)

    def _friend(self, method, data):
        url = API_PATH['friend_v1'].format(user=self.name)
        return self._reddit.request(method, url, data=dumps(data))

    def friend(self, note=None):
        """Friend the Redditor.

        :param note: A personal note about the user. Requires reddit
            Gold. (Default: None)
        :returns: The json response from the server.

        Calling this method subsequent times will update the note.

        """
        return self._friend('PUT', data={'note': note} if note else {})

    def get_friend_info(self):
        """Return information about this friend, including personal notes.

        The personal note can be added or overwritten with :meth:friend, but
            only if the user has reddit Gold.

        :returns: The json response from the server.

        """
        url = self.reddit_session.config['friend_v1'].format(user=self.name)
        data = {'id': self.name}
        return self.reddit_session.request_json(url, data=data, method='GET')

    def unblock(self):
        """Unblock the Redditor.

        :returns: The json response from the server.

        Blocking must be done from a Message, Comment Reply or Submission
        Reply.

        """
        data = {'container': self._reddit.user.me().fullname,
                'name': self.name, 'type': 'enemy'}
        return self._reddit.post(API_PATH['unfriend'], data=data)

    def unfriend(self):
        """Unfriend the Redditor."""
        self._friend(method='delete', data={'id': self.name})
