import praw
import os
import re
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
log = logging.getLogger(__name__)

reddit = praw.Reddit(
    client_id=os.environ['CLIENT_ID'],
    client_secret=os.environ['CLIENT_SECRET'],
    password=os.environ['ACCT_PASSWD'],
    user_agent='r/dataisbeautiful bot (https://github.com/cavedave/dataisbeautiful-bot)',
    username='cavedave'
)

OC_PATTERN = re.compile(r'[\[\(\{][oO][cC][\]\)\}]')

REPLY_TEMPLATE = (
    "Thank you for your [Original Content](https://www.reddit.com/r/dataisbeautiful/wiki/rules/rule3), /u/{author}!  \n"
    "**Here is some important information about this post:**\n\n"
    "* [View the author's citations](https://www.reddit.com{permalink})\n\n"
    "* [View other OC posts by this author](https://www.reddit.com/r/dataisbeautiful/search?q=author%3A\"{author}\"+title%3AOC&sort=new&include_over_18=on&restrict_sr=on)\n\n"
    "Remember that all visualizations on r/DataIsBeautiful should be viewed with a healthy dose of skepticism. "
    "If you see a potential issue or oversight in the visualization, please post a constructive comment below. "
    "Post approval does not signify that this visualization has been verified or its sources checked.\n\n"
    "Not satisfied with this visual? Think you can do better? "
    "[Remix this visual](https://www.reddit.com/r/dataisbeautiful/wiki/rules/rule3#wiki_remixing) with the data in the author's citation.\n\n"
    "---\n\n"
    "^^[I'm&nbsp;open&nbsp;source](https://github.com/cavedave/dataisbeautiful-bot)&nbsp;|&nbsp;"
    "[How&nbsp;I&nbsp;work](https://www.reddit.com/r/dataisbeautiful/wiki/flair#wiki_oc_flair)"
)

def get_submissions(subreddit):
    start_date = os.environ.get('START_DATE')
    end_date = os.environ.get('END_DATE')

    if start_date:
        start_ts = int(time.mktime(time.strptime(start_date, '%Y-%m-%d')))
        end_ts = int(time.mktime(time.strptime(end_date, '%Y-%m-%d'))) if end_date else int(time.time())
        log.info(f"Catchup mode: paginating back to {start_date}")

        last_id = None
        total = 0
        while True:
            params = {'after': f't3_{last_id}'} if last_id else {}
            batch = list(subreddit.new(limit=100, params=params))
            if not batch:
                log.info("No more posts to fetch")
                break

            for submission in batch:
                if submission.created_utc > end_ts:
                    continue
                if submission.created_utc < start_ts:
                    log.info(f"Reached start date, stopping pagination after {total} posts")
                    return
                total += 1
                yield submission

            last_id = batch[-1].id
            log.info(f"Fetched batch, last post date: {time.strftime('%Y-%m-%d', time.gmtime(batch[-1].created_utc))}, total yielded: {total}")
            time.sleep(1)  # be polite to Reddit API
    else:
        log.info("Normal mode: fetching 1000 newest posts")
        yield from subreddit.new(limit=1000)

def process_submissions():
    subreddit = reddit.subreddit('dataisbeautiful')
    catchup = os.environ.get('CATCHUP_MODE', 'false').lower() == 'true'

    for submission in get_submissions(subreddit):
        try:
            if not OC_PATTERN.search(submission.title):
                continue
            if submission.saved:
                continue
            if submission.approved_by is None:
                continue

            for comment in submission.comments:
                if comment.is_submitter and comment.is_root:
                    if submission.author_flair_css_class in ("ocmaker", None, ""):
                        flair_text = submission.author_flair_text or ""
                        if flair_text.startswith("OC: "):
                            oc_count = int(flair_text.replace("OC: ", "")) + 1
                        else:
                            oc_count = 1
                        new_flair = f"OC: {oc_count}"
                        subreddit.flair.set(submission.author.name, new_flair, "ocmaker")
                        log.info(f"Set flair for u/{submission.author.name} → {new_flair}")

                    if not catchup:
                        reply_text = REPLY_TEMPLATE.format(
                            author=submission.author.name,
                            permalink=comment.permalink
                        )
                        submission.reply(reply_text).mod.distinguish(sticky=True)
                        log.info(f"Replied to: {submission.id} — {submission.title[:60]}")

                    submission.save()
                    break

        except Exception as e:
            log.error(f"Error processing {submission.id}: {e}")

if __name__ == '__main__':
    log.info("Bot run started")
    process_submissions()
    log.info("Bot run complete")
