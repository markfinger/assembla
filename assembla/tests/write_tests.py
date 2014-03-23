# -*- coding: utf-8 -*-

import unittest
from assembla import API, Ticket, WikiPage
from assembla.tests.auth import auth

class TestAssembla(unittest.TestCase):

    assembla = API(
        key=auth[0],
        secret=auth[1],
    )
    assembla.cache_responses = False

    def __space_with_tickets(self, cutoff=1):
        for space in self.assembla.spaces():
            if len(space.tickets()) > cutoff:
                return space

    def test_update_ticket(self):
        space = self.__space_with_tickets()
        ticket = space.tickets()[0]

        current_summary = ticket['summary']
        new_summary = u"TEST"
        ticket['summary'] = new_summary

        ticket = ticket.write()

        # fetch a copy, assert it has the summary we just pushed
        ticket2 = space.tickets()[0]
        self.assertEqual(ticket2['summary'], new_summary)

        #put back the original summary
        ticket2['summary'] = current_summary
        ticket2.write()

    def test_new_ticket(self):

        space = self.__space_with_tickets()
        ticket = Ticket({'summary': "Here is a new ticket"})
        ticket.space = space

        assert 'number' not in ticket.data

        ticket = ticket.write()

        # ticket now has a number
        self.assertTrue(ticket['number'])
        self.assertTrue(ticket['id'])

        # tidy up (oh and test delete)
        ticket.delete()

    def _get_space_with_wiki_tools(self):
        for space in self.assembla.spaces():
            for tool in space.tools():
                if 'wiki' in tool['menu_name'].lower():
                    return space
        raise Exception('Can\'t find a space with the Wiki tool')

    def test_wiki_page_write_and_delete(self):
        space = self._get_space_with_wiki_tools()

        page_name = 'Test_page'

        wiki_page = WikiPage()
        wiki_page.space = space
        wiki_page['page_name'] = page_name
        wiki_page['contents'] = 'Test content'

        wiki_page = wiki_page.write()

        self.assertTrue(wiki_page['id'])

        self.assertTrue(len(space.wiki_pages(page_name=page_name)) > 0)

        space.wiki_pages(page_name=page_name)[0].delete()

        self.assertTrue(len(space.wiki_pages(page_name=page_name)) == 0)

if __name__ == '__main__':
    unittest.main()