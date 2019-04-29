import json
import time
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

    def getInfo(self):
        return self.config.getRequest(self.config.baseURLService + self.serviceName + "/info", None, None)

    def checkJobStatus(self, tsUUID: str):
        """
        Check the status of a specific job
        :param UUID: Job identifier
        :return: Job status
        """
        return self.config.getRequest(self.config.baseURLService + self.serviceName + "/status?uuid=" + tsUUID,
                                      None, None)

    def checkStatus(self):
        """
        Check the status of the last job submitted with this instance
        :return: Job status
        """
        if self.lastUUID:
            return self.checkJobStatus(self.lastUUID)
        else:
            return None

    def annotate(self):
        """
        Run the service
        :return:
        """
        lsResults = self.config.postRequest(self.config.baseURLService + self.serviceName + "/process?doc_url=" +
                                            self.racsUrl + "batch/corpora/" + self.corpusId + "/documents",
                                            UserType.CustomUser, self.get_json_config(), useServiceToken=True)
        jres = json.loads(lsResults.text)
        if "uuid" in jres:
            self.lastUUID = jres["uuid"]

        return self.lastUUID

    def waitUntilFinished(self, maxWaitTime=60*60*24, waitBetweenCheck=5):
        """

        :param maxWaitTime: Maximum time in second to wait for the service to fail or succeed
        :param waitBetweenCheck: Time in seconds to wait between status check
        :return:
        """
        if not self.lastUUID or maxWaitTime <= 0 or waitBetweenCheck <= 0:
            return None

        start_time = time.time()
        while time.time() - start_time <= maxWaitTime:
            status = self.checkStatus()
            lsResult = json.loads(status.text)
            if lsResult["status"].lower() in ["success", "failure"]:
                break
            else:
                time.sleep(waitBetweenCheck)

    def get_json_config(self):
        pass
