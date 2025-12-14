"""
JARVIS ULTIMATE GUI - Enhanced GUI for Jarvis Ultimate
- Real-time voice assistant integration
- All original GUI features
- Voice command display
- Response visualization
- System monitoring
- YouTube control interface
"""

import sys, math, random, time, os, threading, queue
from datetime import datetime, timedelta
try:
    import psutil
except:
    psutil = None

from PySide6.QtCore import Qt, QTimer, QRectF, QPointF, QSize, QObject, Signal, QThread
from PySide6.QtGui import (
    QPainter, QColor, QPen, QFont, QLinearGradient, QRadialGradient, QImage,
    QPixmap, QBrush, QFontInfo
)
from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QFrame,
    QSizePolicy, QGridLayout, QPushButton, QListWidget, QTextEdit, QSlider,
    QFileDialog, QMessageBox, QDialog, QFormLayout, QSpinBox, QScrollArea
)

# --------------------- Helpers & Themes ---------------------
def clamp(v, lo, hi): return max(lo, min(hi, v))
def safe_now_str(): return datetime.now().strftime("%Y%m%d_%H%M%S")

THEMES = {
    "blue": {"bg": (5, 12, 20), "accent": (60, 200, 255), "glow": (60,200,255,180)},
    "red": {"bg": (18, 6, 8), "accent": (255,110,90), "glow": (255,110,90,180)},
    "green": {"bg": (6, 18, 12), "accent": (80,220,120), "glow": (80,220,120,180)},
    "purple": {"bg": (12, 6, 18), "accent": (180,120,255), "glow": (180,120,255,180)}
}
THEME_ORDER = ["blue","red","green","purple"]

# --------------------- Voice Assistant Integration ---------------------
class VoiceAssistantWorker(QObject):
    """Handles communication with Jarvis Ultimate voice assistant"""
    
    voice_command_received = Signal(str)
    voice_response_received = Signal(str)
    system_status_updated = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.is_listening = False
        self.is_speaking = False
    
    def add_command(self, command):
        """Add voice command to display"""
        self.voice_command_received.emit(command)
    
    def add_response(self, response):
        """Add voice response to display"""
        self.voice_response_received.emit(response)
    
    def set_listening(self, listening):
        """Update listening status"""
        self.is_listening = listening
        status = "🎤 Listening..." if listening else "⏸️ Idle"
        self.system_status_updated.emit(status)
    
    def set_speaking(self, speaking):
        """Update speaking status"""
        self.is_speaking = speaking
        status = "🗣️ Speaking..." if speaking else "⏸️ Idle"
        self.system_status_updated.emit(status)

# --------------------- Enhanced UI Components ---------------------
class SectionTitle(QLabel):
    def __init__(self, text):
        super().__init__(text.upper())
        self.setStyleSheet("color:#CFE7FF; font-weight:700; font-size:10px; letter-spacing:0.6px; margin-bottom: 4px;")

class VoiceConversationWidget(QFrame):
    """Widget to display voice conversations"""
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QFrame { border-radius:8px; background:rgba(10,14,20,220); }")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8,8,8,8)
        
        self.title = SectionTitle("Voice Conversation")
        layout.addWidget(self.title)
        
        # Status indicator
        self.status_label = QLabel("⏸️ Idle")
        self.status_label.setStyleSheet("color:#A0C0E0; font-size:12px; font-weight:bold; padding:4px;")
        layout.addWidget(self.status_label)
        
        # Conversation display
        self.conversation_area = QTextEdit()
        self.conversation_area.setReadOnly(True)
        self.conversation_area.setStyleSheet("""
            QTextEdit {
                background: rgba(5,10,15,150);
                border: 1px solid rgba(60,120,180,50);
                border-radius: 6px;
                color: #DCECFB;
                font-size: 11px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.conversation_area, 1)
        
        # Quick commands
        commands_layout = QHBoxLayout()
        self.quick_commands = [
            ("🎵", "Play Music"),
            ("📸", "Screenshot"),
            ("🌤️", "Weather"),
            ("⏰", "Time")
        ]
        
        for icon, tooltip in self.quick_commands:
            btn = QPushButton(icon)
            btn.setToolTip(tooltip)
            btn.setFixedSize(32, 32)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(60,120,180,30);
                    border: 1px solid rgba(60,200,255,50);
                    border-radius: 16px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: rgba(60,200,255,50);
                }
            """)
            commands_layout.addWidget(btn)
        
        layout.addLayout(commands_layout)
    
    def add_command(self, command):
        """Add user command to conversation"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.conversation_area.append(f'<span style="color:#60C8FF;">[{timestamp}] 👤 You:</span> {command}')
        self.conversation_area.verticalScrollBar().setValue(
            self.conversation_area.verticalScrollBar().maximum()
        )
    
    def add_response(self, response):
        """Add Jarvis response to conversation"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.conversation_area.append(f'<span style="color:#50DC78;">[{timestamp}] 🤖 Jarvis:</span> {response}')
        self.conversation_area.verticalScrollBar().setValue(
            self.conversation_area.verticalScrollBar().maximum()
        )
    
    def update_status(self, status):
        """Update status indicator"""
        self.status_label.setText(status)

class YouTubeControlWidget(QFrame):
    """Widget for YouTube controls"""
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QFrame { border-radius:8px; background:rgba(10,14,20,220); }")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8,8,8,8)
        
        self.title = SectionTitle("YouTube Control")
        layout.addWidget(self.title)
        
        # Current playing
        self.now_playing = QLabel("No music playing")
        self.now_playing.setStyleSheet("color:#DCECFB; font-size:12px; font-weight:bold; padding:4px;")
        self.now_playing.setWordWrap(True)
        layout.addWidget(self.now_playing)
        
        # Control buttons
        controls_layout = QGridLayout()
        
        self.controls = {
            "⏮️": ("Previous", 0, 0),
            "⏯️": ("Play/Pause", 0, 1),
            "⏭️": ("Next", 0, 2),
            "🔇": ("Mute", 1, 0),
            "🔉": ("Vol Down", 1, 1),
            "🔊": ("Vol Up", 1, 2),
            "⛶": ("Fullscreen", 2, 0),
            "🔄": ("Repeat", 2, 1),
            "🔀": ("Shuffle", 2, 2)
        }
        
        for icon, (tooltip, row, col) in self.controls.items():
            btn = QPushButton(icon)
            btn.setToolTip(tooltip)
            btn.setFixedSize(40, 40)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(60,120,180,30);
                    border: 1px solid rgba(60,200,255,50);
                    border-radius: 20px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background: rgba(60,200,255,50);
                }
                QPushButton:pressed {
                    background: rgba(60,200,255,80);
                }
            """)
            controls_layout.addWidget(btn, row, col)
        
        layout.addLayout(controls_layout)
    
    def set_now_playing(self, song):
        """Update currently playing song"""
        self.now_playing.setText(f"🎵 {song}")

class SystemMonitorWidget(QFrame):
    """Enhanced system monitoring"""
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QFrame { border-radius:8px; background:rgba(10,14,20,220); }")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8,8,8,8)
        
        self.title = SectionTitle("System Monitor")
        layout.addWidget(self.title)
        
        # System stats
        self.stats_layout = QVBoxLayout()
        
        self.cpu_bar = self.create_progress_bar("CPU", "#FF6B6B")
        self.memory_bar = self.create_progress_bar("Memory", "#4ECDC4")
        self.disk_bar = self.create_progress_bar("Disk", "#45B7D1")
        self.battery_bar = self.create_progress_bar("Battery", "#96CEB4")
        
        for bar in [self.cpu_bar, self.memory_bar, self.disk_bar, self.battery_bar]:
            self.stats_layout.addWidget(bar)
        
        layout.addLayout(self.stats_layout)
        
        # Network info
        self.network_label = QLabel("Network: 0.0 MB/s ↑ | 0.0 MB/s ↓")
        self.network_label.setStyleSheet("color:#A0C0E0; font-size:10px; padding:4px;")
        layout.addWidget(self.network_label)
    
    def create_progress_bar(self, name, color):
        """Create a custom progress bar"""
        container = QFrame()
        container.setFixedHeight(30)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0,0,0,0)
        
        label = QLabel(name)
        label.setFixedWidth(60)
        label.setStyleSheet("color:#DCECFB; font-size:10px;")
        
        progress = QFrame()
        progress.setStyleSheet(f"""
            QFrame {{
                background: rgba(20,30,40,150);
                border: 1px solid rgba(60,120,180,50);
                border-radius: 8px;
            }}
        """)
        
        value_label = QLabel("0%")
        value_label.setFixedWidth(35)
        value_label.setStyleSheet("color:#DCECFB; font-size:10px;")
        value_label.setAlignment(Qt.AlignRight)
        
        layout.addWidget(label)
        layout.addWidget(progress, 1)
        layout.addWidget(value_label)
        
        # Store references for updating
        container.progress_frame = progress
        container.value_label = value_label
        container.color = color
        
        return container
    
    def update_stats(self, cpu, memory, disk, battery):
        """Update system statistics"""
        stats = [
            (self.cpu_bar, cpu),
            (self.memory_bar, memory),
            (self.disk_bar, disk),
            (self.battery_bar, battery)
        ]
        
        for bar, value in stats:
            bar.value_label.setText(f"{int(value)}%")
            # Update progress bar visual here if needed
    
    def update_network(self, upload, download):
        """Update network statistics"""
        self.network_label.setText(f"Network: {upload:.1f} MB/s ↑ | {download:.1f} MB/s ↓")

class EnhancedEnergyCore(QWidget):
    """Enhanced energy core with voice integration"""
    def __init__(self):
        super().__init__()
        self.phase = 0.0
        self.rings = 5
        self.speed = 1.0
        self.glow_intensity = 1.0
        self.theme = THEMES['blue']
        self.voice_active = False
        self.setMinimumSize(420, 420)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    def set_voice_active(self, active):
        """Set voice activity state"""
        self.voice_active = active
        if active:
            self.speed = 2.0
            self.glow_intensity = 2.0
        else:
            self.speed = 1.0
            self.glow_intensity = 1.0
        self.update()
    
    def set_theme(self, theme_key):
        """Set color theme"""
        self.theme = THEMES.get(theme_key, self.theme)
        self.update()
    
    def paintEvent(self, event):
        """Enhanced paint event with voice visualization"""
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        rect = self.rect()
        cx, cy = rect.center().x(), rect.center().y()
        
        base_radius = min(rect.width(), rect.height()) * 0.18
        
        # Background gradient
        bg = QRadialGradient(QPointF(cx, cy), base_radius * 3.0)
        bg.setColorAt(0.0, QColor(8, 10, 14))
        bg.setColorAt(1.0, QColor(6, 8, 12, 0))
        p.fillRect(rect, bg)
        
        # Voice activity glow
        if self.voice_active:
            glow_col = self.theme['glow']
            for i in range(8):
                alpha = int((80 * math.exp(-i * 0.4)) * self.glow_intensity)
                rads = base_radius * (0.8 + i * 1.2 + 0.1 * math.sin(self.phase * 8 + i))
                p.setBrush(QBrush(QColor(glow_col[0], glow_col[1], glow_col[2], clamp(alpha, 0, 255))))
                p.setPen(Qt.NoPen)
                p.drawEllipse(QPointF(cx, cy), rads, rads)
        
        # Animated rings
        t = self.phase * 2.0 * self.speed
        for i in range(self.rings):
            prog = (t + i * (1.0 / self.rings)) % 1.0
            radius = base_radius + prog * base_radius * 3.2
            thickness = 6 * (1.0 - prog) + 1.0
            alpha = int(220 * (1.0 - prog) * self.glow_intensity)
            
            color = QColor(self.theme['accent'][0], self.theme['accent'][1], self.theme['accent'][2], clamp(alpha, 0, 255))
            pen = QPen(color, thickness)
            pen.setCapStyle(Qt.RoundCap)
            p.setPen(pen)
            
            rectf = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)
            span = int(180 * 16 + math.sin(self.phase * 6 + i) * 30 * 16)
            start = int((self.phase * 360 + i * 40) * 16)
            p.drawArc(rectf, -start, -span)
        
        # Center text
        p.setPen(QColor(220, 240, 255))
        font_name = "Orbitron" if QFontInfo(QFont("Orbitron")).family().lower() == "orbitron" else "Segoe UI"
        p.setFont(QFont(font_name, 28, QFont.Black))
        p.drawText(rect, Qt.AlignCenter, "J.A.R.V.I.S")
        
        # Voice status
        if self.voice_active:
            p.setFont(QFont(font_name, 12, QFont.Bold))
            p.setPen(QColor(self.theme['accent'][0], self.theme['accent'][1], self.theme['accent'][2]))
            status_rect = QRectF(cx - 60, cy + 60, 120, 20)
            p.drawText(status_rect, Qt.AlignCenter, "VOICE ACTIVE")
    
    def animate_step(self, dt=0.016):
        """Animation step"""
        self.phase = (self.phase + dt * 0.12 * self.speed) % 10.0
        self.update()

# --------------------- Main Ultimate HUD ---------------------
class JarvisUltimateHUD(QMainWindow):
    """Main HUD window for Jarvis Ultimate"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("J.A.R.V.I.S ULTIMATE - Voice Assistant HUD")
        self.resize(1400, 900)
        
        self.theme_index = 0
        self.theme_key = THEME_ORDER[self.theme_index]
        
        self.setup_ui()
        self.setup_voice_integration()
        self.setup_timers()
        
        self.append_console("[JARVIS ULTIMATE] All systems online. Voice assistant ready.")
    
    def setup_ui(self):
        """Setup the user interface"""
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        root = QVBoxLayout(central)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(8)
        
        # Title bar
        title_bar = self.create_title_bar()
        root.addWidget(title_bar)
        
        # Main content grid
        content_grid = QGridLayout()
        content_grid.setSpacing(10)
        root.addLayout(content_grid, 1)
        
        # Left column - Voice & System
        left_column = QVBoxLayout()
        
        # Voice conversation widget
        self.voice_widget = VoiceConversationWidget()
        left_column.addWidget(self.voice_widget, 2)
        
        # System monitor
        self.system_monitor = SystemMonitorWidget()
        left_column.addWidget(self.system_monitor, 1)
        
        left_frame = QFrame()
        left_frame.setLayout(left_column)
        content_grid.addWidget(left_frame, 0, 0, 2, 1)
        
        # Center - Energy Core
        self.energy_core = EnhancedEnergyCore()
        content_grid.addWidget(self.energy_core, 0, 1, 2, 1)
        
        # Right column - Controls & Info
        right_column = QVBoxLayout()
        
        # YouTube controls
        self.youtube_widget = YouTubeControlWidget()
        right_column.addWidget(self.youtube_widget, 1)
        
        # Console
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFixedHeight(200)
        self.console.setStyleSheet("""
            QTextEdit {
                background: rgba(5,10,15,200);
                border: 1px solid rgba(60,120,180,50);
                border-radius: 6px;
                color: #DCECFB;
                font-size: 10px;
                font-family: 'Consolas', monospace;
            }
        """)
        right_column.addWidget(self.console, 1)
        
        # Action buttons
        actions_frame = self.create_actions_frame()
        right_column.addWidget(actions_frame)
        
        right_frame = QFrame()
        right_frame.setLayout(right_column)
        content_grid.addWidget(right_frame, 0, 2, 2, 1)
        
        # Set column stretches
        content_grid.setColumnStretch(0, 1)
        content_grid.setColumnStretch(1, 2)
        content_grid.setColumnStretch(2, 1)
    
    def create_title_bar(self):
        """Create the title bar"""
        title_frame = QFrame()
        title_frame.setStyleSheet("QFrame{background:rgba(8,12,16,200);border-bottom:1px solid rgba(100,140,200,20);}")
        
        layout = QHBoxLayout(title_frame)
        layout.setContentsMargins(10, 6, 10, 6)
        
        # Title
        title_label = QLabel("J.A.R.V.I.S ULTIMATE - Voice Assistant HUD")
        font_name = "Orbitron" if QFontInfo(QFont("Orbitron")).family().lower() == "orbitron" else "Segoe UI"
        title_label.setFont(QFont(font_name, 12, QFont.Bold))
        title_label.setStyleSheet("color:#DDEFFB;")
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # Control buttons
        buttons = [
            ("🎨", "Cycle Theme", self.cycle_theme),
            ("💬", "Toggle Console", self.toggle_console),
            ("🎙️", "Voice Status", self.toggle_voice_mode),
            ("⚙️", "Settings", self.open_settings)
        ]
        
        for icon, tooltip, func in buttons:
            btn = QPushButton(icon)
            btn.setToolTip(tooltip)
            btn.setFixedSize(36, 28)
            btn.setStyleSheet("QPushButton{border-radius:6px;background:rgba(100,140,200,12);}")
            btn.clicked.connect(func)
            layout.addWidget(btn)
        
        return title_frame
    
    def create_actions_frame(self):
        """Create action buttons frame"""
        frame = QFrame()
        frame.setStyleSheet("QFrame { border-radius:8px; background:rgba(10,14,20,220); }")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 8, 8, 8)
        
        title = SectionTitle("Quick Actions")
        layout.addWidget(title)
        
        actions = [
            ("📸 Screenshot", self.take_screenshot),
            ("🎵 Play Music", self.play_music),
            ("🌤️ Get Weather", self.get_weather),
            ("⏰ Current Time", self.get_time),
            ("💻 System Info", self.get_system_info)
        ]
        
        for text, func in actions:
            btn = QPushButton(text)
            btn.setFixedHeight(32)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(60,120,180,30);
                    border: 1px solid rgba(60,200,255,50);
                    border-radius: 6px;
                    color: #DCECFB;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: rgba(60,200,255,50);
                }
                QPushButton:pressed {
                    background: rgba(60,200,255,80);
                }
            """)
            btn.clicked.connect(func)
            layout.addWidget(btn)
        
        return frame
    
    def setup_voice_integration(self):
        """Setup voice assistant integration"""
        self.voice_worker = VoiceAssistantWorker()
        
        # Connect signals
        self.voice_worker.voice_command_received.connect(self.voice_widget.add_command)
        self.voice_worker.voice_response_received.connect(self.voice_widget.add_response)
        self.voice_worker.system_status_updated.connect(self.voice_widget.update_status)
        
        # Voice activity affects energy core
        self.voice_worker.voice_command_received.connect(lambda: self.energy_core.set_voice_active(True))
        self.voice_worker.voice_response_received.connect(lambda: self.energy_core.set_voice_active(False))
    
    def setup_timers(self):
        """Setup update timers"""
        # Animation timer
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.energy_core.animate_step)
        self.anim_timer.start(16)  # 60 FPS
        
        # System stats timer
        self.stats_timer = QTimer(self)
        self.stats_timer.timeout.connect(self.update_system_stats)
        self.stats_timer.start(1000)  # 1 second
        
        # Clock timer
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
    
    def update_system_stats(self):
        """Update system statistics"""
        if psutil:
            try:
                cpu = psutil.cpu_percent()
                memory = psutil.virtual_memory().percent
                disk = psutil.disk_usage('/').percent
                
                # Battery
                try:
                    battery = psutil.sensors_battery()
                    battery_percent = battery.percent if battery else 100
                except:
                    battery_percent = 100
                
                self.system_monitor.update_stats(cpu, memory, disk, battery_percent)
                
                # Network
                try:
                    net = psutil.net_io_counters()
                    # Simple network calculation (you might want to improve this)
                    upload = random.uniform(0, 5)  # Placeholder
                    download = random.uniform(0, 10)  # Placeholder
                    self.system_monitor.update_network(upload, download)
                except:
                    pass
                    
            except Exception as e:
                self.append_console(f"[SYSTEM] Stats error: {e}")
        else:
            # Fake data if psutil not available
            cpu = random.uniform(10, 80)
            memory = random.uniform(30, 70)
            disk = random.uniform(20, 60)
            battery = random.uniform(50, 100)
            self.system_monitor.update_stats(cpu, memory, disk, battery)
    
    def update_clock(self):
        """Update clock and random system messages"""
        if random.random() < 0.05:  # 5% chance per second
            messages = [
                "All systems nominal",
                "Monitoring voice patterns",
                "System optimization complete",
                "Voice recognition active",
                "Neural networks stable"
            ]
            self.append_console(f"[JARVIS] {random.choice(messages)}")
    
    # --------------------- Voice Integration Methods ---------------------
    def simulate_voice_command(self, command):
        """Simulate receiving a voice command (for testing)"""
        self.voice_worker.add_command(command)
        self.append_console(f"[VOICE] Command: {command}")
    
    def simulate_voice_response(self, response):
        """Simulate Jarvis response (for testing)"""
        self.voice_worker.add_response(response)
        self.append_console(f"[JARVIS] Response: {response}")
    
    # --------------------- Action Methods ---------------------
    def take_screenshot(self):
        """Take screenshot action"""
        self.simulate_voice_command("take screenshot")
        self.simulate_voice_response("Screenshot captured successfully, sir!")
    
    def play_music(self):
        """Play music action"""
        self.simulate_voice_command("play music on youtube")
        self.simulate_voice_response("Opening YouTube music, sir!")
        self.youtube_widget.set_now_playing("Random Song - Artist")
    
    def get_weather(self):
        """Get weather action"""
        self.simulate_voice_command("what's the weather")
        self.simulate_voice_response("The weather is 22°C and sunny, sir!")
    
    def get_time(self):
        """Get time action"""
        current_time = datetime.now().strftime("%I:%M %p")
        self.simulate_voice_command("what time is it")
        self.simulate_voice_response(f"The time is {current_time}, sir!")
    
    def get_system_info(self):
        """Get system info action"""
        self.simulate_voice_command("system status")
        self.simulate_voice_response("All systems running optimally, sir!")
    
    # --------------------- UI Control Methods ---------------------
    def cycle_theme(self):
        """Cycle through themes"""
        self.theme_index = (self.theme_index + 1) % len(THEME_ORDER)
        self.theme_key = THEME_ORDER[self.theme_index]
        self.energy_core.set_theme(self.theme_key)
        self.append_console(f"[JARVIS] Theme changed to {self.theme_key.upper()}")
    
    def toggle_console(self):
        """Toggle console visibility"""
        self.console.setVisible(not self.console.isVisible())
        status = "visible" if self.console.isVisible() else "hidden"
        self.append_console(f"[JARVIS] Console {status}")
    
    def toggle_voice_mode(self):
        """Toggle voice mode"""
        self.energy_core.set_voice_active(not self.energy_core.voice_active)
        status = "activated" if self.energy_core.voice_active else "deactivated"
        self.append_console(f"[JARVIS] Voice mode {status}")
    
    def open_settings(self):
        """Open settings dialog"""
        self.append_console("[JARVIS] Settings panel opened")
        # You can implement a settings dialog here
    
    def append_console(self, text):
        """Add text to console"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.append(f"[{timestamp}] {text}")
        # Auto-scroll to bottom
        scrollbar = self.console.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

# --------------------- Main Function ---------------------
def main():
    """Main function to run the GUI"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the HUD
    hud = JarvisUltimateHUD()
    hud.show()
    
    # Demo: Simulate some voice interactions after 2 seconds
    def demo_interactions():
        hud.simulate_voice_command("Hello Jarvis")
        hud.simulate_voice_response("Hello sir! Jarvis Ultimate is ready to assist you!")
        
        QTimer.singleShot(3000, lambda: hud.simulate_voice_command("play believer on youtube"))
        QTimer.singleShot(3500, lambda: hud.simulate_voice_response("Playing Believer on YouTube, sir!"))
        QTimer.singleShot(4000, lambda: hud.youtube_widget.set_now_playing("Believer - Imagine Dragons"))
    
    QTimer.singleShot(2000, demo_interactions)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()