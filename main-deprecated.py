import asyncio
import faulthandler
import os
import sys

import praw
import prawcore
import qdarkstyle
from PyQt5 import uic, QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QMessageBox
from asyncqt import QApplication, QEventLoop

from resources.common import test, appname, winsanetize


class RedditInput(QDialog):
    def __init__(self):

        super(RedditInput, self).__init__()
        self.submissionUrlSplit = None
        self.submission = None
        uic.loadUi("ui/reddit_input.ui", self)
        self.setWindowIcon(QtGui.QIcon('resources/bookicon.png'))
        self.pb_cancel.clicked.connect(self.close)
        self.pb_finish.clicked.connect(self.finish)
        self.pb_next.clicked.connect(self.next)
        self.le_url.textChanged.connect(self.novel_name)
        self.reddit = praw.Reddit(client_id="MRaFf0j2qWq-sLXK-jRxkA",
                                  client_secret="_8SFyEvJ5WGGHeZ-l3RFmVMAhg1MBA",
                                  username="Stories_scrapper",
                                  password="cKFnF8TfJ4KwLNa",
                                  user_agent="Duke_Scrapper_for_stories")

    def next(self):
        if self.le_url.text() == "":
            pass
        else:
            self.import_from_reddit()
            self.le_url.setText("")
            self.le_url.setFocus()

    def finish(self):
        if self.le_url.text() == "":
            pass
        else:
            self.import_from_reddit()
        self.close()

    def import_from_reddit(self):

        # self.submission = self.reddit.submission(url)
        self.submission.comments.replace_more(limit=None)

        print(self.submission.url)
        urlsplit = self.submission.url.split("/")
        if len(urlsplit) > 4:
            if urlsplit[4] == "HFY":
                self.reddit_HFY(urlsplit)
            elif urlsplit[4] == "WritingPrompts":
                self.reddit_WP()
            else:
                QMessageBox.information(
                    self,
                    f"{appname} - bad URL",
                    f"the subreddit you want is not supported yet",
                )

    def reddit_HFY(self, urlsplit):
        filename = f"HFY/{self.le_novel_name.text()}/{self.submission.title.replace(':', '')}.BV"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            f.write(self.submission.selftext_html)
            # f.write(self.submission.selftext)

            for comment in self.submission.comments.list():
                if comment.author == self.submission.author:
                    if len(comment.body) > 300:
                        f.write(comment.body_html)
                        # f.write(comment.body)
            f.write("\n" + self.submission.url)

    def reddit_WP(self):
        filename = f"WritingPrompts/{winsanetize(self.submission.url.split('/')[6])} ~ {winsanetize(self.submission.url.split('/')[7]).replace('_', ' ').replace('sp ', '{SP} ').replace('wp ', '{WP} ')}/"
        if len(self.submission.selftext) > 300:
            fullname = f"{filename}entry-from-{self.submission.author.name}.html"
            try:
                os.makedirs(os.path.dirname(fullname), exist_ok=True)
            except OSError:
                pass
            with open(fullname, "w", encoding="utf8") as f:

                # f.write(f"\n\n***********\nNEW COMMENT from {top.author.name}\n***********\n\n")
                f.write(f"<h1>Story from u/{self.submission.author.name}</h1>")
                f.write(f"<h2>{self.submission.title}</h2>")
                f.write(self.submission.selftext_html)
                for comment in self.submission.comments.list():
                    if comment.author == self.submission.author:
                        if len(comment.body) > 300:
                            f.write(comment.body_html)
                f.write("\n" + self.submission.url)

        self.submission.comments.replace_more(limit=None)

        for top in self.submission.comments:
            if top.author is not None:
                if top.author.name != "AutoModerator":
                    if len(top.body_html) < 350:
                        continue
                    fullnameclean = f"{filename}entry-from-{winsanetize(top.author.name)}.html"
                    os.makedirs(os.path.dirname(fullnameclean), exist_ok=True)
                    with open(fullnameclean, "w", encoding="utf8") as f:

                        # f.write(f"\n\n***********\nNEW COMMENT from {top.author.name}\n***********\n\n")
                        f.write(f"<h1>Story from u/{top.author.name}</h1>")
                        f.write(f"<h2>{self.submission.title}</h2>")
                        f.write(top.body_html)
                        for comment in top.replies.list():
                            if comment.author == top.author:
                                if len(comment.body) > 300:
                                    f.write(comment.body_html)
                        f.write("\n" + self.submission.url)
    def novel_name(self):
        if self.le_url.text() != "":
            urlSplit = self.le_url.text().split("/")

            try:
                if len(urlSplit) > 1:
                    if urlSplit[6] != "":
                        self.submission = self.reddit.submission(id=urlSplit[6])
                elif len(urlSplit) == 1:
                    self.submission = self.reddit.submission(id=urlSplit[0])

                self.submissionUrlSplit = self.submission.url.split("/")
                if self.submissionUrlSplit[2] == "www.reddit.com":
                    self.le_sub.setText(self.submissionUrlSplit[4])
                    self.le_novel_name.setText(self.submissionUrlSplit[7])
                else:
                    self.le_novel_name.setText("")
                    self.le_sub.setText("not a reddit url")
            except IndexError:
                self.le_sub.setText("!!no post found!!")
                self.le_novel_name.setText("")
            except prawcore.exceptions.NotFound:
                self.le_sub.setText("!!no post found!!")
                self.le_novel_name.setText("")
            except prawcore.exceptions.BadRequest as s:
                print(s)
        else:
            self.le_sub.setText("url empty")
            self.le_novel_name.setText("")
if __name__ == "__main__":
    faulthandler.enable()

    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    dark_stylesheet = qdarkstyle.load_stylesheet_pyqt5()
    app.setStyleSheet(dark_stylesheet + "QMessageBox { messagebox-text-interaction-flags: 5; }")
    app.setWindowIcon(QIcon('resources/bookicon.png'))


    with loop:
            main = RedditInput()
            main.show()
            loop.run_forever()
