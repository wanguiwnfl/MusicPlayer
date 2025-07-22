from PyQt6.QtGui import QIcon,QPainter,QPixmap,QFont
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QHBoxLayout, QGridLayout, \
    QFormLayout, QLabel, QMenu, QMainWindow, QMessageBox, QStatusBar, QSlider, QListWidget, QAbstractItemView, QToolBar, \
    QSpacerItem, QSizePolicy, QDialog, QDoubleSpinBox, QGroupBox,QStackedWidget
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl, Qt, QTimer, QTime,QPoint, QSize,QPropertyAnimation
import sys
from functools import partial


class MusicPlayer(QMainWindow):#继承Qwidget类 表示一个窗口
    def __init__(self):
        super().__init__()
        #设置主窗口
        self.setWindowTitle("🎵这是一个音乐播放器")   #设置窗口的标题
        self.setGeometry(500, 300, 800, 600)   #设置窗口的大小位置(x, y, width, height)  xy 表示
        #播放状态
        self.playbackStatus = True


        #界面
        #音乐列表
        self.music_list = []
        self.music_current_index = -1  #初始正在播放的是哪一首  -1表示没有   列表从0开始

        #定义音乐列表
        self.music_list_popup =QMenu(self)

        #设置窗口的用途  目前做的是一个音乐播放器
        self.player = QMediaPlayer()  #定义音频播放器的核心类
        self.audio_output = QAudioOutput()  #声音输出设备
        self.player.setAudioOutput(self.audio_output)  #QMediaPlayer（音乐源） ─────► QAudioOutput（音乐播放器） ─────► 系统声音输出（扬声器/耳机）（指定输出设备）
        self.audio_output.setVolume(0.5) #设置音量

        #设置滑动模块 （进度条）
        self.slider_ProgressBar = QSlider(Qt.Orientation.Horizontal)
        self.slider_ProgressBar.setRange(0,100)  #设置长度
        self.slider_ProgressBar.sliderReleased.connect(self.set_position)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_slider)
        self.timer.start(10)
        #时间模块
        self.playingSlider = QSlider(Qt.Orientation.Horizontal)
        self.playingSlider.setRange(0, 100)  # 假设为百分比
        self.slider_ProgressBarStartTimes = QLabel("00:00")
        self.slider_ProgressBarEndTimes = QLabel("00:00")
        self.player.duration()
        self.player.durationChanged.connect(self.update_total_duration)
        sliceTimerFont= QFont("Arial",10)
        self.slider_ProgressBarStartTimes.setFont(sliceTimerFont)
        self.slider_ProgressBarEndTimes.setFont(sliceTimerFont)

        self.if_slider_dragging = False
        self.slider_ProgressBar.sliderPressed.connect(self.slider_pressed)  # 拖动开始时暂停更新
        self.slider_ProgressBar.sliderReleased.connect(self.slider_released)  # 拖动结束后恢复更新

        # 设置滑动模块（音量）   小窗口
        self.VolumePopup =QDialog(self)
        self.VolumePopup.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup )
        # self.VolumePopup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.VolumePopup.setFixedSize(30,100)

        #界面模块
        #滑块 音量
        self.volume_slider = QSlider(Qt.Orientation.Vertical)
        self.volume_slider.setRange(0, 100)     # 区间值
        self.volume_slider.setValue(30)   #默认30
        self.volume_slider.sliderReleased.connect(self.change_volume)

        #将这个滑块放进音量的小窗口中
        volume_layout = QVBoxLayout()
        volume_layout.setContentsMargins(10, 10, 10, 10)  # 设置边距（可选）
        volume_layout.addWidget(self.volume_slider)  #给布局添加一个 滑块
        self.VolumePopup.setLayout(volume_layout)   #然后应用这个滑块到 窗口中

        #状态栏  软件下面的显示  比如进度等等
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('🎧 准备就绪')   #初始化默认信息

        #设置菜单栏
        #第一个设置下的菜单栏  添加关于和退出的选项
        menubarSet = self.menuBar()
        settings_menu = menubarSet.addMenu('设置')
        about_action = settings_menu.addAction("关于")
        about_action.triggered.connect(self.show_about)
        quit_action = settings_menu.addAction("退出")
        quit_action.triggered.connect(self.close)

        #信息菜单
        menubarInfo = self.menuBar()
        InfoMenu =  menubarInfo.addMenu('信息')
        aboutVersion = InfoMenu.addAction('版本')
        aboutVersion.triggered.connect(self.version)

        #定义界面上的按钮
        self.play_button = QPushButton("")  #无父类按钮
        self.play_button.setFixedSize(40, 40)
        self.play_button.setIcon(QIcon("icon/play.png"))
        self.play_button.setIconSize(QSize(40, 40))

        self.open_button = QPushButton("添加音乐")
        self.open_button.setFixedSize(100, 40)

        self.button_previoussong  = QPushButton("")
        self.button_previoussong.setIcon(QIcon("icon/previous.png"))
        self.button_previoussong.setFixedSize(40,40)

        self.button_nexttsong = QPushButton("")
        self.button_nexttsong.setIcon(QIcon("icon/next.png"))
        self.button_nexttsong.setFixedSize(40, 40)

        #按钮 列表
        self.button_music_list = QPushButton("")
        self.button_music_list.setIcon(QIcon("icon/list.png"))

        #按钮  音量
        self.Volume_icon_button  = QPushButton("")
        self.Volume_icon_button.setIconSize(QSize(30, 30))
        self.Volume_icon_button.setFixedSize(30, 30)
        self.Volume_icon_button.setIcon(QIcon("icon/Volumeicon.png"))


        #抽屉式界面
        #今日推荐
        self.DailyRecommendation =QWidget()  #页面

        self.page_recommendation = QWidget()  #页面
        recommend_layout = QVBoxLayout()
        label = QLabel("🎶 今日推荐歌曲：\n1. 青花瓷\n2. 稻香\n3. 告白气球")
        label.setStyleSheet("font-size:16px;padding-left:10px;padding-right:10px;background-image: url(/icon/DailyRecommendation.jpg);")
        btn_back = QPushButton("返回主界面")
        btn_back.clicked.connect(self.back_to_main)
        recommend_layout.addWidget(label)
        recommend_layout.addWidget(btn_back)
        self.page_recommendation.setLayout(recommend_layout)

        #私人漫游
        self.page_PrivateRoaming = QWidget()
        layout_PrivateRoaming = QVBoxLayout()
        label_PrivateRoaming = QLabel("📀 私人漫游：\n1. 夜曲\n2. 东风破")
        label_PrivateRoaming.setStyleSheet("font-size:18px;")
        btn_back2 = QPushButton("返回主界面")
        btn_back2.clicked.connect(self.back_to_main)
        layout_PrivateRoaming.addWidget(label_PrivateRoaming)
        layout_PrivateRoaming.addWidget(btn_back2)
        self.page_PrivateRoaming.setLayout(layout_PrivateRoaming)

        #热门歌曲
        self.page_PopularSongs = QWidget()
        layout_PopularSongs = QVBoxLayout()
        label_PopularSongs = QLabel("📀 热门歌曲：\n1. 晴天\n2. 简单爱")
        label_PopularSongs.setStyleSheet("font-size:16px;")
        btn_back3 = QPushButton("返回主界面")
        btn_back3.clicked.connect(self.back_to_main)
        layout_PopularSongs.addWidget(label_PopularSongs)
        layout_PopularSongs.addWidget(btn_back3)
        self.page_PopularSongs.setLayout(layout_PopularSongs)

        # --- 创建 QStackedWidget 管理两个页面 ---
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.DailyRecommendation)  # index 0
        self.stacked_widget.addWidget(self.page_recommendation)  # index 1
        self.stacked_widget.addWidget(self.page_PrivateRoaming)  #index 2
        self.stacked_widget.addWidget(self.page_PopularSongs)    #index 3

        #循环播放窗口
        self.LoopWindows_mainWindows = QWidget()
        self.LoopWindows =QHBoxLayout()
        self.label_LoopWindows = QLabel("ceshi")
        self.stacked_LoopWindows = QStackedWidget()  #堆叠窗口
        self.stacked_LoopWindows.setFixedSize(150,100)
        self.label_LoopWindows.setFixedSize(150,100)
        self.label_LoopWindows.setStyleSheet("font-size:16px;")
        self.LoopWindows.addSpacing(10)
        self.LoopWindows.addWidget(self.label_LoopWindows)
        self.LoopWindows.addSpacing(20)
        self.LoopWindows.addWidget(self.stacked_LoopWindows)
        self.LoopWindows.addSpacing(20)
        # self.LoopWindows_mainWindows.setStyleSheet("font-size:16px;border:2px solid black;")  #绘制边框
        self.LoopWindows_mainWindows.setLayout(self.LoopWindows)
        self.imagePath = ['icon/LoopWindwos.jpg','icon/HotSong.jpg','icon/DailyRecommendation.jpg']
        self.imageIndex = 0
        self.updateImage()

        #定时器
        self.imagetimer= QTimer()
        self.imagetimer.timeout.connect(self.updateImage)
        self.imagetimer.start(2000)

        for image in self.imagePath:
            label_loop = QLabel()
            label_loop.setAlignment(Qt.AlignmentFlag.AlignCenter)
            pixmap = QPixmap(image).scaled(self.stacked_LoopWindows.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            label_loop.setPixmap(pixmap)
            self.stacked_LoopWindows.addWidget(label_loop)

        self.stacked_LoopWindows.setCurrentIndex(self.imageIndex)  #初始化    setCurrentIndex  是配合QStackedWidget的一种用法 用于选择

        self.imagetimer_Two = QTimer()
        self.imagetimer_Two.timeout.connect(self.updateImage_Two)
        self.imagetimer_Two.start(2000)

        for buttons in [self.play_button, self.button_previoussong, self.button_nexttsong]:
            buttons.setStyleSheet("""
                QPushButton {
                    background-color: transparent; ;       /* 背景色：透明 */
                    color: white;                    /* 字体颜色：白色 */
                    font-size: 16px;                 /* 字体大小 */
                    border-radius: 20px;             /* 圆角半径 */
                    padding: 1px 2px;              /* 内边距 */
                    border: none                    /* 不显示边线 */
                }
                QPushButton:hover {
                    background-color: transparent;       /* 鼠标悬停颜色 */
                }
                QPushButton:pressed {
                    background-color: transparent;      /* 鼠标按下颜色 */
                }
            """)

        #消除上方边框的的框框
        self.DailyRecommendation.setStyleSheet(
            """
                QWidget {
                    border: none;
                    background-color: transparent;
                }
            """
        )

        #音乐滑块的样式
        self.VolumePopup.setStyleSheet("""
            QDialog {
                background-color:#ccc ;  /* 深灰半透明背景 */
                border-radius: 8px;           /* 圆角边框 */
                border: None;                /* 绿色边框 */
            }
        """)

        self.open_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;       /* 背景色：绿色 */
                color: white;                    /* 字体颜色：白色 */
                font-size: 14px;                 /* 字体大小 */
                border-radius: 10px;             /* 圆角半径 */
                padding: 10px 20px;              /* 内边距 */
                border: none;
            }
            QPushButton:hover {
                background-color: #33FF33;       /* 鼠标悬停颜色 */
            }
            QPushButton:pressed {
                background-color: #99FF33;      /* 鼠标按下颜色 */
            }
        """)

        #进度滑块设计
        self.slider_ProgressBar.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;  /* 轨道高度 */
                background: #444;  /* 轨道颜色 */
                border-radius: 3px;  /* 圆角 */
            }
            QSlider::handle:horizontal {
                background: #bb86fc;  /* 紫色滑块 */
                width: 16px;  /* 滑块宽度 */
                height: 16px;  /* 滑块高度 */
                margin: -5px 0;  /* 垂直居中 */
                border-radius: 8px;  /* 圆形滑块 */
            }
            QSlider::sub-page:horizontal {
                background: #bb86fc;  /* 已播放部分颜色 */
                border-radius: 3px;  /* 圆角 */
            }
        """)
        #音量滑块设计
        self.volume_slider.setStyleSheet("""
            QSlider::groove:vertical {
                width: 6px;  /* 轨道宽度 */
                background: #444;  /* 轨道颜色 */
                border-radius: 3px;  /* 圆角 */
            }
            QSlider::handle:vertical {
                background: #03dac6;  /* 青色滑块 */
                height: 16px;  /* 滑块高度 */
                width: 16px;  /* 滑块宽度 */
                margin: 0 -5px;  /* 水平居中 */
                border-radius: 8px;  /* 圆形滑块 */
            }
            QSlider::sub-page:vertical {
                background: #03dac6;  /* 已设置音量部分颜色 */
                border-radius: 3px;  /* 圆角 */
            }
        """)

        self.button_music_list.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;       /* 背景色：绿色 */
                color: white;                    /* 字体颜色：白色 */
                font-size: 16px;                 /* 字体大小 */
                border-radius: 10px;             /* 圆角半径 */
                padding: 3px 5px;              /* 内边距 */
            }
            QPushButton:hover {
                background-color: #33FF33;       /* 鼠标悬停颜色 */
            }
            QPushButton:pressed {
                background-color: #99FF33;      /* 鼠标按下颜色 */
            }
            """
        )
        self.Volume_icon_button.setStyleSheet(
            """
            QPushButton {
                border-radius: 10px;  /* 圆角 */
                background-color: transparent;       /* 背景色：绿色 */
                color: white;                    /* 字体颜色：白色 */
                font-size: 16px;                 /* 字体大小 */
                border-radius: 10px;             /* 圆角半径 */
                padding: 3px 5px;              /* 内边距 */
            }
            QPushButton:hover {
                background-color: #33FF33;       /* 鼠标悬停颜色 */
            }
            QPushButton:pressed {
                background-color: #99FF33;      /* 鼠标按下颜色 */
            }
            """
        )
        #槽函数   按钮点击事件
        self.play_button.clicked.connect(self.play_music)
        self.open_button.clicked.connect(self.open_file)
        self.button_previoussong.clicked.connect(self.previous_song)
        self.button_nexttsong.clicked.connect(self.next_song)
        self.button_music_list.clicked.connect(self.toggle_music_popup)
        self.Volume_icon_button.clicked.connect(self.show_volume_popup)
        self.player.positionChanged.connect(self.update_slider)

        '''布局'''
        #定义布局方式   QVBoxLayout 纵向布局
        #播放按钮
        Hlayout_Middle = QHBoxLayout()
        Hlayout_Middle.addWidget(self.button_previoussong)
        Hlayout_Middle.addSpacing(5)
        Hlayout_Middle.addWidget(self.play_button)
        Hlayout_Middle.addSpacing(5)
        Hlayout_Middle.addWidget(self.button_nexttsong)

        #开始结束时间
        Hlayout_Times = QHBoxLayout()
        Hlayout_Times.addWidget(self.slider_ProgressBarStartTimes)
        Hlayout_Times.addStretch()
        Hlayout_Times.addWidget(self.slider_ProgressBarEndTimes)

        # 音量按钮
        Hlayout_VolumeAdjustment = QHBoxLayout()
        Hlayout_VolumeAdjustment.addWidget(self.Volume_icon_button)

        #音乐列表
        Hlayout_MusicList = QHBoxLayout()
        Hlayout_MusicList.addWidget(self.button_music_list)

        #水平总布局
        Hlayout_Right = QHBoxLayout()
        Hlayout_Right.addStretch(8)
        Hlayout_Right.addLayout(Hlayout_VolumeAdjustment,1)
        Hlayout_Right.addLayout(Hlayout_MusicList,1)

        # 主水平布局
        Hlayout_Mainlayout= QHBoxLayout()
        Hlayout_Mainlayout.addStretch(4)
        Hlayout_Mainlayout.addLayout(Hlayout_Middle,2)
        Hlayout_Mainlayout.addLayout(Hlayout_Right, 4)

        # open_button 上方按钮
        V1layout = QVBoxLayout()
        V1layout.addStretch(4)
        V1layout.addWidget(self.open_button)
        V1layout.addStretch()

        # 最终垂直布局
        Vlayout = QVBoxLayout()
        # Vlayout.addLayout(Vlayout_SecondFloor)
        Vlayout.addLayout(V1layout)
        Vlayout.addLayout(Hlayout_Mainlayout)
        Vlayout.addWidget(self.slider_ProgressBar)
        Vlayout.addLayout(Hlayout_Times)
        Vlayout.insertWidget(0,self.creat_TodayRecommendationSection())
        Vlayout.insertWidget(1,self.LoopWindows_mainWindows)
        self.DailyRecommendation.setLayout(Vlayout)



        Vlayout_main = QVBoxLayout()
        Vlayout_main.addWidget(self.stacked_widget)

        central_widget = BackgroundWidget()
        central_widget.setLayout(Vlayout_main)
        self.setCentralWidget(central_widget)

    # 槽函数
    def updateImage_Two(self):
        next_index = (self.imageIndex + 1) % len(self.imagePath)

        # 当前页面和下一页
        current_widget = self.stacked_LoopWindows.widget(self.imageIndex)
        next_widget = self.stacked_LoopWindows.widget(next_index)

        # 把下一张放在右边准备滑动进来
        next_widget.move(self.stacked_LoopWindows.width(), 0)
        next_widget.show()

        # 动画1：当前图左滑出
        anim_out = QPropertyAnimation(current_widget, b"pos", self)
        anim_out.setDuration(500)
        anim_out.setStartValue(QPoint(0, 0))
        anim_out.setEndValue(QPoint(-self.stacked_LoopWindows.width(), 0))

        # 动画2：下一图从右滑入
        anim_in = QPropertyAnimation(next_widget, b"pos", self)
        anim_in.setDuration(500)
        anim_in.setStartValue(QPoint(self.stacked_LoopWindows.width(), 0))
        anim_in.setEndValue(QPoint(0, 0))

        # 启动动画
        anim_out.start()
        anim_in.start()

        # 切换索引
        self.imageIndex = next_index
        self.stacked_LoopWindows.setCurrentIndex(self.imageIndex)

    def updateImage(self):
        pixmap = QPixmap(self.imagePath[self.imageIndex])
        scaled_pixmap = pixmap.scaled(
            self.label_LoopWindows.size(), Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.label_LoopWindows.setPixmap(scaled_pixmap)

        # 下一张
        self.imageIndex = (self.imageIndex + 1) % len(self.imagePath)

    def update_total_duration(self,duration):
        minutes = int(duration / 60000)
        seconds = int((duration % 60000) / 1000)
        end_time_str = f"{minutes:02d}:{seconds:02d}"
        self.slider_ProgressBarEndTimes.setText(end_time_str)

    def slider_pressed(self):
        self.if_slider_dragging =True
        self.timer.stop()  # 停止定时器，防止更新进度条

    def slider_released(self):
        self.if_slider_dragging =False
        self.set_position()  # 设置播放位置
        self.timer.start(10)  # 恢复定时器

    def change_volume(self):
        value = self.volume_slider.value()
        self.audio_output.setVolume(value / 100.0)
        self.statusBar.showMessage(f"🔊 音量：{value}%")

    def show_volume_popup(self):
        # 获取音量按钮的全局坐标
        button_pos = self.Volume_icon_button.mapToGlobal(self.Volume_icon_button.rect().bottomLeft())
        # 将弹窗显示在按钮下方（或调整为合适位置）
        self.VolumePopup.move(button_pos.x(), button_pos.y() - self.VolumePopup.height() - 35)
        self.VolumePopup.show()

    def toggle_music_popup(self):
        self.update_music_menu()
        pos = self.button_music_list.mapToGlobal(self.button_music_list.rect().bottomLeft())
        self.music_list_popup.popup(pos)  # 弹出菜单

    def update_music_menu(self):
        self.music_list_popup.clear()
        for index, song_path in enumerate(self.music_list):
            song_name = song_path.split("/")[-1]
            action = self.music_list_popup.addAction(song_name)
            action.triggered.connect(partial(self.music_select, index))

    def previous_song(self):
        if self.music_list and self.music_current_index > 0:
            self.music_current_index -= 1
            self.load_and_play(self.music_current_index)
        else:
            self.statusBar.showMessage("🎵 已是第一首")

    def next_song(self):
        if self.music_list and self.music_current_index < len(self.music_list) -1:
            self.music_current_index += 1
            self.load_and_play(self.music_current_index)
        else:
            self.statusBar.showMessage("🎵 已是最后一首")

    def load_and_play(self, index):
        if 0 <= index < len(self.music_list):
            self.music_current_index = index
            self.player.setSource(QUrl.fromLocalFile(self.music_list[index]))
            # self.music_list_popup.setCurrentRow(index)  # 高亮当前歌曲
            self.play_music()

    def music_select(self,item):
        self.music_current_index = item
        print("music_list =", self.music_list)
        print("当前索引 =", self.music_current_index)
        if 0 <= self.music_current_index < len(self.music_list):
            self.player.setSource(QUrl.fromLocalFile(self.music_list[self.music_current_index]))
            self.play_music()

            # self.music_list_popup.hide()

    def update_slider(self):
        if self.if_slider_dragging:
            return
        duration = self.player.duration()  #获取音频总时长（毫秒单位）
        position = self.player.position()  #获取当前播放的位置（当前播放了多久，单位也是毫秒）。
        if duration > 0: #防止出现0的状态 音频未加载完
            self.slider_ProgressBar.setValue(int(position * 100 / duration))  #设置滑动快的进度，当前时间 / 总时长
            self.slider_ProgressBarStartTimes.setText(self.format_time(position))


    def format_time(self, ms):
        secs = ms // 1000
        return QTime(0, secs // 60, secs % 60).toString("mm:ss")

    def set_position(self):
        duration = self.player.duration()  #获取音频总时长
        if duration > 0:  #防止音频未加载完
            value = self.slider_ProgressBar.value()  #返回当前滑块的位置（整数）。
            new_pos = int(duration * value / 100)  #通过当前的value模块的位置 和 总时长  计算视频播放到的位置
            self.player.setPosition(new_pos)  #设置当前歌曲到对应进度

    def resizeEvent(self, event):
        self.update()  # 当窗口尺寸改变时，自动重绘背景

    def open_file(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "选择音乐文件", "", "音乐文件 (*.mp3 *.wav *.ogg)"
        )
        if paths:
            self.music_list = paths
            if self.music_current_index == -1:
                self.music_current_index = 0
                self.player.setSource(QUrl.fromLocalFile(self.music_list[0]))
                self.statusBar.showMessage('📂 已加载音乐文件')

    def play_music(self):
        if not self.music_list:
            self.statusBar.showMessage("音乐列表为空，请先添加音乐文件")
            return

        # 如果尚未开始播放任何歌曲
        if self.music_current_index == -1:
            self.music_current_index = 0
            self.player.setSource(QUrl.fromLocalFile(self.music_list[self.music_current_index]))
            # self.music_list_popup.setCurrentRow(self.music_current_index)


        # 如果正在播放，就暂停
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.play_button.setIcon(QIcon("icon/play.png"))
            self.statusBar.showMessage("⏸ 播放已暂停")
        else:
            # 恢复播放
            self.player.play()
            self.play_button.setIcon(QIcon("icon/pause.png"))
            self.statusBar.showMessage('▶ 正在播放 ' + self.music_list[self.music_current_index].split("/")[-1])

    def stop_music(self):
        self.player.stop()

    def show_about(self):
        #information 需要三个参数 self   弹窗名称   内容
        QMessageBox.information(self, "关于", "这是一个简易音乐播放器 Demo\n作者：你")

    def version(self):
        QMessageBox.information(self,'版本','当前版本为1.0')

    def VolumeMusicSlider(self,value):
        self.label.setText(f"音量：{value}%")
        self.audio_output.setVolume(value / 100.0)

    def  creat_TodayRecommendationSection(self):  #创建一个组件
        group  = QGroupBox(self)
        layout_section = QHBoxLayout()
        btn1 = QPushButton(f"推荐歌曲")
        btn1.setFixedSize(150, 100)
        btn1.setStyleSheet("""
                QPushButton {
                    border-radius: 10px;
                    border-image: url('./icon/DailyRecommendation.jpg');
                    color: white;                      /* 设置字体颜色为白色 */
                    font-family: "微软雅黑";            /* 设置字体为圆融宽体（微软雅黑是常见替代） */
                    font-size: 16px;                  /* 字体大小 */
                    font-weight: bold;               /* 字体加粗，可选 */
                    text-align: top center;          /* 文字居上居中 */
                    padding-top: 10px;               /* 向下偏移，避免太贴边 */
                }
                QPushButton:hover {
                    border-image: url('./icon/girl.jpg');
                }
            """)


        btn1.clicked.connect(lambda :self.stacked_widget.setCurrentIndex(1))  #每日推荐

        btn2 = QPushButton(f"私人漫游")
        btn2.setFixedSize(150, 100)
        btn2.setStyleSheet("""
                QPushButton {
                    border-radius: 10px;
                    border-image: url('./icon/PrivateRoaming.jpg');
                    color: white;                      /* 设置字体颜色为白色 */
                    font-family: "微软雅黑";            /* 设置字体为圆融宽体（微软雅黑是常见替代） */
                    font-size: 16px;                  /* 字体大小 */
                    font-weight: bold;               /* 字体加粗，可选 */
                    text-align: top center;          /* 文字居上居中 */
                    padding-top: 10px;               /* 向下偏移，避免太贴边 */
                }
                QPushButton:hover {
                    border-image: url('./icon/girl.jpg');
                }
            """)
        btn2.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))

        btn3 = QPushButton("热歌榜")
        btn3.setFixedSize(150, 100)
        btn3.setStyleSheet("""
                QPushButton {
                    border-radius: 10px;
                    border-image: url('./icon/HotSong.jpg');
                    color: white;                      /* 设置字体颜色为白色 */
                    font-family: "微软雅黑";            /* 设置字体为圆融宽体（微软雅黑是常见替代） */
                    font-size: 16px;                  /* 字体大小 */
                    font-weight: bold;               /* 字体加粗，可选 */
                    text-align: top center;          /* 文字居上居中 */
                    padding-top: 10px;               /* 向下偏移，避免太贴边 */
                }
                QPushButton:hover {
                    border-image: url('./icon/girl.jpg');
                }
            """)
        btn3.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))

        layout_section.addWidget(btn1)
        layout_section.addWidget(btn2)
        layout_section.addWidget(btn3)

        group.setLayout(layout_section)
        return group

    def Creat_loopwindows(self):
        group = QGroupBox(self)
        loopWindow = QHBoxLayout()
        btn = QPushButton("")
        btn.setFixedSize(150, 100)
        loopWindow.addWidget(btn)
        group.setLayout(loopWindow)
        return group


    def show_recommendation(self):
        self.stacked_widget.setCurrentIndex(1)

    def back_to_main(self):
        self.stacked_widget.setCurrentIndex(0)

class BackgroundWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bg = QPixmap("./icon/Background.jpg")

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.bg.isNull():
            # 拉伸并居中绘制背景图
            scaled = self.bg.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding)
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)



if __name__ == "__main__":
    app = QApplication(sys.argv)   #必须存在qt中 类似qt的启动器
    window = MusicPlayer()    #  实例化类
    window.show()  #显示窗口
    sys.exit(app.exec())  #启动事件循环。当用户关闭窗口时 app.exec() 退出，sys.exit() 确保整个 Python 程序退出。
