import urllib.request
import json
import hashlib
import sugarcrm


class SugarCrmAPI:
    def __init__(self, rest_url, username, password, logger=sugarcrm.logger):
        self.session_id = None
        self.rest_url = rest_url
        self.logger = logger

        encode = hashlib.md5(password.encode("utf-8"))
        encodedPassword = encode.hexdigest()
        args = {"user_auth": {"user_name": username, "password": encodedPassword}}
        response = self._api_request("login", args)
        result = json.loads(response.decode("utf-8"))

        if "id" in result:
            self.session_id = result["id"]
        else:
            raise sugarcrm.CrmError("CRM Invalid Authentication")

    def _api_request(self, method, args):
        data = json.dumps(args)
        args = {
            "method": method,
            "input_type": "json",
            "response_type": "json",
            "rest_data": data,
        }
        self.logger.debug("SugarCRM request to {}, args={}".format(self.rest_url, args))
        params = urllib.parse.urlencode(args).encode("utf-8")
        response = urllib.request.urlopen(self.rest_url, params)
        if not response:
            raise sugarcrm.CrmError("No HTTP Response from {}".format(method))
        response = response.read().strip()
        self.logger.debug("SugarCRM response: {}".format(response))
        return response

    def search_email(self, email):
        args = [self.session_id, email, ["Accounts", "Contacts"], 0, 1, "", ["id"], False, False]
        self.logger.info("SugarCRM searching email: {}".format(email))
        response = self._api_request("search_by_module", args)
        result = json.loads(response.decode("utf-8"))

        if "entry_list" not in result:
            raise sugarcrm.CrmError("Unexpected Response: {}".format(response))
        else:
            account_records = result["entry_list"][0]["records"]
            contact_records = result["entry_list"][1]["records"]

            account_id = contact_id = None
            if account_records:
                account_id = account_records[0]["id"]["value"]
            if contact_records:
                contact_id = contact_records[0]["id"]["value"]
            self.logger.info("Found account_id: {}, contact_id: {}".format(account_id, contact_id))
            return account_id, contact_id

    def get_field(self, module, object_id, field):
        args = [self.session_id, module, object_id, [], [], False]
        response = self._api_request("get_entry", args)
        result = json.loads(response.decode("utf-8"))
        self.logger.debug("SugarCRM response: {}".format(response))
        if "entry_list" not in result:
            raise sugarcrm.CrmError("Unexpected Response: {}".format(response))
        else:
            roles = result["entry_list"][0]["name_value_list"][field]["value"]
            return roles
