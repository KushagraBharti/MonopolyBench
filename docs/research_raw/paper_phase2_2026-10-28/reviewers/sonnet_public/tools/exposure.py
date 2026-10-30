"""usage: exposure.py GAME SPEAKER_LINE RECIPIENT_PID  -> where the speaker's message sits in the recipient's recorded public timeline."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import add_candidates as A
