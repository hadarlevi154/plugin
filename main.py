import argparse
import sys
from plugin.dummyjson_plugin import DummyJsonPlugin
from plugin.plugin_config import PluginConfig
from plugin.constants import ConstantsParameters


def main():
    # Main entrypoint
    parser = argparse.ArgumentParser(description='Anecdotes DummyJSON plugin for evidence collection')
    parser.add_argument('--username', help='Username for authentication', default=ConstantsParameters.USERNAME)
    parser.add_argument('--password', help='Password for authentication', default=ConstantsParameters.PASSWORD)
    parser.add_argument('--api-base-url', help='Base URL for the API', default=ConstantsParameters.API_BASE_URL)
    parser.add_argument('--test-only', action='store_true', help='Run only connectivity test')
    args = parser.parse_args()

    # Create plugin configuration
    config = PluginConfig(
        username=args.username,
        password=args.password,
        api_base_url=args.api_base_url
    )

    # Initialize the plugin
    plugin = DummyJsonPlugin(config)

    # Run connectivity test
    print("Running connectivity test")

    connectivity_result = plugin.test_connectivity()
    if not connectivity_result.success:
        print(f"Connectivity test failed: {connectivity_result.message}")
        sys.exit(1)
    print(f"Connectivity test successful: {connectivity_result.message}")

    if args.test_only:
        print("Test only mode - exiting after connectivity test")
        sys.exit(0)

    # Collect evidence
    print("\nCollecting evidence")

    # Evidence E1 (User details)
    print("\n Evidence E1 (User details)")
    user_evidence = plugin.collect_user_details()
    if user_evidence.success:
        user = user_evidence.data.get('user', {})
        username = user.get('username', 'unknown user')
        print(f"Successfully collected user details for: {username}")
    else:
        print(f"Failed to collect user details: {user_evidence.message}")

    # Evidence E2 (List of posts)
    print("\n Evidence E2 (List of Posts)")
    posts_evidence = plugin.collect_posts()
    if posts_evidence.success:
        post_count = len(posts_evidence.data.get("posts", []))
        if post_count < ConstantsParameters.DEFAULT_POST_LIMIT:
            print(
                f"Partial Success - collected {post_count} posts out of {ConstantsParameters.DEFAULT_POST_LIMIT}")
        else:
            print(f"Successfully collected {post_count} posts.")
    else:
        print(f"Failed to collect posts: {posts_evidence.message}")

    # Evidence E3 (List of Posts with comments)
    print("\n Evidence E3 (List of Posts with comments)")
    posts_with_comments_evidence = plugin.collect_posts_with_comments()
    if posts_with_comments_evidence.success:
        post_count = len(posts_with_comments_evidence.data.get('posts', []))
        comment_count = sum(
            len(post.get('comments', [])) for post in posts_with_comments_evidence.data.get('posts', []))
        if post_count < ConstantsParameters.DEFAULT_POST_LIMIT:
            print(f"Partial success - collected {post_count} posts out of {ConstantsParameters.DEFAULT_POST_LIMIT}, with {comment_count} comments")
        else:
            print(f"Successfully collected {post_count} posts with a total of {comment_count} comments")
    else:
        print(f"Failed to collect posts with comments: {posts_with_comments_evidence.message}")

    print("\nEvidence collection completed")


if __name__ == "__main__":
    main()


