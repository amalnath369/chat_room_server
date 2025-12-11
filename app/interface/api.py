from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import HTMLResponse
import logging
from ..infrastructure.websocket.handlers import WebSocketHandler
from ..infrastructure.websocket.connection_manager import ConnectionManager
from ..infrastructure.repositories import InMemoryChatRepository
from ..application.use_cases import ChatUseCases
from ..application.services import ChatService
from ..core.config import settings
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(title=settings.app_name)
    
    # Initialize dependencies
    repository = InMemoryChatRepository()
    use_cases = ChatUseCases(repository)
    chat_service = ChatService(use_cases, settings.message_ttl)
    connection_manager = ConnectionManager(chat_service)
    websocket_handler = WebSocketHandler(connection_manager)
    
    # Start cleanup task
    @app.on_event("startup")
    async def startup_event():
        asyncio.create_task(use_cases.cleanup_expired_messages(settings.message_ttl))
    
    @app.get("/")
    async def root():
        return {"message": "WebSocket Chat Server is running"}
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    @app.get("/topics")
    async def list_topics():
        topics = await repository.get_all_topics()
        return {
            "topics": [
                {
                    "name": name,
                    "user_count": topic.user_count,
                    "message_count": len(topic.messages)
                }
                for name, topic in topics.items()
            ]
        }
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for chat"""
        await websocket_handler.handle_websocket(websocket)
    
    @app.get("/client")
    async def client_page():
        """Simple HTML client for testing"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Chat Client</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                input, button { padding: 10px; margin: 5px; }
                #messages { border: 1px solid #ccc; padding: 10px; height: 300px; overflow-y: scroll; }
                .message { margin: 5px 0; }
            </style>
        </head>
        <body>
            <h1>WebSocket Chat Client</h1>
            <div>
                <input type="text" id="username" placeholder="Username">
                <input type="text" id="topic" placeholder="Topic">
                <button onclick="connect()">Connect</button>
            </div>
            <div>
                <input type="text" id="messageInput" placeholder="Type your message" disabled>
                <button onclick="sendMessage()" disabled id="sendBtn">Send</button>
                <button onclick="sendListCommand()" disabled id="listBtn">List Topics</button>
            </div>
            <div id="messages"></div>
            
            <script>
                let ws = null;
                
                function connect() {
                    const username = document.getElementById('username').value;
                    const topic = document.getElementById('topic').value;
                    
                    if (!username || !topic) {
                        alert('Please enter username and topic');
                        return;
                    }
                    
                    ws = new WebSocket(`ws://${window.location.host}/ws`);
                    
                    ws.onopen = function() {
                        ws.send(JSON.stringify({ username, topic }));
                        document.getElementById('messageInput').disabled = false;
                        document.getElementById('sendBtn').disabled = false;
                        document.getElementById('listBtn').disabled = false;
                        addMessage('System: Connected to chat');
                    };
                    
                    ws.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        if (data.type === 'topic_list') {
                            addMessage('Active Topics: ' + data.topics.join(', '));
                        } else if (data.type === 'acknowledgment') {
                            addMessage('System: Message delivered');
                        } else {
                            addMessage(`${data.username}: ${data.message}`);
                        }
                    };
                    
                    ws.onclose = function() {
                        addMessage('System: Disconnected');
                        document.getElementById('messageInput').disabled = true;
                        document.getElementById('sendBtn').disabled = true;
                        document.getElementById('listBtn').disabled = true;
                    };
                }
                
                function sendMessage() {
                    const input = document.getElementById('messageInput');
                    const message = input.value;
                    if (message && ws) {
                        ws.send(message);
                        input.value = '';
                    }
                }
                
                function sendListCommand() {
                    if (ws) {
                        ws.send('/list');
                    }
                }
                
                function addMessage(text) {
                    const messages = document.getElementById('messages');
                    const message = document.createElement('div');
                    message.className = 'message';
                    message.textContent = text;
                    messages.appendChild(message);
                    messages.scrollTop = messages.scrollHeight;
                }
                
                document.getElementById('messageInput').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        sendMessage();
                    }
                });
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    
    return app