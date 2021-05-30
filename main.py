#!/usr/bin/env python3
import sys
import argparse
from datetime import date, datetime, timedelta

import requests
from lxml import html
from sqlalchemy import create_engine
# import pdb


from tables import create_tables, Community, ActivityLog


URL = "http://www.fwpd.org/community/search-activity-logs/"


class Application(object):
    def __init__(self):
        self.eng = None

    def init_db(self):
        self.eng = create_engine(
            "postgresql://fwpd:fwpd@localhost/fwpd_activity",
            echo=True,
        )
        create_tables(self.eng)

    def run(self):
        yesterday = (date.today() - timedelta(days=1)).strftime("%m/%d/%Y")

        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--start",
            default=yesterday,
            help="Start date",
        )
        parser.add_argument(
            "--end",
            default=yesterday,
            help="End date",
        )
        args = parser.parse_args()

        self.init_db()

        payload = {
            "submit": 1,
            "startDate": args.start,
            "endDate": args.end,
            "searchLogs": "Search",
        }
        res = requests.post(URL, data=payload)

        if res.status_code == 200:
            tree = html.fromstring(res.content)

            # Skip 'All'
            communities = tree.xpath(
                '//*[@id="logSearchBlock"]/select/option/text()'
            )[1:]
            com = Community(self.eng)
            com.update_communities(communities)

            rows = tree.xpath('//*[@id="main"]/table/tr')

            inserts = []

            # Skip header row
            for row in rows[1:]:
                incident = xpath_text(row, 'td[1]/text()')
                incident_d = xpath_text(row, 'td[2]/text()')
                incident_t = xpath_text(row, 'td[3]/text()')
                nature = xpath_text(row, 'td[4]/text()')
                address = xpath_text(row, 'td[5]/text()')
                community = xpath_text(row, 'td[6]/text()')

                db_vals = {
                    'incident': incident,
                    'incident_dt': datetime.strptime(
                        "{0} {1}".format(incident_d, incident_t),
                        "%m/%d/%Y %I:%M%p",
                    ),
                    'nature': nature,
                    'address': address,
                    'community': community,
                }
                inserts.append(db_vals)

            activity_log = ActivityLog(self.eng)
            activity_log.add_new(inserts)
        else:
            return 1


def xpath_text(ele, path):
    res = ele.xpath(path)
    if res:
        return res[0]


def main():
    app = Application()
    return app.run()


if __name__ == '__main__':
    sys.exit(main())
