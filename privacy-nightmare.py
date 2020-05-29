import logging
import json
import os
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK


class PrivacyNightmare(plugins.Plugin):
    __author__ = 'glenn@pegden.com.com'
    __version__ = '0.0.1'
    __license__ = 'Private (for now)'
    __description__ = 'Private Nightmare.  gps portions shameless stolen from evilsockets gps module and trimmed down to save on screen real estate'

    def __init__(self):
        self.running = True
        self.gps_up = False
        self.pn_count = 0
        self.pn_status = "Waiting....."
        self.pn_gps_coords = None

    def on_ready(self, agent):
        if 'gps_device' in self.options:
            if os.path.exists(self.options["gps_device"]):
                logging.info(
                    f"enabling bettercap's gps module for {self.options['gps_device']}"
                )
                try:
                    agent.run("gps off")
                except Exception:
                    pass

                agent.run(f"set gps.device {self.options['gps_device']}")
                agent.run(f"set gps.baudrate {self.options['gps_speed']}")
                agent.run("gps on")
                self.gps_up = True
            else:
                logging.warning("no GPS detected")
        else:
                logging.warning('no GPS configured')

    def on_loaded(self):
        logging.info("privacy nightmare plugin loaded")

        if 'pn_output_path' not in self.options or ('pn_output_path' in self.options and self.options['pn_output_path'] is None):
            logging.debug("pn_output_path not set")
            return


        if not os.path.exists(self.options['pn_output_path']):
            os.makedirs(self.options['pn_output_path'])


    def on_wifi_update(self, agent, access_points):
#        logging.info("PN: Incoming AP update")
        if self.running:

            if self.gps_up:
                info = agent.session()
                self.pn_gps_coords = info["gps"]

                if self.pn_gps_coords and all([
                    self.pn_gps_coords["Latitude"], self.pn_gps_coords["Longitude"]
                ]):
                    logging.info("PN: GPS %s %s" % (self.pn_gps_coords["Latitude"], self.pn_gps_coords["Longitude"]))
                else:
                    logging.info("Unknown location")
            else:
                logging.info("Unknown location (gps not up).")

            if len(access_points) == 0:
                 logging.info("PN: Empty AP list :(")

            for ap in access_points:
                logging.info("PN: We Got One! ( %s )" , str(ap))
                self.pn_status = ("Found AP: %s" % ap['hostname'])
                self.pn_count += 1
                pn_filename = "%s/%s.json" % (self.options['pn_output_path'],ap['hostname'])
                logging.info(f"saving GPS to {pn_filename} ({ap['hostname']} at {self.pn_gps_coords})")
                with open(pn_filename, "w+t") as fp:
                   json.dump(ap, fp)
                   json.dump(self.pn_gps_coords, fp)


    def on_ui_setup(self, ui):
        pos = (1, 76)
        ui.add_element('pn_status', LabeledValue(color=BLACK, label='', value='PN: Active',
                                                   position=pos,
                                                   label_font=fonts.Small, text_font=fonts.Small))

        pos = (300, 109)
        ui.add_element('pn_count', LabeledValue(color=BLACK, label='', value='PN: Active',
                                                   position=pos,
                                                   label_font=fonts.Small, text_font=fonts.Small))

    def on_ui_update(self, ui):
            ui.set('pn_status', "PN: %s" % (self.pn_status))
            ui.set('pn_count', "PN Hits: %s" % (self.pn_count))








