"""
Admin APK Interface
Real-time monitoring of all interview sessions and documents
"""

from kivy.app import App
from kivy.uix.screen import Screen
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.uix.textinput import TextInput

import requests
import socketio
import json
import uuid
from threading import Thread
from datetime import datetime

Window.size = (360, 800)

# ==================== SOCKET.IO CLIENT ====================

sio = socketio.Client()
SERVER_URL = 'http://localhost:5000'


class SocketIOManager:
    """Manages WebSocket connections for admin"""
    
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
        
        @sio.on('user_connected')
        def on_user_connected(data):
            self.callback('user_connected', data)
        
        @sio.on('user_disconnected')
        def on_user_disconnected(data):
            self.callback('user_disconnected', data)
        
        @sio.on('document_updated')
        def on_document_updated(data):
            self.callback('document_updated', data)
    
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
    
    def register_as_admin(self):
        """Register as admin"""
        sio.emit('register', {
            'user_id': self.user_id,
            'user_type': 'admin',
            'session_id': 'admin'
        })
    
    def join_session(self, session_id):
        """Join a specific session to monitor it"""
        sio.emit('register', {
            'user_id': self.user_id,
            'user_type': 'admin',
            'session_id': session_id
        })


# ==================== DASHBOARD SCREEN ====================

class DashboardScreen(Screen):
    """Admin dashboard showing all sessions"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'dashboard'
        self.socket_manager = None
        self.sessions = {}
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Title
        title = Label(
            text='[b]Admin Dashboard[/b]',
            font_size='28sp',
            markup=True,
            size_hint_y=0.08
        )
        main_layout.add_widget(title)
        
        # Refresh button
        refresh_btn = Button(
            text='Refresh Sessions',
            size_hint_y=0.08,
            background_color=(0.2, 0.6, 0.8, 1)
        )
        refresh_btn.bind(on_press=self.refresh_sessions)
        main_layout.add_widget(refresh_btn)
        
        # Sessions list
        scroll = ScrollView(size_hint=(1, 0.84))
        self.sessions_layout = GridLayout(
            cols=1,
            spacing=10,
            size_hint_y=None,
            padding=5
        )
        self.sessions_layout.bind(minimum_height=self.sessions_layout.setter('height'))
        scroll.add_widget(self.sessions_layout)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
    
    def on_enter(self):
        """Screen entered"""
        if not self.socket_manager:
            self.socket_manager = SocketIOManager(self.handle_socket_event)
            thread = Thread(target=self._connect_thread)
            thread.daemon = True
            thread.start()
    
    def _connect_thread(self):
        """Connect to server"""
        if self.socket_manager.connect():
            self.socket_manager.register_as_admin()
            Clock.schedule_once(lambda dt: self.refresh_sessions(None), 1)
    
    def handle_socket_event(self, event_type, data):
        """Handle WebSocket events"""
        Clock.schedule_once(lambda dt: self._handle_socket_event(event_type, data))
    
    def _handle_socket_event(self, event_type, data):
        """Handle WebSocket events on main thread"""
        if event_type == 'user_connected':
            self.refresh_sessions(None)
        elif event_type == 'document_updated':
            self.refresh_sessions(None)
    
    def refresh_sessions(self, instance):
        """Refresh session list from server"""
        thread = Thread(target=self._fetch_sessions)
        thread.daemon = True
        thread.start()
    
    def _fetch_sessions(self):
        """Fetch sessions from server"""
        try:
            response = requests.get(
                f'{SERVER_URL}/api/admin/sessions',
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                Clock.schedule_once(
                    lambda dt: self._update_sessions_display(data.get('sessions', [])),
                    0
                )
        except Exception as e:
            print(f"Error fetching sessions: {e}")
    
    def _update_sessions_display(self, sessions):
        """Update sessions display"""
        self.sessions_layout.clear_widgets()
        
        if not sessions:
            no_session_label = Label(
                text='No active sessions',
                size_hint_y=None,
                height=50,
                font_size='14sp'
            )
            self.sessions_layout.add_widget(no_session_label)
            return
        
        for session in sessions:
            session_widget = self._create_session_widget(session)
            self.sessions_layout.add_widget(session_widget)
    
    def _create_session_widget(self, session):
        """Create widget for a session"""
        session_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=120,
            padding=10,
            spacing=5
        )
        
        # Background color
        with session_box.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            Rectangle(size=session_box.size, pos=session_box.pos)
        
        # Session code and status
        header = BoxLayout(size_hint_y=0.4, spacing=10)
        code_label = Label(
            text=f"Code: {session['code']}",
            font_size='14sp',
            font_name='monospace',
            size_hint_x=0.6
        )
        header.add_widget(code_label)
        
        status_label = Label(
            text='Active' if session['is_active'] else 'Inactive',
            font_size='12sp',
            color=(0.2, 0.8, 0.2, 1) if session['is_active'] else (0.8, 0.2, 0.2, 1),
            size_hint_x=0.4
        )
        header.add_widget(status_label)
        session_box.add_widget(header)
        
        # Session details
        details_label = Label(
            text=f"Users: {session['connection_count']} | Documents: {session['document_count']}",
            font_size='12sp',
            size_hint_y=0.3
        )
        session_box.add_widget(details_label)
        
        # View button
        view_btn = Button(
            text='View Documents',
            size_hint_y=0.3,
            background_color=(0.2, 0.6, 0.8, 1)
        )
        view_btn.bind(on_press=lambda x: self.view_session(session['id']))
        session_box.add_widget(view_btn)
        
        return session_box
    
    def view_session(self, session_id):
        """View session details"""
        details_screen = self.manager.get_screen('session_details')
        details_screen.session_id = session_id
        details_screen.load_session()
        
        self.manager.transition = FadeTransition()
        self.manager.current = 'session_details'


# ==================== SESSION DETAILS SCREEN ====================

class SessionDetailsScreen(Screen):
    """Detailed view of a specific session"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'session_details'
        self.session_id = None
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Top bar
        top_bar = BoxLayout(size_hint_y=0.08, spacing=10)
        
        back_btn = Button(
            text='← Back',
            size_hint_x=0.3,
            background_color=(0.8, 0.8, 0.8, 1)
        )
        back_btn.bind(on_press=self.go_back)
        top_bar.add_widget(back_btn)
        
        self.session_label = Label(
            text='Session Details',
            font_size='14sp',
            size_hint_x=0.7
        )
        top_bar.add_widget(self.session_label)
        
        main_layout.add_widget(top_bar)
        
        # Documents and connections scrollview
        scroll = ScrollView()
        self.details_layout = GridLayout(
            cols=1,
            spacing=10,
            size_hint_y=None,
            padding=5
        )
        self.details_layout.bind(minimum_height=self.details_layout.setter('height'))
        scroll.add_widget(self.details_layout)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
    
    def load_session(self):
        """Load session details"""
        thread = Thread(target=self._fetch_session_details)
        thread.daemon = True
        thread.start()
    
    def _fetch_session_details(self):
        """Fetch session details from server"""
        try:
            response = requests.get(
                f'{SERVER_URL}/api/sessions/{self.session_id}/connections',
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                Clock.schedule_once(
                    lambda dt: self._display_session_details(data),
                    0
                )
        except Exception as e:
            print(f"Error fetching session details: {e}")
    
    def _display_session_details(self, data):
        """Display session details"""
        self.details_layout.clear_widgets()
        
        # Session info
        active_count = data.get('active_count', 0)
        session_info = Label(
            text=f"Active Connections: {active_count}",
            size_hint_y=None,
            height=40,
            font_size='14sp'
        )
        self.details_layout.add_widget(session_info)
        
        # Connected users
        connections = data.get('all_connections', [])
        for conn in connections:
            conn_widget = self._create_connection_widget(conn)
            self.details_layout.add_widget(conn_widget)
    
    def _create_connection_widget(self, connection):
        """Create widget for a connection"""
        conn_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=80,
            padding=8,
            spacing=4
        )
        
        with conn_box.canvas.before:
            Color(0.9, 0.95, 1, 1)
            Rectangle(size=conn_box.size, pos=conn_box.pos)
        
        # User info
        user_label = Label(
            text=f"User: {connection['user_id'][:8]}... ({connection['user_type']})",
            font_size='12sp',
            size_hint_y=0.4
        )
        conn_box.add_widget(user_label)
        
        # Connection time
        connected_at = connection.get('connected_at', 'Unknown')
        time_label = Label(
            text=f"Connected: {connected_at}",
            font_size='10sp',
            size_hint_y=0.3
        )
        conn_box.add_widget(time_label)
        
        # Status
        if connection.get('disconnected_at'):
            status_label = Label(
                text='Disconnected',
                font_size='10sp',
                color=(0.8, 0.2, 0.2, 1),
                size_hint_y=0.3
            )
        else:
            status_label = Label(
                text='Active',
                font_size='10sp',
                color=(0.2, 0.8, 0.2, 1),
                size_hint_y=0.3
            )
        conn_box.add_widget(status_label)
        
        return conn_box
    
    def go_back(self, instance):
        """Go back to dashboard"""
        self.manager.current = 'dashboard'


# ==================== DOCUMENT VIEW SCREEN ====================

class DocumentViewScreen(Screen):
    """View a specific document with full history"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'document_view'
        self.document_id = None
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Top bar
        top_bar = BoxLayout(size_hint_y=0.08, spacing=10)
        
        back_btn = Button(
            text='← Back',
            size_hint_x=0.3,
            background_color=(0.8, 0.8, 0.8, 1)
        )
        back_btn.bind(on_press=self.go_back)
        top_bar.add_widget(back_btn)
        
        title = Label(text='Document View', size_hint_x=0.7)
        top_bar.add_widget(title)
        main_layout.add_widget(top_bar)
        
        # Document content
        self.doc_label = Label(
            text='Loading...',
            font_size='12sp',
            size_hint_y=0.5
        )
        main_layout.add_widget(self.doc_label)
        
        # History
        scroll = ScrollView(size_hint_y=0.42)
        self.history_layout = GridLayout(
            cols=1,
            spacing=5,
            size_hint_y=None,
            padding=5
        )
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        scroll.add_widget(self.history_layout)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
    
    def on_enter(self):
        """Load document details"""
        if self.document_id:
            self.load_document()
    
    def load_document(self):
        """Load document details"""
        thread = Thread(target=self._fetch_document)
        thread.daemon = True
        thread.start()
    
    def _fetch_document(self):
        """Fetch document from server"""
        try:
            response = requests.get(
                f'{SERVER_URL}/api/admin/documents/{self.document_id}',
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                Clock.schedule_once(
                    lambda dt: self._display_document(data),
                    0
                )
        except Exception as e:
            print(f"Error fetching document: {e}")
    
    def _display_document(self, data):
        """Display document content and history"""
        # Show document content (first 200 chars)
        content = data.get('content', '')[:200]
        self.doc_label.text = f"Content Preview:\n{content}..."
        
        # Show history
        self.history_layout.clear_widgets()
        history = data.get('change_history', [])
        
        for change in history:
            change_label = Label(
                text=f"[{change['timestamp']}] {change['change_type']}",
                size_hint_y=None,
                height=40,
                font_size='11sp'
            )
            self.history_layout.add_widget(change_label)
    
    def go_back(self, instance):
        """Go back to previous screen"""
        self.manager.current = 'session_details'


# ==================== MAIN APP ====================

class AdminApp(App):
    """Main application"""
    
    def build(self):
        # Create screen manager
        sm = ScreenManager(transition=FadeTransition())
        
        # Add screens
        sm.add_widget(DashboardScreen())
        sm.add_widget(SessionDetailsScreen())
        sm.add_widget(DocumentViewScreen())
        
        return sm


if __name__ == '__main__':
    AdminApp().run()
