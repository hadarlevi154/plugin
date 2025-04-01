import requests
from typing import Dict
import logging

from .base_plugin import BasePlugin
from .models import ConnectivityResult, EvidenceResult
from .plugin_config import PluginConfig
from .constants import ConstantsParameters

# Logging
logging.basicConfig(level=logging.INFO, format=ConstantsParameters.LOGGING_FORMAT)
logger = logging.getLogger(__name__)


class DummyJsonPlugin(BasePlugin):

    def __init__(self, config: PluginConfig):
        super().__init__(config)
        self.base_url = config.api_base_url

    def test_connectivity(self) -> ConnectivityResult:
        # Test connectivity- DummyJSON API
        try:
            login_url = f"{self.base_url}/auth/login"
            payload = {
                'username': self.config.username,
                'password': self.config.password
            }

            logger.info(f"Testing connectivity with {login_url}")
            response = requests.post(login_url, json=payload)

            if response.status_code == ConstantsParameters.OK:
                data = response.json()
                logger.info(f"Authentication response: {data}")

                if ConstantsParameters.ACCESS_TOKEN in data:
                    self.auth_token = data['accessToken']
                    message = f"Successfully authenticated as {data.get('username', self.config.username)}"
                    logger.info(message)
                    return ConnectivityResult.success_result(message, self.auth_token)
                elif ConstantsParameters.TOKEN in data:
                    self.auth_token = data['token']
                    message = f"Successfully authenticated as {data.get('username', self.config.username)}"
                    logger.info(message)
                    return ConnectivityResult.success_result(message, self.auth_token)
                else: # Fallback if the no token
                    message = "Authentication succeeded but there is no token, using fallback"
                    logger.warning(message)
                    # Create a dummy token
                    self.auth_token = ConstantsParameters.DUMMY_TOKEN
                    return ConnectivityResult.success_result(message, self.auth_token)
            else:
                message = f"Authentication failed: {response.text}"
                logger.error(message)
                return ConnectivityResult.failure_result(message, response.status_code)

        except Exception as e:
            message = f"Connectivity test failed with an exception: {str(e)}"
            logger.exception(message)
            return ConnectivityResult.failure_result(message)

    def _make_authenticated_request(self, endpoint: str, method: str = 'GET', params: Dict = None) -> requests.Response:
        # Authenticated request
        if not self.auth_token:
            raise ValueError("Not authenticated. Call test_connectivity() first")

        url = f"{self.base_url}/{endpoint}"

        # Add authorization header if we have a real token
        if self.auth_token and self.auth_token != ConstantsParameters.DUMMY_TOKEN:
            headers = {'Authorization': f'Bearer {self.auth_token}'}
        else:
            headers = {}

        logger.info(f"Making {method} request to {url}")

        if method.upper() == ConstantsParameters.GET:
            response = requests.get(url, headers=headers, params=params)
        elif method.upper() == ConstantsParameters.POST:
            response = requests.post(url, headers=headers, json=params)
        else:
            raise ValueError(f"The HTTP method {method} is not supported")

        return response

    def collect_user_details(self) -> EvidenceResult:
        # Evidence E1 - Collecting user details
        try:
            # Direct users endpoint
            try:
                # Searching username
                search_url = f"users/search?q={self.config.username}"
                response = self._make_authenticated_request(search_url)

                if response.status_code == ConstantsParameters.OK:
                    data = response.json()
                    users = data.get('users', [])
                    if users and len(users) > 0:
                        user_data = users[0]
                        logger.info(f"Successfully collected user details for {user_data.get('username')}")
                        return EvidenceResult.success_result({"user": user_data})
            except Exception as e:
                logger.warning(f"Error searching user by username: {str(e)}")

            # If username search failed, try a sample user
            response = self._make_authenticated_request("users/1")

            if response.status_code == ConstantsParameters.OK:
                user_data = response.json()
                logger.info(f"Successfully collected sample user details for {user_data.get('username')}")
                return EvidenceResult.success_result({"user": user_data})
            else:
                message = f"Failed to collect user details: {response.text}"
                logger.error(message)
                return EvidenceResult.failure_result(message, response.status_code)

        except Exception as e:
            message = f"Failed to collect User details, with an exception: {str(e)}"
            logger.exception(message)
            return EvidenceResult.failure_result(message)

    def collect_posts(self) -> EvidenceResult:
        # Evidence E2 - Collecting posts
        try:
            # collecting posts in one request by setting limit = ConstantsParameters.DEFAULT_POST_LIMIT
            response = self._make_authenticated_request(f"posts?limit={ConstantsParameters.DEFAULT_POST_LIMIT}&skip=0")

            if response.status_code != ConstantsParameters.OK:
                message = f"Failed to collect posts: {response.text}"
                logger.error(message)
                return EvidenceResult.failure_result(message, response.status_code)

            # Extract posts
            data = response.json()
            posts = data.get('posts', [])

            # Validate we got the expected number of posts
            if len(posts) < ConstantsParameters.DEFAULT_POST_LIMIT:
                message = f"Expected {ConstantsParameters.DEFAULT_POST_LIMIT} posts but received {len(posts)}"
                logger.warning(message)
                return EvidenceResult.success_result({"posts": posts}, message)

            logger.info(f"Successfully collected {len(posts)} posts")
            return EvidenceResult.success_result({"posts": posts})

        except Exception as e:
            message = f"Posts collection failed with an exception: {str(e)}"
            logger.exception(message)
            return EvidenceResult.failure_result(message)

    def collect_posts_with_comments(self) -> EvidenceResult:
        # Evidence E3 - Collecting posts with comments evidence
        try:
            # collecting posts
            posts_result = self.collect_posts()
            if not posts_result.success:
                return posts_result

            posts = posts_result.data.get('posts', [])
            posts_with_comments = []

            # For each post, get comments
            for post in posts:
                post_id = post.get('id')
                try:
                    comments_response = self._make_authenticated_request(f"posts/{post_id}/comments")

                    if comments_response.status_code == ConstantsParameters.OK:
                        comments_data = comments_response.json()
                        post_with_comments = post.copy()
                        post_with_comments['comments'] = comments_data.get('comments', [])
                        posts_with_comments.append(post_with_comments)
                    else:
                        logger.warning(f"Failed to get comments for post {post_id}: {comments_response.text}")
                        # Add the post without comments
                        post_with_comments = post.copy()
                        post_with_comments['comments'] = []
                        posts_with_comments.append(post_with_comments)
                except Exception as e:
                    logger.warning(f"Exception getting comments for post {post_id}: {str(e)}")
                    # Add the post without comments
                    post_with_comments = post.copy()
                    post_with_comments['comments'] = []
                    posts_with_comments.append(post_with_comments)

            logger.info(f"Successfully collected {len(posts_with_comments)} posts with comments")
            return EvidenceResult.success_result({"posts": posts_with_comments})

        except Exception as e:
            message = f"Posts with comments collection failed with an exception: {str(e)}"
            logger.exception(message)
            return EvidenceResult.failure_result(message)

    def collect_evidence(self, evidence_type: str, **kwargs) -> EvidenceResult:
        # Collect evidence based on specified type
        evidence_methods = {
            'user_details': self.collect_user_details,
            'posts': self.collect_posts,
            'posts_with_comments': self.collect_posts_with_comments
        }

        method = evidence_methods.get(evidence_type)
        if not method:
            message = f"Unknown evidence type: {evidence_type}"
            logger.error(message)
            return EvidenceResult.failure_result(message)

        return method(**kwargs)

