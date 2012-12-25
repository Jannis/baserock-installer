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


import pygtk
pygtk.require('2.0')
import gobject
import gtk


class Assistant(gtk.Window):

    __gsignals__ = {
        'cancel': (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE,
            ()
        ),
        'close': (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE,
            ()
        ),
        'prepare': (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE,
            (gtk.Widget, )
        ),
    }

    def __init__(self):
        gtk.Window.__init__(self)

        self.set_border_width(0)

        self._pages = []
        self._type = {}
        self._title = {}
        self._complete = {}
        self._label = {}
        self.index = 0
        self.committed = False

        table = gtk.Table()
        table.set_col_spacings(12)
        table.set_row_spacings(6)
        table.set_border_width(8)
        table.show()
        self.add(table)

        frame = gtk.Frame()
        frame.set_shadow_type(gtk.SHADOW_IN)
        frame.show()
        table.attach(frame, 0, 1, 0, 2, gtk.FILL, gtk.FILL)

        eventbox = gtk.EventBox()
        eventbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#dfdfdf'))
        eventbox.show()
        frame.add(eventbox)

        self.sidebar = gtk.VBox(False, 6)
        self.sidebar.set_border_width(6)
        self.sidebar.show()
        eventbox.add(self.sidebar)

        self.container = gtk.Frame()
        self.container.set_shadow_type(gtk.SHADOW_NONE)
        self.container.show()
        table.attach(self.container, 1, 2, 0, 1)

        table.set_row_spacing(0, 20)

        buttons = gtk.HButtonBox()
        buttons.set_spacing(6)
        buttons.set_layout(gtk.BUTTONBOX_END)
        buttons.show()
        table.attach(buttons, 1, 2, 1, 2, gtk.FILL, gtk.SHRINK)

        self.cancel_button = gtk.Button(stock=gtk.STOCK_CANCEL)
        self.cancel_button.connect('clicked', self.cancel)
        self.cancel_button.show()
        buttons.pack_end(self.cancel_button)

        self.back_button = gtk.Button(stock=gtk.STOCK_GO_BACK)
        self.back_button.connect('clicked', self.back)
        self.back_button.show()
        buttons.add(self.back_button)
        
        self.forward_button = gtk.Button(stock=gtk.STOCK_GO_FORWARD)
        self.forward_button.connect('clicked', self.forward)
        self.forward_button.show()
        buttons.add(self.forward_button)

        self.close_button = gtk.Button(stock=gtk.STOCK_CLOSE)
        self.close_button.connect('clicked', self.close)
        self.close_button.show()
        buttons.add(self.close_button)

    def cancel(self, button):
        self.emit('cancel')

    def back(self, button):
        index = self.get_current_page()
        self.set_current_page(index-1)

    def forward(self, button):
        index = self.get_current_page()
        self.set_current_page(index+1)

    def next_page(self):
        self.forward(self.forward_button)

    def close(self, button):
        pass

    def append_page(self, page):
        self._pages.append(page)

        label = gtk.Label()
        label.set_alignment(0.0, 0.0)
        label.show()
        self.sidebar.pack_start(label, False, False, 0)

        self._label[page] = label

    def set_page_type(self, page, page_type):
        self._type[page] = page_type

    def set_page_title(self, page, title):
        self._title[page] = title
        self._label[page].set_text('%s' % title)
        self._label[page].set_use_markup(True)

    def set_page_complete(self, page, complete):
        self._complete[page] = complete
        self._update()

    def set_current_page(self, index):
        old_page = self.container.get_child()
        if old_page:
            self.container.remove(old_page)
            self._label[old_page].set_text(self._title[old_page])

        self.index = index
        new_page = self._pages[index]
        self.emit('prepare', new_page)
        self._pages[index].emit('complete')

        self._label[new_page].set_markup('<b>%s</b>' % self._title[new_page])
        self.container.add(new_page)
        self._update()

    def get_current_page(self):
        return self.index

    def get_nth_page(self, index):
        return self._pages[index]

    def commit(self):
        self.committed = True
        self._update()

    def _update(self):
        index = self.get_current_page()
        page = self.get_nth_page(index)

        if page in self._complete:
            self.forward_button.set_sensitive(self._complete[page])
        else:
            self.forward_button.set_sensitive(False)

        if self._type[page] == gtk.ASSISTANT_PAGE_INTRO:
            self.back_button.hide()
        else:
            self.back_button.show()

        if self._type[page] == gtk.ASSISTANT_PAGE_SUMMARY \
                or self._type[page] == gtk.ASSISTANT_PAGE_CONFIRM:
                    self.close_button.show()
                    self.close_button.grab_default()
        else:
            self.close_button.hide()
            self.forward_button.grab_default()

        for button in [self.cancel_button,
                       self.back_button,
                       self.forward_button,
                       self.close_button]:
            if not page.child_focus(gtk.DIR_TAB_FORWARD):
                if button.get_visible() and button.get_sensitive():
                    button.grab_focus()

        if self.committed:
            self.back_button.hide()
