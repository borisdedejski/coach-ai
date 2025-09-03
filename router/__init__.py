from router.v1.chat import router as chat
from router.v1.progress import router as progress
from router.v1.history import router as history
from router.v1.insights import router as insights
from router.v1.habits import router as habits
from router.v1.conversations import router as conversations

api_routers_v1 = [chat, progress, history, insights, habits, conversations]
