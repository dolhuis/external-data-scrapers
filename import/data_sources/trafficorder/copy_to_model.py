import argparse
import io
import logging
import time
from xml.etree import ElementTree

import requests

import db_helper
from data_sources.importer_class import Importer
from data_sources.link_areas import link_areas
from data_sources.trafficorder.models import TrafficOrder, TrafficOrderRaw

log = logging.getLogger(__name__)
logging.getLogger("urllib3").setLevel(logging.INFO)


class TrafficOrderImporter(Importer):
    raw_model = TrafficOrderRaw
    clean_model = 'importer_trafficorder'

    def __init__(self, *args, **kwargs):
        self.override = {
            'postcodeHuisnummer': 'postcode',
            'straatnaam': 'street_name',
            'verkeersbordcode': 'traffic_sign_code',
            'jaargang': 'year'
        }
        self.columns = TrafficOrder.__table__.columns
        return super().__init__(*args, **kwargs)

    def fetch(self, metadata_url):
        response = requests.get(metadata_url)
        return response.content

    def get_tag_name(self, tag):
        tag_name = tag.attrib['name'].split('.')[1]
        return self.override.get(tag_name, tag_name)

    def process_xml(self, root_tag, scraped_at):
        trafficorder_attr = {'scraped_at': scraped_at}
        spatial_tags = []
        traffic_sign_list = []

        for tag in root_tag:
            tag_name = self.get_tag_name(tag)

            if tag_name in self.columns.keys() and tag_name != 'traffic_sign_code':
                trafficorder_attr[tag_name] = tag.attrib['content']

            if tag_name == 'spatial' and tag.attrib['scheme'].split('.')[1] != 'Gemeente':
                spatial = {}
                coordinates = tag.attrib['content'].split(' ')
                spatial['geometrie'] = self.point_to_str(28992, coordinates)
                spatial['spatial_coordinates'] = ' '.join(coordinates)

                if trafficorder_attr.get('spatial_coordinates', 'empty') == 'empty':
                    trafficorder_attr.update(spatial)
                else:
                    spatial_tags.append(spatial)

            if tag_name == 'traffic_sign_code':
                traffic_sign = {}
                traffic_sign[tag_name] = tag.attrib['content']

                if trafficorder_attr.get(tag_name, 'empty') == 'empty':
                    trafficorder_attr.update(traffic_sign)
                else:
                    traffic_sign_list.append(traffic_sign)

        self.trafficorder_list.append(trafficorder_attr)

        for spatial in spatial_tags:
            trafficorder_copy = dict(**trafficorder_attr)
            trafficorder_copy.update(spatial)
            self.trafficorder_list.append(trafficorder_copy)

        for traffic_sign in traffic_sign_list:
            trafficorder_copy = dict(**trafficorder_attr)
            trafficorder_copy.update(traffic_sign)
            self.trafficorder_list.append(trafficorder_copy)

    def store(self, raw_data):
        self.trafficorder_list = []

        for row in raw_data:
            root = ElementTree.parse(io.BytesIO(row.data)).getroot()
            records_urls = root.iter('{http://standaarden.overheid.nl/sru}url')

            for url in records_urls:
                metadata_url = url.text.split('.html')[0] + '/metadata.xml'
                meta_root = ElementTree.parse(io.BytesIO(self.fetch(metadata_url))).getroot()

                self.process_xml(meta_root, row.scraped_at)

        log.info("Storing {} TrafficOrder entries".format(len(self.trafficorder_list)))
        self.session.bulk_insert_mappings(TrafficOrder, self.trafficorder_list)
        self.session.commit()
        self.session.close()


def main(make_engine=True):
    desc = "Clean data and import into db."
    inputparser = argparse.ArgumentParser(desc)

    inputparser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debugging"
    )

    inputparser.add_argument(
        "--link_areas", action="store_true",
        default=False, help="Link with neighbourhood areas"
    )

    args = inputparser.parse_args()

    if args.debug:
        log.setLevel(logging.DEBUG)

    start = time.time()

    if make_engine:
        engine = db_helper.make_engine()
        db_helper.set_session(engine)

    if args.link_areas:
        session = db_helper.session
        link_areas(session, 'importer_trafficorder')

    else:
        importer = TrafficOrderImporter()
        importer.start_import()

    log.info("Total time: %s", time.time() - start)


if __name__ == "__main__":
    main()
