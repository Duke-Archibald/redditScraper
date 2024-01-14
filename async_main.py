import asyncio
import contextlib
import faulthandler
import os
import pathlib
import re
import sys
import threading
import time
import traceback
import wave
from datetime import datetime, timedelta
### testing
import elevenlabs
import randomcolor
import winsound
from google.cloud import texttospeech
from google.oauth2 import service_account
import simpleaudio as sa
import soundfile
import srt
import asyncpraw
import asyncprawcore
import qdarkstyle
import spacy
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import QPersistentModelIndex, QTimer, QSettings
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QIcon, QCloseEvent
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QTableView, qApp
from elevenlabs import generate, set_api_key, RateLimitError
from pydub import AudioSegment
from pydub.playback import play
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QEventLoop as QEL
from qasync import QEventLoop, QApplication, asyncSlot
from scipy.io import wavfile

from resources.TableColorModel import TableColorModel
from resources.common import appname, winsanetize, padding
from ui.MainWindowUI import Ui_MainWindow

os.system("pyuic5 -o ui/MainWindowUI.py ui/MainWindow.ui")


class RedditInput(QMainWindow):
    def __init__(self):

        super().__init__()
        self.LselectedRows = None
        self.submissionUrlSplit = None
        self.submission = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(appname)
        self.setWindowIcon(QtGui.QIcon('resources/bookicon.png'))
        self.settings = QSettings("NovelApp", "reddit_v1")
        self.readSettings()
        self.validThread = True
        self.periodic_thread = threading.Thread(target=self.every, args=(5, self.handle_clear_sel))
        self.periodic_thread.start()

        self.credentials = service_account.Credentials.from_service_account_file("resources/"
                                                                                 "novelapp-322716-f629fcd1c568.json")
        self.client = texttospeech.TextToSpeechClient(credentials=self.credentials)

        self.ui.pb_cancel.clicked.connect(self.close)
        self.ui.pb_finish.clicked.connect(self.finish)
        self.ui.pb_next.clicked.connect(self.next)
        self.ui.pb_delete_line.clicked.connect(self.deleteRow)
        self.ui.pb_duplicate_line.clicked.connect(self.insertRow)
        self.ui.pb_merge_lines.clicked.connect(self.mergeRow)
        self.ui.pb_tts.clicked.connect(self.text_to_speech)
        # self.ui.pb_test.clicked.connect()

        self.ui.pb_sample.clicked.connect(self.sample)
        self.ui.pb_next.hide()
        self.ui.pb_finish.hide()
        self.ui.pb_clear.clicked.connect(self.handle_clear_sel)
        self.ui.pb_complete.clicked.connect(self.handle_complete)
        self.ui.le_url.textChanged.connect(self.novel_name)

        self.con = QSqlDatabase.addDatabase("QSQLITE")
        databasefile = "resources/Reddit.sqlite"
        self.con.setDatabaseName(databasefile)
        self.con.open()
        self.model_subreddit = QSqlTableModel(db=self.con)
        self.model_subreddit.setTable("subreddits")
        self.model_subreddit.select()
        self.ui.cb_subreddit.setModel(self.model_subreddit)
        self.ui.cb_subreddit.setModelColumn(1)

        self.model_submission = TableColorModel(db=self.con)
        self.model_submission.setTable("submissions")
        self.model_submission.select()
        self.ui.cb_post_title.setModel(self.model_submission)
        self.ui.cb_post_title.setModelColumn(1)

        self.model_chapter_entry = TableColorModel(db=self.con)
        self.model_chapter_entry.setTable("entries")
        self.model_chapter_entry.select()
        self.ui.cb_entry_name.setModel(self.model_chapter_entry)
        self.ui.cb_entry_name.setModelColumn(1)
        self.model_chapter_entry.setFilter(f"entry_submission = "
                                           f"'{self.model_submission.data(self.model_submission.index(self.ui.cb_post_title.currentIndex(), 2))}' and (entry_status = 'to-do' or entry_status = 'wip' or entry_status = 'TTS_Done')")

        self.model_voice = TableColorModel(db=self.con)
        self.model_voice.setTable("voices")
        self.model_voice.select()
        self.ui.cb_voice.setModel(self.model_voice)
        self.ui.cb_voice.setModelColumn(2)

        self.model_lines = TableColorModel(db=self.con)
        self.loadline(
            self.model_chapter_entry.data(self.model_chapter_entry.index(self.ui.cb_entry_name.currentIndex(), 2)))
        self.ui.tv_lines.selectionModel().selectionChanged.connect(self.tv_lines_clicked)

        self.reddit = asyncpraw.Reddit(client_id="MRaFf0j2qWq-sLXK-jRxkA",
                                       client_secret="_8SFyEvJ5WGGHeZ-l3RFmVMAhg1MBA",
                                       username="Stories_scrapper",
                                       password="cKFnF8TfJ4KwLNa",
                                       user_agent="Duke_Scrapper_for_stories")

        self.ui.cb_voice.activated.connect(self.ui.tv_lines.clearSelection)
        self.ui.cb_subreddit.activated.connect(self.comboboxChanged)
        self.ui.cb_post_title.activated.connect(self.comboboxChanged)
        self.ui.cb_entry_name.activated.connect(self.comboboxChanged)
        self.ui.cb_gender.activated.connect(self.comboboxChanged)
        self.model_voice.setFilter(f"voice_gender = '{self.ui.cb_gender.currentText()}'")
        self.model_voice.select()

    def readSettings(self):
        try:
            self.restoreGeometry(self.settings.value("geometry"))
            self.restoreState(self.settings.value("windowState"))

        except Exception as e:
            print("new pc no setting",e)

    def handle_clear_sel(self):
        self.ui.tv_lines.clearSelection()
        print(self.model_chapter_entry.index(self.ui.cb_entry_name.currentIndex(), 1).data())
        self.model_chapter_entry.setData(self.model_chapter_entry.index(self.ui.cb_entry_name.currentIndex(), 3),
                                         f"wip", Qt.EditRole)
        self.model_submission.setData(self.model_submission.index(self.ui.cb_post_title.currentIndex(), 3), f"wip",
                                      Qt.EditRole)
        self.model_chapter_entry.submitAll()
        self.model_submission.submitAll()

    def startThread(self):

        pass

    def every(self, delay, task):
        next_time = time.time() + delay
        while self.validThread:
            time.sleep(max(0, next_time - time.time()))
            try:
                task()
            except Exception:
                traceback.print_exc()
            next_time += (time.time() - next_time) // delay * delay + delay

    @asyncSlot()
    async def next(self):
        if self.ui.le_url.text() == "":
            pass
        else:
            self.ui.pb_next.hide()
            self.ui.pb_finish.hide()
            await self.import_from_reddit()
            self.ui.le_url.setText("")
            self.ui.le_url.setFocus()
            self.reloadcbb()

    @asyncSlot()
    async def finish(self):
        if self.ui.le_url.text() == "":
            pass
        else:
            await self.import_from_reddit()
        self.close()

    def sample(self):
        try:
            filename = f"voice_sample/{self.model_voice.data(self.model_voice.index(self.ui.cb_voice.currentIndex(), 1))}-{self.ui.cb_voice.currentText()}.wav"

            data, samplerate = soundfile.read(filename)
            soundfile.write(filename, data, samplerate)
            wave_obj = sa.WaveObject.from_wave_file(filename)
            play_obj = wave_obj.play()
            play_obj.wait_done()
        except:
            print("sample not found")

    def reloadcbb(self):
        print("reload")
        # self.model_lines.select()
        self.model_submission.select()
        self.model_subreddit.select()
        self.model_chapter_entry.select()
        self.model_voice.select()

    def comboboxChanged(self):
        print(self.sender().objectName())
        if self.sender() == self.ui.cb_subreddit:
            self.model_submission.setFilter(f"submission_subreddit = '{self.ui.cb_subreddit.currentText()}'")

        elif self.sender() == self.ui.cb_post_title:  # update progression novel and set filter complete or not
            self.model_chapter_entry.setFilter(f"entry_submission = "
                                               f"'{self.model_submission.data(self.model_submission.index(self.ui.cb_post_title.currentIndex(), 2))}' and (entry_status = 'to-do' or entry_status = 'wip')")

        elif self.sender() == self.ui.cb_entry_name:
            self.loadline(
                self.model_chapter_entry.data(self.model_chapter_entry.index(self.ui.cb_entry_name.currentIndex(), 2)))
        elif self.sender() == self.ui.cb_gender:
            print("gender")
            self.model_voice.setFilter(f"voice_gender = '{self.ui.cb_gender.currentText()}'")
            self.model_voice.select()

    def loadline(self, entry_code):
        Hidden = True
        notHidden = False
        self.model_lines.setTable("lines")
        self.model_lines.setHeaderData(1, Qt.Horizontal, "#")
        self.model_lines.setHeaderData(6, Qt.Horizontal, "entry")
        self.model_lines.setHeaderData(3, Qt.Horizontal, "Character Voice")
        self.model_lines.setHeaderData(2, Qt.Horizontal, "Line Text")

        Lfilter = f"line_entry = '{entry_code}'"
        self.model_lines.setFilter(Lfilter)
        self.model_lines.setSort(1, Qt.AscendingOrder)
        self.model_lines.select()
        self.ui.tv_lines.setModel(self.model_lines)
        self.model_lines.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.ui.tv_lines.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

        self.ui.tv_lines.setColumnHidden(0, Hidden)
        self.ui.tv_lines.setColumnHidden(1, notHidden)
        self.ui.tv_lines.setColumnHidden(2, notHidden)
        self.ui.tv_lines.setColumnHidden(3, Hidden)
        self.ui.tv_lines.setColumnHidden(4, Hidden)
        self.ui.tv_lines.setColumnHidden(5, notHidden)
        self.ui.tv_lines.setColumnHidden(6, Hidden)
        self.ui.tv_lines.setColumnHidden(7, Hidden)
        self.ui.tv_lines.setColumnHidden(8, Hidden)
        self.ui.tv_lines.setColumnHidden(9, Hidden)
        self.ui.tv_lines.setColumnHidden(10, Hidden)
        self.ui.tv_lines.setColumnHidden(11, Hidden)

        self.ui.tv_lines.setColumnWidth(2, 100)
        self.ui.tv_lines.setColumnWidth(1, 125)
        self.ui.tv_lines.setSelectionBehavior(QTableView.SelectRows)
        self.ui.tv_lines.setSelectionMode(QTableView.MultiSelection)

    @pyqtSlot('QItemSelection', 'QItemSelection')
    def tv_lines_clicked(self, selected, deselected):
        self.LselectedRows = self.ui.tv_lines.selectionModel().selectedRows()
        if selected:

            for x, index in enumerate(selected.indexes()):
                if x % 6 == 0:
                    if self.ui.cb_voice.currentText() != "":
                        # voice code
                        self.model_lines.setData(self.model_lines.index(index.row(), 3),
                                                 f"{self.model_voice.data(self.model_voice.index(self.ui.cb_voice.currentIndex(), 1))}",
                                                 Qt.EditRole)

                        # voice name
                        self.model_lines.setData(self.model_lines.index(index.row(), 2),
                                                 f"{self.model_voice.data(self.model_voice.index(self.ui.cb_voice.currentIndex(), 2))}",
                                                 Qt.EditRole)
                        # voice system
                        self.model_lines.setData(self.model_lines.index(index.row(), 4),
                                                 f"{self.model_voice.data(self.model_voice.index(self.ui.cb_voice.currentIndex(), 3))}",
                                                 Qt.EditRole)
                        # voice color
                        self.model_lines.setData(self.model_lines.index(index.row(), 11),
                                                 f"{self.model_voice.data(self.model_voice.index(self.ui.cb_voice.currentIndex(), 6))}",
                                                 Qt.EditRole)
                        # set entry and submission to wip

                    else:
                        # code
                        self.model_lines.setData(self.model_lines.index(index.row(), 3), f"to-do",
                                                 Qt.EditRole)
                        # name
                        self.model_lines.setData(self.model_lines.index(index.row(), 2), f"to-do",
                                                 Qt.EditRole)
                        # system
                        self.model_lines.setData(self.model_lines.index(index.row(), 4), f"none",
                                                 Qt.EditRole)
                        # color
                        self.model_lines.setData(self.model_lines.index(index.row(), 11), f"#ffffff",
                                                 Qt.EditRole)

    async def TTSTitle(self, folder_base, line_text, audioname):
        filename = (f'{"/".join(folder_base.split("/")[0:3])}/{audioname}.wav')
        filename2 = os.path.abspath(filename)
        # print(filename2, os.path.isfile(filename2))
        if not os.path.isfile(filename):
            audio = generate(text=line_text, voice="C94nrIONO8Li9asoWtIp")
            with open(filename, mode='wb') as f:
                f.write(audio)

            data, samplerate = soundfile.read(filename)
            soundfile.write(filename, data, samplerate)

    @asyncSlot()
    async def text_to_speech(self):

        def add_subtext(file, line):
            with open(file, "a", encoding="utf-8") as sub:
                print(line)
                sub.write(f"{line}\n")

        infomessagebox = QMessageBox(self)
        infomessagebox.setWindowTitle(f"{appname} - TTS")
        infomessagebox.setText("making TTS please wait")
        infomessagebox.setStandardButtons(QMessageBox.NoButton)
        infomessagebox.open()
        qApp.processEvents()
        api_key = "1f13e2ad164fb6ffe1c81706487e9152"
        set_api_key(api_key)
        Titles = 0
        query = QSqlQuery(db=self.con)
        entry_code = self.model_chapter_entry.data(
            self.model_chapter_entry.index(self.ui.cb_entry_name.currentIndex(), 2))
        Qpre1 = f"SELECT * FROM lines WHERE line_entry = '{entry_code}' ORDER BY line_num ASC"
        # print(Qpre1)
        query.exec_(Qpre1)
        subtitle_text = []
        filename_base = ""
        # if query.last():
        #     self.progress_bar.setMaximum(query.at() + 1)
        #     query.first()
        #     query.previous()
        quotaecceded = False
        while query.next():

            line_id = query.value(0)
            line_num = query.value(1)
            line_voice_name = query.value(2)
            line_voice = query.value(3)
            line_voice_system = query.value(4)
            line_text = query.value(5)
            line_subreddit = query.value(6)
            line_submission = query.value(7)
            line_submission_title = query.value(8)
            line_entry = query.value(9)
            line_entry_author = query.value(10)

            infomessagebox.setText(f"making TTS please wait -- line {line_num}")
            loop = QEL()
            QTimer.singleShot(1, loop.quit)
            loop.exec_()
            # filename_base = f"[{line_subreddit}]/{line_entry_author}/{winsanetize(line_submission)} ~ {winsanetize(line_submission_title)}"
            filename_base = f"data/{line_subreddit}/{winsanetize(line_submission)} - {winsanetize(line_submission_title)}/{line_entry_author}"
            os.makedirs(filename_base, exist_ok=True)
            filenameAudio = f"{padding(line_num, 3)}_{line_voice_name}"
            dirnameAudio = f'{filename_base}/audio'
            os.makedirs(dirnameAudio, exist_ok=True)
            subtitle_text.append(line_text)
            dirnameSub = f"{filename_base}/subtitles"
            os.makedirs(dirnameSub, exist_ok=True)
            filename_text_subtitle = f"{dirnameSub}/subtitle.txt"
            filename_title_text_subtitle = f"{'/'.join(dirnameSub.split('/')[:-2])}/Title_subtitle.txt"
            print(line_num)
            if line_num == 0:
                with open(filename_text_subtitle, "w", encoding="utf-8") as sub:
                    sub.write(f"")
                with open(filename_title_text_subtitle, "w", encoding="utf-8") as sub:
                    sub.write(f"")

            if line_voice == "to-do":
                add_subtext(filename_text_subtitle, line_text)
                continue
            if line_voice_system == "google":
                print("google")
                add_subtext(filename_text_subtitle, line_text)
                if not os.path.isfile(f'{dirnameAudio}/{filenameAudio}.wav'):
                    language_code = "-".join(line_voice.split("-")[:2])
                    if line_text.strip() == "…" or line_text.strip() == "'…'":
                        line_text = f'<speak><break time="750ms"/></speak>'
                        text_input = texttospeech.SynthesisInput(ssml=line_text)

                    else:
                        text_input = texttospeech.SynthesisInput(text=line_text)

                    voice_params = texttospeech.VoiceSelectionParams(
                        language_code=language_code, name=line_voice
                    )
                    audio_config = texttospeech.AudioConfig(
                        audio_encoding=texttospeech.AudioEncoding.LINEAR16
                    )
                    response = self.client.synthesize_speech(
                        input=text_input, voice=voice_params, audio_config=audio_config
                    )
                    with open(f"{dirnameAudio}/{filenameAudio}.wav", mode="wb") as out:
                        out.write(response.audio_content)

                    data, samplerate = soundfile.read(f"{dirnameAudio}/{filenameAudio}.wav")
                    soundfile.write(f"{dirnameAudio}/{filenameAudio}.wav", data, samplerate)

            if line_voice_system == "elevenlabs":
                print("elevenlabs")
                add_subtext(filename_text_subtitle, line_text)
                if not os.path.isfile(f'{dirnameAudio}/{filenameAudio}.wav'):
                    try:
                        audio = generate(text=line_text, voice=line_voice)
                    except RateLimitError as e:
                        infomessagebox.done(0)
                        infomessagebox2 = QMessageBox(self)
                        infomessagebox2.setWindowTitle(f"{appname} - autoSave")
                        infomessagebox2.setText(e.message, line_text)
                        infomessagebox2.setStandardButtons(QMessageBox.Close)
                        infomessagebox2.open()
                        quotaecceded = True
                        break
                    with open(f'{dirnameAudio}/{filenameAudio}.wav', mode='wb') as f:
                        f.write(audio)

                    data, samplerate = soundfile.read(f'{dirnameAudio}/{filenameAudio}.wav')
                    soundfile.write(f'{dirnameAudio}/{filenameAudio}.wav', data, samplerate)
            if line_voice_system == "none":
                if line_voice == "Title":
                    await self.TTSTitle(filename_base, line_text, filenameAudio)
                    add_subtext(filename_title_text_subtitle, line_text)
                    Titles += 1
                # data, samplerate = soundfile.read("resources/placeholder.wav")
                # soundfile.write(f'{dirnameAudio}/{filenameAudio}.wav', data, samplerate)

        sub_ok = await self.subtitle_gen(dirnameSub, dirnameAudio)
        title_sub_ok = await self.title_subtitle_gen("/".join(dirnameSub.split("/")[:-2]),
                                                     '/'.join(dirnameAudio.split("/")[:-2]))
        if sub_ok and title_sub_ok:
            self.model_chapter_entry.setData(
                self.model_chapter_entry.index(self.ui.cb_entry_name.currentIndex(), 3),
                f"TTS_Done", Qt.EditRole)
        if self.model_chapter_entry.submitAll():

            self.model_chapter_entry.select()
        else:
            print(self.con.lastError().text())
        infomessagebox.done(0)

    def handle_complete(self):
        self.model_submission.setData(self.model_submission.index(self.ui.cb_post_title.currentIndex(), 3),
                                      f"complete", Qt.EditRole)
        self.model_submission.submitAll()

    async def subtitle_gen(self, dirname_sub, dirname_audio):
        def nat_key(value):
            return tuple(int(s) if s.isdigit() else s for s in re.split(r"(\d+)", value))

        time0 = "00:00:00,000"
        date_format_str = '%H:%M:%S,%f'
        start = datetime.strptime(time0, date_format_str)
        sublist = []
        with (open(f"{dirname_sub}/subtitle.txt", "r") as subText):
            linelist = subText.readlines()
            _, _, audios = next(os.walk(dirname_audio))
            audios = [audio for audio in audios if ".wav" in audio]
            audiofilelist = os.scandir(dirname_audio)
            if len(linelist) != len(audios):
                print("number of lines")
                QMessageBox.information(
                    self,
                    f"{appname} - error",
                    f"the number of line does not match the number of audiofiles\ntext: {len(linelist)}\naudiofiles: {len(audios)}",
                )
                return False
            for z, entry in enumerate(sorted(audiofilelist, key=lambda e: nat_key(e.name))):
                print()
                path = (os.path.join(dirname_audio, entry.name))
                data, samplerate = soundfile.read(path)
                soundfile.write(path, data, samplerate)

                Fs, data = wavfile.read(path)
                n = data.size
                t = n / Fs
                y = (int((t * 1000) * 24) / 24)
                print(z, y, linelist[z])
                addnext = timedelta(milliseconds=y)

                end = start + addnext

                fullsub = ""
                startT = str(start.time()).replace('.', ',')
                endT = str(end.time()).replace('.', ',')
                if len(endT) == 15:
                    endT = endT[:-3]
                else:
                    endT = endT + ",000"
                if len(startT) == 15:
                    startT = startT[:-3]
                else:
                    startT = startT + ",000"
                fullsub += (str(z + 1) + "\n")
                fullsub += (f"{startT} --> "
                            f"{endT}\n")
                fullsub += (str(linelist[z]).replace(",.", ".").replace(".", "") + "\n")
                sublist.append(fullsub)
                start = end

            with open(f"{dirname_sub}/subtitle.srt", "w", encoding="utf16") as f:
                subtitle_gen_v = srt.parse("\n".join(sublist))
                subtitles = list(subtitle_gen_v)
                f.write(srt.compose(subtitles))
            return True

    async def title_subtitle_gen(self, dirname_sub, dirname_audio):
        def nat_key(value):
            return tuple(int(s) if s.isdigit() else s for s in re.split(r"(\d+)", value))

        time0 = "00:00:00,000"
        date_format_str = '%H:%M:%S,%f'
        start = datetime.strptime(time0, date_format_str)
        sublist = []
        with (open(f"{dirname_sub}/title_subtitle.txt", "r") as subText):
            linelist = subText.readlines()
            _, _, audios = next(os.walk(dirname_audio))
            audios = [audio for audio in audios if ".wav" in audio]
            _, _, audiofilelist = next(os.walk(dirname_audio))
            audiofilelist = [audio for audio in audiofilelist if ".wav" in audio]
            if len(linelist) != len(audios):
                print("number of lines")
                QMessageBox.information(
                    self,
                    f"{appname} - error",
                    f"the number of line does not match the number of audiofiles\ntext: {len(linelist)}\naudiofiles: {len(audios)}",
                )
                return False
            for z, entry in enumerate(sorted(audiofilelist, key=lambda e: nat_key(e))):
                print()
                path = (os.path.join(dirname_audio, entry))
                data, samplerate = soundfile.read(path)
                soundfile.write(path, data, samplerate)

                Fs, data = wavfile.read(path)
                n = data.size
                t = n / Fs
                y = (int((t * 1000) * 24) / 24)
                print(z, y, linelist[z])
                addnext = timedelta(milliseconds=y)

                end = start + addnext

                fullsub = ""
                startT = str(start.time()).replace('.', ',')
                endT = str(end.time()).replace('.', ',')
                if len(endT) == 15:
                    endT = endT[:-3]
                else:
                    endT = endT + ",000"
                if len(startT) == 15:
                    startT = startT[:-3]
                else:
                    startT = startT + ",000"
                fullsub += (str(z + 1) + "\n")
                fullsub += (f"{startT} --> "
                            f"{endT}\n")
                fullsub += (str(linelist[z]).replace(",.", ".").replace(".", "") + "\n")
                sublist.append(fullsub)
                start = end

            with open(f"{dirname_sub}/title_subtitle.srt", "w", encoding="utf16") as f:
                subtitle_gen_v = srt.parse("\n".join(sublist))
                subtitles = list(subtitle_gen_v)
                f.write(srt.compose(subtitles))
            return True

    async def import_from_reddit(self):

        # self.submission = self.reddit.submission(url)
        await self.submission.comments.replace_more(limit=None)

        urlsplit = self.submission.url.split("/")
        if len(urlsplit) > 4:
            if urlsplit[4] == "HFY":
                prequery = f"insert into 'subreddits'('subreddit_name') VALUES('{urlsplit[4]}');"
                # print(prequery)
                query = QSqlQuery()
                query.exec(prequery)
                await self.reddit_HFY(urlsplit)
            elif urlsplit[4] == "WritingPrompts":
                prequery = f"insert into 'subreddits'('subreddit_name') VALUES('{urlsplit[4]}');"
                # print(prequery)
                query = QSqlQuery()
                query.exec(prequery)
                await self.reddit_WP()
            else:
                QMessageBox.information(
                    self,
                    f"{appname} - bad URL",
                    f"the subreddit you want is not supported yet",
                )

    async def reddit_HFY(self, urlsplit):
        filename = f"HFY/{winsanetize(self.le_novel_name.text())}/{winsanetize(self.submission.title.replace(':', ''))}.BV"
        os.makedirs(filename, exist_ok=True)
        with open(filename, "w") as f:
            f.write(self.submission.selftext_html)
            # f.write(self.submission.selftext)
            await self.submission.comments.replace_more(limit=None)
            for comment in self.submission.comments.list():
                if comment.author == self.submission.author:
                    if len(comment.body) > 300:
                        f.write(comment.body_html)
                        # f.write(comment.body)
            f.write("\n" + self.submission.url)

    async def database_line_text_input(self, fullname, top):
        text = pathlib.Path(fullname).read_text(encoding="utf-8")
        nlp = spacy.load("en_core_web_sm")
        text = nlp(text).text

        text = text.replace("*****", "")
        text = text.replace("****", "")
        text = text.replace('”', '" ')
        text = text.replace('’', "'")
        text = text.replace('“', '" ')
        text = re.sub('\r+', '\r', text)
        text = re.sub('\n+', '\n.', text)
        text = text.replace('" ', '." ')
        text = text.replace('"', '')
        text = text.replace("..", ".")
        text = text.replace(" . ", ".")
        text = text.replace(".  ", ". ")
        text = re.sub("(^|[.?!])\s*([a-zA-Z])", lambda p: p.group(0).upper(), text)
        text = re.sub('\.([a-zA-Z])', '. \\1', text)
        text = re.sub('\s+', ' ', text)
        text = text.replace(". .", ".")
        text = text.replace(" .", ". ")
        text = text.replace(".. ", ". ")
        doc = nlp(text)

        for x, sent in enumerate(doc.sents):
            sent = sent.text.replace("'", "''").replace('. ', '.').strip()
            # print(x, sent)
            subreddit = self.submission.url.split("/")[4]
            if sent.strip() == "":
                continue
            title = winsanetize(self.submission.title.replace("'", "''"))
            prequery = (
                f"INSERT INTO 'lines' ('line_num','line_voice_name', 'line_text', 'line_voice', 'line_subreddit', "
                f"'line_submission', 'line_entry', 'line_voice_system', 'line_entry_author', 'line_submission_title',"
                f"'line_color')"
                f"VALUES ({x},'to-do','{sent}','to-do','{subreddit}','{self.submission}','{top}','none','{top.author.name}','{title}','#ffffff');")
            # prequery = (
            #     f"insert into 'lines'('line_num','line_text','line_voice','line_subreddit','line_submission','line_entry','line_voice_system') "
            #     f"VALUES('{x}','{sent}','to-do','{subreddit}','{self.submission}','{top}','none')")
            print("line sql")
            print(prequery)
            query = QSqlQuery()
            query.exec(prequery)

    async def reddit_WP(self):
        fullname = ""
        prequery = (
            f"insert into 'submissions'('submission_name','submission_code','submission_status','submission_url',"
            f"'submission_subreddit')"
            f"VALUES('{winsanetize(self.submission.title)}','{self.submission}','to-do','{self.submission.url}',"
            f"'{winsanetize(self.submission.url.split('/')[4])}');")
        print("submission sql")
        print(prequery)
        query = QSqlQuery()
        query.exec(prequery)

        await self.submission.comments.replace_more(limit=None)

        for top in self.submission.comments:
            if top.author is not None:
                if top.author.name != "AutoModerator" and top.author.name != "WritingPromptsRobot":
                    if len(top.body_html) > 350:
                        prequery = (
                            f"insert into "
                            f"'entries'('entry_author_name','entry_code','entry_status','entry_submission') "
                            f"VALUES('{top.author.name}','{top}','to-do','{self.submission}');")
                        # print(prequery)
                        query = QSqlQuery()
                        query.exec(prequery)
                        title = (winsanetize(self.submission.title).replace('_', ' ').replace('sp ', '')
                                 .replace('wp ', ''))
                        foldername = f"data/WritingPrompts/{winsanetize(self.submission)} - {title}/{winsanetize(top.author.name)}".replace(
                            " ", "_")
                        fullname = f"{foldername}/entry_text.txt"
                        os.makedirs(foldername, exist_ok=True)
                        with open(f"{fullname}", "w", encoding="utf8") as f:
                            print(top.author.name)
                            f.write(f"writing Prompt by {self.submission.author}\n")
                            f.write(
                                f"{self.submission.title.replace('_', ' ').replace('[SP] ', '').replace('[WP]', '')}\n")
                            f.write(f"Story from user {top.author.name}.\n")
                            f.write(top.body)
                            for comment in top.replies.list():
                                if comment.author == top.author:
                                    if len(comment.body) > 300:
                                        f.write(comment.body)
                            # f.write("\n" + self.submission.url)

                    await self.database_line_text_input(fullname, top)

    def deleteRow(self):
        try:
            index_list = []
            for model_index in self.LselectedRows:
                index = QPersistentModelIndex(model_index)
                index_list.append(index)
            for index in index_list:
                self.model_lines.removeRow(index.row())
            self.model_lines.submitAll()
            self.model_lines.select()
        except TypeError:
            QMessageBox.information(
                self,
                f"{appname} - error",
                f"no line selected",
            )

    def insertRow(self):
        try:
            for model_index in self.LselectedRows:
                r = self.model_lines.record()
                for z in range(self.model_lines.columnCount()):
                    data = self.model_lines.data(self.model_lines.index(model_index.row(), z), Qt.DisplayRole)
                    Hname = self.model_lines.record().fieldName(z)
                    if z == 1:
                        data = round(data + .1, 1)
                    if z == 0:
                        r.setGenerated(Hname, False)
                    else:
                        r.setValue(Hname, data)
                self.model_lines.insertRecord(-1, r)

                if self.model_lines.submitAll():
                    self.model_lines.select()
                else:
                    QMessageBox.information(
                        self,
                        f"{appname} - error",
                        f"there was an error while adding line"
                        f"\n{self.lines_model.lastError().text()}"
                        f"\nif blank no error was reported (wierd error)",
                    )
        except TypeError:
            QMessageBox.information(
                self,
                f"{appname} - error",
                f"no line selected",
            )

    def mergeRow(self):
        try:
            if len(self.LselectedRows) != 2:
                QMessageBox.information(
                    self,
                    f"{appname} - error",
                    f"you can only merge exactly 2 line",
                )
                return
            mergedLine = ""
            for model_index in self.LselectedRows:
                mergedLine += self.model_lines.data(self.model_lines.index(model_index.row(), 5), Qt.DisplayRole)
                mergedLine += " "

            r = self.model_lines.record()

            for z in range(self.model_lines.columnCount()):
                data = self.model_lines.data(self.model_lines.index(self.LselectedRows[0].row(), z), Qt.DisplayRole)
                Hname = self.model_lines.record().fieldName(z)
                if z == 1:
                    data = round(data + .1, 1)
                if z == 5:
                    data = mergedLine.strip()
                if z == 0:
                    r.setGenerated(Hname, False)
                else:
                    r.setValue(Hname, data)
            self.model_lines.insertRecord(-1, r)

            if self.model_lines.submitAll():
                self.deleteRow()
                self.model_lines.select()
            else:
                QMessageBox.information(
                    self,
                    f"{appname} - error",
                    f"there was an error while adding line"
                    f"\n{self.lines_model.lastError().text()}"
                    f"\nif blank no error was reported (wierd error)",
                )
        except TypeError:
            QMessageBox.information(
                self,
                f"{appname} - error",
                f"no line selected",
            )

    @asyncSlot()
    async def novel_name(self):
        if self.ui.le_url.text() != "":
            urlSplit = self.ui.le_url.text().split("/")

            try:
                if len(urlSplit) > 1:
                    if urlSplit[6] != "":
                        self.submission = await self.reddit.submission(id=urlSplit[6])
                elif len(urlSplit) == 1:
                    self.submission = await self.reddit.submission(id=urlSplit[0])

                self.submissionUrlSplit = self.submission.url.split("/")
                if self.submissionUrlSplit[2] == "www.reddit.com":
                    self.ui.le_sub.setText(self.submissionUrlSplit[4])
                    self.ui.le_novel_name.setText(self.submissionUrlSplit[7])
                    self.ui.pb_next.show()
                    self.ui.pb_finish.show()
                else:
                    self.ui.le_novel_name.setText("")
                    self.ui.le_sub.setText("not a reddit url")
            except IndexError:
                self.ui.le_sub.setText("!!no post found!!")
                self.ui.le_novel_name.setText("")
            except asyncprawcore.exceptions.NotFound:
                self.ui.le_sub.setText("!!no post found!!")
                self.ui.le_novel_name.setText("")
            except asyncprawcore.exceptions.BadRequest as s:
                print(s)
        else:
            self.ui.le_sub.setText("url empty")
            self.ui.le_novel_name.setText("")

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.settings.setValue('geometry', self.saveGeometry())
        self.settings.setValue('windowState', self.saveState())
        self.validThread = False
        self.con.close()


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
