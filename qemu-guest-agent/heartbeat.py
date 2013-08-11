
import json
import time

from libvirt_qemu import libvirt
from base_thread import BaseThread

import sender

RUN_HB = True
heartbeat_delay = 5
# `must` larger than 5s, default timeout of libvirt checking qga status is 5s
heartbeat_cmd_timeout = 6

class HeartBeatThread(BaseThread):
    def __init__(self):
        super(HeartBeatThread, self).__init__()
        global heartbeat_delay
        self.delay = heartbeat_delay
        self.sender = sender.MemcacheClient()
        self.qga_cmd = {"execute": "guest-sync", "arguments": {"id": 0}}

    def _run(self):
        global RUN_HB
        return RUN_HB

    def serve(self):
        print "-----heartbeat start: ", time.asctime()
        domains = self.helper.list_all_domains()
        for dom in domains:
            if not dom.isActive():
                print "domain is not active %s" % dom.UUIDString()
                continue
            heartbeat_cmd = json.dumps({"execute": "guest-sync",
                                    "arguments": {"id": long(time.time())}})
            uuid = dom.UUIDString()
            global heartbeat_cmd_timeout
            response = self.helper.exec_qga_command(dom, heartbeat_cmd,
                                            timeout=heartbeat_cmd_timeout)
            print "qga response: %s" % response
            if response:
                self.sender.report_heartbeat(uuid)
            else:
                print "heartbeat command failed"
        print "-----heartbeat end: ", time.asctime()

        self.start()