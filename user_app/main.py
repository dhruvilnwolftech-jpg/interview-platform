"""
User APK Interface - Interview Document Sharing Platform
Allows users to join sessions with a code and view/edit transparent documents
"""

from kivy.app import App
from kivy.uix.screen import Screen
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.progressbar import ProgressBar

import requests
import socketio
import json
import uuid
from threading import Thread
from PIL import Image as PILImage
from io import BytesIO
import base64

# Window size for development (ignore for APK)
Window.size = (360, 800)

# ==================== SOCKET.IO CLIENT ====================

sio = socketio.Client()
SERVER_URL = 'http://localhost:5000'  # Change to your server IP


class SocketIOManager:
    """Manages WebSocket connections"""
    
    def __init__(self, callback):
        self.callback = callback
        self.user_id = str(uuid.uuid4())
        self.setup_socket_events()
    
    def setup_socket_events(self):
        """Setup Socket.IO event handlers"""
        
        @sio.event
        def connect():
            self.callback('socket_connected', {})
        
        @sio.event
        def disconnect():
            self.callback('socket_disconnected', {})
        
        @sio.on('connection_response')
        def on_connection_response(data):
            self.callback('connection_response', data)
        
        @sio.on('register_response')
        def on_register_response(data):
            self.callback('register_response', data)
        
        @sio.on('document_updated')
        def on_document_updated(data):
            self.callback('document_updated', data)
        
        @sio.on('sync_response')
        def on_sync_response(data):
            self.callback('sync_response', data)
        
        @sio.on('user_connected')
        def on_user_connected(data):
            self.callback('user_connected', data)
        
        @sio.on('user_disconnected')
        def on_user_disconnected(data):
            self.callback('user_disconnected', data)
    
    def connect(self):
        """Connect to server"""
        try:
            sio.connect(SERVER_URL)
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from server"""
        if sio.connected:
            sio.disconnect()
    
    def register(self, session_id):
        """Register user in session"""
        sio.emit('register', {
            'user_id': self.user_id,
            'user_type': 'user',
            'session_id': session_id
        })
    
    def send_document_change(self, session_id, document_id, change_type, new_value, old_value=''):
        """Send document change to server"""
        sio.emit('document_change', {
            'session_id': session_id,
            'document_id': document_id,
            'change_type': change_type,
            'new_value': new_value,
            'old_value': old_value,
            'user_id': self.user_id
        })
    
    def request_sync(self, session_id, document_id):
        """Request document sync"""
        sio.emit('request_sync', {
            'session_id': session_id,
            'document_id': document_id
        })


# ==================== LOGIN SCREEN ====================

class LoginScreen(Screen):
    """Code entry screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'login'
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Title
        title = Label(
            text='[b]Interview Session[/b]',
            font_size='32sp',
            markup=True,
            size_hint_y=0.2
        )
        layout.add_widget(title)
        
        # Instructions
        instructions = Label(
            text='Enter the 6-digit code provided by\nthe interview support person',
            font_size='14sp',
            size_hint_y=0.15
        )
        layout.add_widget(instructions)
        
        # Code input
        self.code_input = TextInput(
            multiline=False,
            hint_text='Enter 6-digit code',
            input_filter='alphanumeric',
            font_size='20sp',
            size_hint_y=0.1
        )
        layout.add_widget(self.code_input)
        
        # Status label
        self.status_label = Label(
            text='',
            font_size='12sp',
            size_hint_y=0.1,
            color=(1, 0, 0, 1)
        )
        layout.add_widget(self.status_label)
        
        # Join button
        join_btn = Button(
            text='Join Session',
            size_hint_y=0.15,
            background_color=(0.2, 0.6, 0.8, 1)
        )
        join_btn.bind(on_press=self.verify_code)
        layout.add_widget(join_btn)
        
        # Loading progress bar
        self.progress = ProgressBar(size_hint_y=0.1)
        layout.add_widget(self.progress)
        
        self.add_widget(layout)
    
    def verify_code(self, instance):
        """Verify session code with backend"""
        code = self.code_input.text.strip().upper()
        
        if not code or len(code) < 6:
            self.status_label.text = 'Please enter a valid code'
            return
        
        self.status_label.text = 'Verifying...'
        self.progress.value = 50
        
        # Verify on server
        try:
            response = requests.get(
                f'{SERVER_URL}/api/sessions/{code}',
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                # Pass data to document screen
                doc_screen = self.manager.get_screen('document')
                doc_screen.session_id = data['session_id']
                doc_screen.document_id = data['document_id']
                doc_screen.support_person_id = data['support_person_id']
                doc_screen.initialize_connection()
                
                self.manager.transition = FadeTransition()
                self.manager.current = 'document'
            else:
                self.status_label.text = 'Invalid code or session inactive'
                self.progress.value = 0
        
        except Exception as e:
            self.status_label.text = f'Error: {str(e)}'
            self.progress.value = 0


# ==================== DOCUMENT SCREEN ====================

class TransparentTextInput(TextInput):
    """Custom text input with transparency"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (1, 1, 1, 0)  # Transparent
        self.foreground_color = (0, 0, 0, 1)


class DocumentScreen(Screen):
    """Document editing screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'document'
        
        self.session_id = None
        self.document_id = None
        self.support_person_id = None
        self.socket_manager = None
        self.bg_color = (1, 1, 1, 1)
        self.font_color = (0, 0, 0, 1)
        self.font_size = 14
        self.opacity = 1.0
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Top toolbar
        toolbar = BoxLayout(size_hint_y=0.08, spacing=5)
        
        # Document info
        self.info_label = Label(
            text='Connected',
            font_size='12sp',
            size_hint_x=0.6
        )
        toolbar.add_widget(self.info_label)
        
        # Settings button
        settings_btn = Button(
            text='Settings',
            size_hint_x=0.2,
            background_color=(0.2, 0.6, 0.8, 1)
        )
        settings_btn.bind(on_press=self.open_settings)
        toolbar.add_widget(settings_btn)
        
        # Disconnect button
        disconnect_btn = Button(
            text='Exit',
            size_hint_x=0.2,
            background_color=(0.8, 0.2, 0.2, 1)
        )
        disconnect_btn.bind(on_press=self.disconnect)
        toolbar.add_widget(disconnect_btn)
        
        main_layout.add_widget(toolbar)
        
        # Transparent document editor
        self.text_editor = TransparentTextInput(
            multiline=True,
            size_hint_y=0.92,
            font_size=f'{self.font_size}sp'
        )
        self.text_editor.bind(text=self.on_text_change)
        
        main_layout.add_widget(self.text_editor)
        
        self.add_widget(main_layout)
    
    def initialize_connection(self):
        """Initialize WebSocket connection"""
        self.socket_manager = SocketIOManager(self.handle_socket_event)
        
        # Connect in background thread
        thread = Thread(target=self._connect_thread)
        thread.daemon = True
        thread.start()
    
    def _connect_thread(self):
        """Connect to server in background"""
        if self.socket_manager.connect():
            self.socket_manager.register(self.session_id)
            self.socket_manager.request_sync(self.session_id, self.document_id)
    
    def handle_socket_event(self, event_type, data):
        """Handle WebSocket events"""
        Clock.schedule_once(lambda dt: self._handle_socket_event(event_type, data))
    
    def _handle_socket_event(self, event_type, data):
        """Handle WebSocket events on main thread"""
        if event_type == 'socket_connected':
            self.info_label.text = 'Connecting...'
        
        elif event_type == 'socket_disconnected':
            self.info_label.text = 'Disconnected'
        
        elif event_type == 'register_response':
            self.info_label.text = f"Connected as User"
        
        elif event_type == 'sync_response':
            # Update UI with document state
            self.text_editor.text = data.get('content', '')
            self.bg_color = self.hex_to_rgb(data.get('bg_color', '#FFFFFF'))
            self.font_color = self.hex_to_rgb(data.get('font_color', '#000000'))
            self.font_size = data.get('font_size', 14)
            self.opacity = data.get('opacity', 1.0)
            self.apply_styles()
        
        elif event_type == 'document_updated':
            if data.get('change_type') == 'text_edit':
                # Update text (avoid re-triggering on_text_change)
                self.text_editor.text = data.get('new_value', '')
            elif data.get('change_type') == 'style_change':
                changes = data.get('new_value', {})
                for key, value in changes.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
                self.apply_styles()
        
        elif event_type == 'user_connected':
            active_count = data.get('active_users', 0)
            self.info_label.text = f"Connected • {active_count} user(s)"
    
    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4)) + (1,)
    
    def on_text_change(self, instance, value):
        """Handle text changes"""
        if self.socket_manager and self.document_id:
            self.socket_manager.send_document_change(
                self.session_id,
                self.document_id,
                'text_edit',
                value
            )
    
    def apply_styles(self):
        """Apply current styles to document"""
        with self.text_editor.canvas.before:
            Color(*self.bg_color)
            Rectangle(size=self.text_editor.size, pos=self.text_editor.pos)
        
        self.text_editor.foreground_color = self.font_color
        self.text_editor.font_size = f'{self.font_size}sp'
    
    def open_settings(self, instance):
        """Open document settings"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Font size
        content.add_widget(Label(text='Font Size:', size_hint_y=0.1))
        font_size_input = TextInput(
            text=str(self.font_size),
            input_filter='int',
            multiline=False,
            size_hint_y=0.1
        )
        content.add_widget(font_size_input)
        
        # Opacity
        content.add_widget(Label(text='Opacity:', size_hint_y=0.1))
        opacity_input = TextInput(
            text=str(self.opacity),
            input_filter='float',
            multiline=False,
            size_hint_y=0.1
        )
        content.add_widget(opacity_input)
        
        # Background color
        content.add_widget(Label(text='Background Color (hex):', size_hint_y=0.1))
        bg_color_input = TextInput(
            text='#FFFFFF',
            multiline=False,
            size_hint_y=0.1
        )
        content.add_widget(bg_color_input)
        
        # Font color
        content.add_widget(Label(text='Font Color (hex):', size_hint_y=0.1))
        font_color_input = TextInput(
            text='#000000',
            multiline=False,
            size_hint_y=0.1
        )
        content.add_widget(font_color_input)
        
        # Apply button
        apply_btn = Button(text='Apply', size_hint_y=0.15)
        content.add_widget(apply_btn)
        
        popup = Popup(
            title='Document Settings',
            content=content,
            size_hint=(0.9, 0.7)
        )
        
        def apply_settings(btn):
            try:
                self.font_size = int(font_size_input.text)
                self.opacity = float(opacity_input.text)
                self.bg_color = self.hex_to_rgb(bg_color_input.text)
                self.font_color = self.hex_to_rgb(font_color_input.text)
                self.apply_styles()
                
                # Send to server
                if self.socket_manager:
                    self.socket_manager.send_document_change(
                        self.session_id,
                        self.document_id,
                        'style_change',
                        {
                            'font_size': self.font_size,
                            'opacity': self.opacity,
                            'bg_color': bg_color_input.text,
                            'font_color': font_color_input.text
                        }
                    )
                popup.dismiss()
            except ValueError:
                pass
        
        apply_btn.bind(on_press=apply_settings)
        popup.open()
    
    def disconnect(self, instance):
        """Disconnect from session"""
        if self.socket_manager:
            self.socket_manager.disconnect()
        self.manager.current = 'login'


# ==================== MAIN APP ====================

class UserApp(App):
    """Main application"""
    
    def build(self):
        # Create screen manager
        sm = ScreenManager(transition=FadeTransition())
        
        # Add screens
        sm.add_widget(LoginScreen())
        sm.add_widget(DocumentScreen())
        
        return sm


if __name__ == '__main__':
    UserApp().run()
