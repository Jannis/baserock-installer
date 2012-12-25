# vi:set sw=4 sts=4 ts=4 et nocindent:
#
# Copyright (C) 2012 Jannis Pohlmann <jannis.pohlmann@codethink.co.uk>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


import gio
import gobject
import gtk
import threading


class Task(gobject.GObject):

    __gsignals__ = {
        'started': (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE,
            ()
        ),
        'finished': (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE,
            ()
        ),
        'progress': (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE,
            (float, str),
        ),
        'error': (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE,
            (str, ),
        ),
    }

    def __init__(self):
        gobject.GObject.__init__(self)
        self.cancellable = gio.Cancellable()
        self.thread = threading.Thread(target=self.worker_thread)

    def start(self):
        self.cancellable.reset()
        self.thread.start()

    def worker_thread(self):
        try:
            self.run()
        except Exception, error:
            print 'worker thread raised an exception: %s' % error
            self.emit('error', error.message)

    def run(self):
        return NotImplemented

    def cancel(self):
        self.cancellable.cancel()
        self.thread.join()
