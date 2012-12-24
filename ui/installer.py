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


from gi.repository import Gtk

from ui.pages.downloadreleasepage import DownloadReleasePage
from ui.pages.downloadreleasespage import DownloadReleasesPage
from ui.pages.selectreleasepage import SelectReleasePage
from ui.pages.finishpage import FinishPage
from ui.pages.welcomepage import WelcomePage


class Installer(Gtk.Assistant):

    def __init__(self):
        Gtk.Assistant.__init__(self)

        self.set_default_size(640, 400)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.connect('cancel', self.cancel)
        self.connect('delete-event', self.cancel)
        self.connect('close', self.close)
        self.connect('prepare', self.prepare)

        self.create_pages()

    def create_pages(self):
        self.pages = [
            {
                'id': 'welcome',
                'page': WelcomePage(self),
                'title': 'Welcome',
                'type': Gtk.AssistantPageType.INTRO,
                'complete': False,
            },
            {
                'id': 'download-releases',
                'page': DownloadReleasesPage(self),
                'title': 'Download Releases',
                'type': Gtk.AssistantPageType.CONTENT,
                'auto-advance': True,
            },
            {
                'id': 'select-release',
                'page': SelectReleasePage(self),
                'title': 'Select Release',
                'type': Gtk.AssistantPageType.CONTENT,
            },
            {
                'id': 'download-release',
                'page': DownloadReleasePage(self),
                'title': 'Download Release',
                'type': Gtk.AssistantPageType.CONTENT,
                'auto-advance': True,
            },
            {
                'id': 'finish',
                'page': FinishPage(self),
                'title': 'Summary',
                'type': Gtk.AssistantPageType.SUMMARY,
                'complete': True,
            }
        ]

        for page in self.pages:
            page['page'].connect('child-notify::complete', self.page_complete)
            page['page'].show()
            self.append_page(page['page'])
            self.set_page_type(page['page'], page['type'])
            self.set_page_title(
                    page['page'],
                    '%i. %s' % (self.pages.index(page) + 1, page['title']))
            if 'complete' in page and page['complete']:
                self.set_page_complete(page['page'], True)

        self.set_current_page(0)

    def page_info(self, page):
        return [x for x in self.pages if x['page'] is page][0]

    def results(self):
        results = {}
        for info in self.pages:
            results[info['id']] = info['result'] if 'result' in info else None
        return results

    def page_complete(self, page, pspec):
        info = self.page_info(page)
        if page.is_complete():
            self.set_page_complete(page, True)
            info['result'] = page.result()
            #if 'auto-advance' in info and info['auto-advance']:
            #    self.next_page()
        else:
            self.set_page_complete(page, False)
            info['result'] = None

    def prepare(self, installer, page):
        page.prepare(self.results())
    
    def cancel(self, *args):
        index = self.get_current_page()
        page = self.get_nth_page(index)
        if page:
            page.cancel()
        self.quit()

    def close(self, *args):
        self.quit()

    def quit(self):
        Gtk.main_quit()

    def run(self):
        self.show()
        Gtk.main()
