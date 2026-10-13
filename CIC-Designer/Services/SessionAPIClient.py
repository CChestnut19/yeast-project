import requests

class SessionAPIClient:
    def __init__(self,api_url):
        self.base_url = api_url
        self.session = requests.Session()
        self.login()
    def login(self):
        response = self.session.get(f'{self.base_url}login')
        csrf_token = self.session.cookies.get('csrftoken')
        headers = {'Referer':f'{self.base_url}login','X-CSRFToken':csrf_token}

