from typing import Tuple
from models import UserSession

def decide_reply(sess: UserSession, incoming_text: str) -> Tuple[str, str, dict]:
    t = (incoming_text or "").strip().lower()
    state = sess.state

    if state == "start":
        reply = ("👋 Hi, I’m JibuJob.\n"
                 "Reply:\n"
                 "1️⃣ Jobs\n"
                 "2️⃣ Career Tips")
        return "ask_menu", reply, sess.data

    if state == "ask_menu":
        if t in ("1", "jobs"):
            reply = ("💼 Sample jobs:\n"
                     "• Farm Worker – bit.ly/job1\n"
                     "• Shop Assistant – bit.ly/job2\n"
                     "• Rider – bit.ly/job3\n\n"
                     "Reply 'menu' to go back.")
            return "show_jobs", reply, sess.data
        if t in ("2", "career tips", "tips"):
            reply = "💡 Tip: Tailor your CV to the job ad. Reply 'menu' to go back."
            return "show_tips", reply, sess.data
        reply = "🙏 I didn’t get that. Reply 1 for Jobs or 2 for Tips."
        return "ask_menu", reply, sess.data

    if t in ("menu", "back", "start"):
        reply = ("🏠 Main Menu:\n"
                 "1️⃣ Jobs\n"
                 "2️⃣ Career Tips")
        return "ask_menu", reply, sess.data

    # default fallback
    return state, "Sorry, I didn’t get that. Type 'menu' to see options.", sess.data
