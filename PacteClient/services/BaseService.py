import json
import datetime
import time

# --- Project Libraries --------------------------------------------------------
from PacteUtil.QuickConfig import QuickConfig
from PacteUtil.QuickConfig import UserType


class BaseService(object):
    """
    Utility function for any services for Pacte
    """

    def __init__(self, quickcfg: QuickConfig):
        self.config = quickcfg
        self.lastUUID = ""
        self.serviceName = ""
        self.tool = ""
        self.json_param = self.get_json_config
        self.corpusId = ""
        self.racsUrl = ""

    def getinfo(self):
        return self.config.getRequest(self.config.baseURLService + self.serviceName + "/info", None, None)

    def checkjobstatus(self, suuid: str):
        """
        Check the status of a specific job
        :param suuid: Job identifier
        :return: Job status
        """
        return self.config.getRequest(self.config.baseURLService + self.serviceName + "/status?uuid=" + suuid,
                                      None, None)

    def checkstatus(self):
        """
        Check the status of the last job submitted with this instance
        :return: Job status
        """
        if self.lastUUID:
            return self.checkjobstatus(self.lastUUID)
        else:
            return None

    def annotate(self):
        """
        Run the service
        :return: The unique identifier for the job launched
        """
        results = self.config.postRequest(self.config.baseURLService + self.serviceName + "/process?doc_url=" +
                                          self.racsUrl + "batch/corpora/" + self.corpusId + "/documents",
                                          UserType.CustomUser, self.get_json_config(), useServiceToken=True)
        jres = json.loads(results.text)
        if "uuid" in jres:
            self.lastUUID = jres["uuid"]

        return self.lastUUID

    def waituntilfinished(self, max_wait_time=60 * 60 * 24, wait_between_check=5, verbose=False):
        """
        Loop until the service fail or succeed, or a timeout is reached
        :param max_wait_time: Maximum time in second to wait for the service to fail or succeed
        :param wait_between_check: Time in seconds to wait between status check
        :return: Last status logged by the service on the service gateway
        """
        if not self.lastUUID or max_wait_time <= 0 or wait_between_check <= 0:
            return None

        status = None
        start_time = time.time()
        while time.time() - start_time <= max_wait_time:
            status = self.checkstatus()
            result = json.loads(status.text)

            if str(result["status"]).lower() in ["success", "failure"]:
                break
            else:
                if verbose:
                    print(str(result["status"]) + " (" + datetime.datetime.now().strftime('%H:%M:%S') + ")")
                time.sleep(wait_between_check)
        return status

    def get_json_config(self):
        pass
