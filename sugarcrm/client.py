import requests
import json
import hashlib
import sugarcrm
from sugarcrm.error import CrmAuthenticationError, CrmResponseError


class APIClient:
    def __init__(self, client=requests, logger=sugarcrm.logger):
        self.client = client
        self.session_id = None
        self.rest_url = sugarcrm.rest_url
        self.logger = logger

    def _api_request(self, method, args):
        if not self.session_id and method != "login":
            self._login()

        if self.session_id:
            args.insert(0, self.session_id)

        data = json.dumps(args)
        args = {
            "method": method,
            "input_type": "json",
            "response_type": "json",
            "rest_data": data,
        }
        self.logger.debug("SugarCRM request to {}, args={}".format(self.rest_url, args))
        response = self.client.get(self.rest_url, args)
        self.logger.debug("SugarCRM response: {}".format(response.content))
        return response

    def _login(self):
        encode = hashlib.md5(sugarcrm.password.encode("utf-8"))
        encoded_password = encode.hexdigest()
        args = {"user_auth": {"user_name": sugarcrm.username, "password": encoded_password}}
        response = self._api_request("login", args)
        result = response.json()
        if "id" in result:
            self.session_id = result["id"]
        else:
            raise CrmAuthenticationError("CRM Invalid Authentication")

    def search_email(self, email):
        args = [email, ["Accounts", "Contacts"], 0, 1, "", ["id"], False, False]
        self.logger.info("SugarCRM searching email: {}".format(email))
        response = self._api_request("search_by_module", args)
        result = response.json()

        if "entry_list" not in result:
            raise CrmResponseError("Unexpected Response: {}".format(response.content))
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
        args = [module, object_id, [], [], False]
        response = self._api_request("get_entry", args)
        result = response.json()
        self.logger.debug("SugarCRM response: {}".format(response.content))
        if "entry_list" not in result:
            raise CrmResponseError("Unexpected Response: {}".format(response.content))
        else:
            value = result["entry_list"][0]["name_value_list"][field]["value"]
            return value
