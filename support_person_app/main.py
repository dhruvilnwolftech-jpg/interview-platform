"""
Interview Support Person APK Interface
Manages document sessions, connects with users, manages document styling
"""

from kivy.app import App
from kivy.uix.screen import Screen
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line
from kivy.clock import Clock
from kivy.uix.progressbar import ProgressBar
from kivy.uix.filechooser import FileChooserListView

import requests
import socketio
import json
import uuid
from threading import Thread
from datetime import datetime
from PIL import Image as PILImage
from io import BytesIO
import base64

Window.size = (360, 800)

# ==================== SOCKET.IO CLIENT ====================

sio = socketio.Client()
SERVER_URL = 'http://localhost:5000'


class SocketIOManager:
    """Manages WebSocket connections for support person"""
    
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
        """Register support person in session"""
        sio.emit('register', {
            'user_id': self.user_id,
            'user_type': 'support_person',
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


# ==================== HOME SCREEN ====================

class HomeScreen(Screen):
    """Home screen to create or view sessions"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'home'
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Title
        title = Label(
            text='[b]Interview Support[/b]',
            font_size='32sp',
            markup=True,
            size_hint_y=0.2
        )
        layout.add_widget(title)
        
        # Create new session button
        create_btn = Button(
            text='Create New Session',
            size_hint_y=0.2,
            background_color=(0.2, 0.6, 0.8, 1)
        )
        create_btn.bind(on_press=self.create_session)
        layout.add_widget(create_btn)
        
        # View sessions button
        view_btn = Button(
            text='View Active Sessions',
            size_hint_y=0.2,
            background_color=(0.4, 0.7, 0.4, 1)
        )
        view_btn.bind(on_press=self.view_sessions)
        layout.add_widget(view_btn)
        
        # Status label
        self.status_label = Label(
            text='',
            font_size='12sp',
            size_hint_y=0.2
        )
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)
    
    def create_session(self, instance):
        """Create new interview session"""
        self.status_label.text = 'Creating session...'
        
        thread = Thread(target=self._create_session_thread)
        thread.daemon = True
        thread.start()
    
    def _create_session_thread(self):
        """Create session on server"""
        try:
            response = requests.post(
                f'{SERVER_URL}/api/sessions',
                json={'support_person_id': str(uuid.uuid4())},
                timeout=5
            )
            
            if response.status_code == 201:
                data = response.json()
                Clock.schedule_once(
                    lambda dt: self._go_to_document(data),
                    0
                )
            else:
                Clock.schedule_once(
                    lambda dt: setattr(self.status_label, 'text', 'Failed to create session'),
                    0
                )
        except Exception as e:
            Clock.schedule_once(
                lambda dt: setattr(self.status_label, 'text', f'Error: {str(e)}'),
                0
            )
    
    def _go_to_document(self, session_data):
        """Navigate to document screen"""
        doc_screen = self.manager.get_screen('document')
        doc_screen.session_id = session_data['session_id']
        doc_screen.document_id = session_data['document_id']
        doc_screen.session_code = session_data['code']
        doc_screen.initialize_connection()
        
        self.manager.transition = FadeTransition()
        self.manager.current = 'document'
    
    def view_sessions(self, instance):
        """View active sessions"""
        pass  # Implementation for viewing sessions


# ==================== DOCUMENT SCREEN ====================

class SupportPersonDocumentScreen(Screen):
    """Document editing and management screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'document'
        
        self.session_id = None
        self.document_id = None
        self.session_code = None
        self.socket_manager = None
        self.active_users = 0
        self.bg_color = (1, 1, 1, 1)
        self.font_color = (0, 0, 0, 1)
        self.font_size = 14
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Top toolbar
        toolbar = BoxLayout(size_hint_y=0.08, spacing=5)
        
        # Session code display
        self.code_label = Label(
            text='Code: ------',
            font_size='12sp',
            size_hint_x=0.4
        )
        toolbar.add_widget(self.code_label)
        
        # Connection count
        self.connection_label = Label(
            text='Users: 0',
            font_size='12sp',
            size_hint_x=0.3
        )
        toolbar.add_widget(self.connection_label)
        
        # Settings button
        settings_btn = Button(
            text='Settings',
            size_hint_x=0.15,
            background_color=(0.2, 0.6, 0.8, 1)
        )
        settings_btn.bind(on_press=self.open_settings)
        toolbar.add_widget(settings_btn)
        
        # Exit button
        exit_btn = Button(
            text='Exit',
            size_hint_x=0.15,
            background_color=(0.8, 0.2, 0.2, 1)
        )
        exit_btn.bind(on_press=self.exit_session)
        toolbar.add_widget(exit_btn)
        
        main_layout.add_widget(toolbar)
        
        # Document editor with visible background
        self.text_editor = TextInput(
            multiline=True,
            size_hint_y=0.92,
            font_size='14sp',
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1)
        )
        self.text_editor.bind(text=self.on_text_change)
        
        main_layout.add_widget(self.text_editor)
        
        self.add_widget(main_layout)
    
    def initialize_connection(self):
        """Initialize WebSocket connection"""
        self.code_label.text = f'Code: {self.session_code}'
        
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
        if event_type == 'sync_response':
            self.text_editor.text = data.get('content', '')
            self.bg_color = self.hex_to_rgb(data.get('bg_color', '#FFFFFF'))
            self.font_color = self.hex_to_rgb(data.get('font_color', '#000000'))
            self.font_size = data.get('font_size', 14)
            self.apply_styles()
        
        elif event_type == 'document_updated':
            if data.get('change_type') == 'text_edit':
                self.text_editor.text = data.get('new_value', '')
            elif data.get('change_type') == 'style_change':
                changes = data.get('new_value', {})
                for key, value in changes.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
                self.apply_styles()
        
        elif event_type == 'user_connected':
            self.active_users = data.get('active_users', 0)
            self.connection_label.text = f'Users: {self.active_users}'
    
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
        
        # History button
        history_btn = Button(text='View History', size_hint_y=0.15)
        content.add_widget(history_btn)
        
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
                            'bg_color': bg_color_input.text,
                            'font_color': font_color_input.text
                        }
                    )
                popup.dismiss()
            except ValueError:
                pass
        
        apply_btn.bind(on_press=apply_settings)
        
        def view_history(btn):
            self.view_document_history()
        
        history_btn.bind(on_press=view_history)
        popup.open()
    
    def view_document_history(self):
        """View document change history"""
        try:
            response = requests.get(
                f'{SERVER_URL}/api/documents/{self.document_id}/history',
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                changes = data.get('changes', [])
                
                # Create history popup
                content = BoxLayout(orientation='vertical', padding=10, spacing=10)
                
                scroll = ScrollView()
                history_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
                history_layout.bind(minimum_height=history_layout.setter('height'))
                
                for change in changes:
                    timestamp = change.get('timestamp', 'Unknown')
                    change_type = change.get('change_type', 'Unknown')
                    
                    change_label = Label(
                        text=f"[{timestamp}] {change_type}",
                        size_hint_y=None,
                        height=40,
                        font_size='12sp'
                    )
                    history_layout.add_widget(change_label)
                
                scroll.add_widget(history_layout)
                content.add_widget(scroll)
                
                close_btn = Button(text='Close', size_hint_y=0.1)
                content.add_widget(close_btn)
                
                popup = Popup(
                    title='Document History',
                    content=content,
                    size_hint=(0.95, 0.8)
                )
                
                close_btn.bind(on_press=popup.dismiss)
                popup.open()
        except Exception as e:
            print(f"Error viewing history: {e}")
    
    def exit_session(self, instance):
        """Exit session and return to home"""
        if self.socket_manager:
            self.socket_manager.disconnect()
        self.manager.current = 'home'


# ==================== MAIN APP ====================

class SupportPersonApp(App):
    """Main application"""
    
    def build(self):
        # Create screen manager
        sm = ScreenManager(transition=FadeTransition())
        
        # Add screens
        sm.add_widget(HomeScreen())
        sm.add_widget(SupportPersonDocumentScreen())
        
        return sm


if __name__ == '__main__':
    SupportPersonApp().run()
