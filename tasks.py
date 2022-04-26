@shared_task
def scrape_one_twitter(sa_id: int, attempt: int):
    """Scrape a single twitter account for the follower_count.  If anything blows up for one user, it won't
    impact the rest. Also these are spaced out time to mitigate the rate limiting"""
    try:
        client = tweepy.Client(
            bearer_token=os.environ["TWITTER_BEARER_TOKEN"],
            wait_on_rate_limit=True,
            return_type=dict,
        )

        social_account = SocialAccount.objects.select_related("user", "user__profile").get(pk=sa_id)
        screen_name = social_account.get_provider_account().get_screen_name()

        logger.info(
            "Scraping Twitter for '%s' (ScreenName '%s')",
            social_account.user.username,
            screen_name,
        )
        twitter_user = client.get_user(id=social_account.uid, user_fields="public_metrics")
        logger.debug("Got: %s", twitter_user)

        if "errors" in twitter_user:
            logger.error(
                "Failed getting follower_count for %s: %s",
                social_account.user.username,
                twitter_user,
            )
            return 0

        try:
            followers_count = twitter_user["data"]["public_metrics"]["followers_count"]

            profile = social_account.user.profile
            logger.info(
                "%s had %d followers, now has %d followers",
                social_account.user.username,
                profile.twitter_followers_count,
                followers_count,
            )

            profile.twitter_followers_count = followers_count
            profile.save()
            return 1
        except KeyError:
            logger.exception(
                "Didn't get info for '%s': %s",
                social_account.user.username,
                twitter_user,
            )
            return 0
    except tweepy.errors.TwitterServerError:
        logger.exception("Twitter server threw an exception")
    except Exception:
        logger.exception("Shit is wierd man!")

    attempt += 1
    if attempt < 5:
        logger.info("%s\nScheduling retry #%d for %s", attempt, social_account.user.username)
        scrape_one_twitter.apply_async(
            kwargs={"sa_id": social_account.id, "attempt": attempt},
            countdown=15 * attempt,
        )
    return 0
