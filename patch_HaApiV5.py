from requests import Response

from helloasso_api.exceptions import ApiV5Unauthorized

def call(
    self,
    sub_path: str,
    params: dict = None,
    method: str = "GET",
    data: dict = None,
    json: dict = None,
    headers: dict = None,
    include_auth: bool = True,
) -> Response:
    """Manage all api calls. It also handle re-authentication if necessary."""
    self.log.debug(f"Call : {method} : {sub_path}")
    url, all_headers, data, json, params = self.prepare_request(
        sub_path, headers, data, json, params, include_auth
    )

    try:
        result = self.execute_request(url, method, all_headers, data, json, params)
        return result
    except ApiV5Unauthorized:
        self.log.warning("401 Unauthorized response to API request.")
        if self.oauth.access_token:
            self.log.info("Old token: %s", all_headers["Authorization"])
            self.log.info("Refreshing old token")
            self.oauth.refresh_tokens()
        else:
            self.log.info("Get access token")
            self.oauth.get_token()
        return self.call(
            sub_path, params=params, method=method, data=data, headers=headers
        )