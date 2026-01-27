
"""Chatbot flow for Reflecto: Phase 2C Safety, Pacing, and Permission."""

from typing import List, Dict, Any, Optional, Callable
from . import questions

class ReflectoFlow:
	def __init__(self, user_state: Dict[str, Any]):
		self.user_state = user_state
		self.today_state = {}
		self.asked_questions = []
		self.answered_questions = []
		self.stopped = False
		self.deep_asked = False
		self.deep_agreed = False
		self.energy = self._get_energy()
		self.low_energy = self.energy is not None and self.energy <= 3
		self.medium_or_high_energy = self.energy is not None and self.energy > 3
		self.gentle_closure = None

	def _get_energy(self) -> Optional[int]:
		val = self.user_state.get('energy')
		try:
			return int(val)
		except Exception:
			return None

	def get_next_questions(self) -> List[str]:
		# Use question module logic, but adapt for skip/stop/deep
		qs = questions.get_today_questions(
			previous_state=None,
			today_state=self.today_state,
			user_agrees_deep=self.deep_agreed
		)
		# If low energy, only ask first 2, skip stress/focus
		if self.low_energy:
			qs = qs[:2]
		self.asked_questions = qs
		return qs

	def answer_question(self, question: str, answer: str) -> Optional[str]:
		# Allow skip at any time
		if self._is_skip(answer):
			self.answered_questions.append((question, None))
			return self._gentle_skip_message()
		# Allow stop at any time
		if self._is_stop(answer):
			self.stopped = True
			self.gentle_closure = self._gentle_stop_message()
			return self.gentle_closure
		# Deep question permission
		if self._is_deep_permission(question, answer):
			self.deep_agreed = True
			return "Thank you for your openness. Let's gently reflect on something meaningful."
		self.answered_questions.append((question, answer))
		return None

	def _is_skip(self, answer: str) -> bool:
		return answer.strip().lower() in {"skip", "pass", "not today", "no thanks", "no thank you"}

	def _is_stop(self, answer: str) -> bool:
		return "enough for today" in answer.strip().lower() or "stop" == answer.strip().lower()

	def _is_deep_permission(self, question: str, answer: str) -> bool:
		# Only trigger if deep question is offered and user explicitly agrees
		if not self.medium_or_high_energy:
			return False
		if "something meaningful" in question.lower() or "gently reflect" in question.lower():
			return answer.strip().lower() in {"yes", "sure", "okay", "ok", "let's do it", "i agree", "please"}
		return False

	def _gentle_skip_message(self) -> str:
		return "That's completely fine. We can skip any question—no pressure at all."

	def _gentle_stop_message(self) -> str:
		return (
			"Thank you for reflecting today. Remember, you can pause or stop anytime. "
			"Take care and be gentle with yourself."
		)

	def maybe_add_gentle_closure(self, responses: List[str]) -> List[str]:
		if self.low_energy or self.stopped:
			responses.append(self._gentle_stop_message())
		return responses

def run_reflecto_flow(user_state: Dict[str, Any], answer_callback: Callable[[str], str]) -> List[str]:
	"""
	Main flow runner for Reflecto daily reflection.
	answer_callback: function that takes a question and returns an answer (or skip/stop)
	Returns list of all bot/user exchanges (for test/logging).
	"""
	flow = ReflectoFlow(user_state)
	exchanges = []
	qs_list = flow.get_next_questions()
	for q in qs_list:
		if flow.stopped:
			break
		exchanges.append(q)
		answer = answer_callback(q)
		exchanges.append(answer)
		msg = flow.answer_question(q, answer)
		if msg:
			exchanges.append(msg)
		if flow.stopped:
			break
		# Deep question logic: only once, only if agreed
		if not flow.deep_asked and flow.medium_or_high_energy and not flow.deep_agreed:
			# Offer deep question
			deep_offer = "Would you like to gently reflect on something deeper? (yes/no)"
			exchanges.append(deep_offer)
			deep_answer = answer_callback(deep_offer)
			exchanges.append(deep_answer)
			if flow._is_deep_permission(deep_offer, deep_answer):
				flow.deep_agreed = True
				deep_qs = questions.get_today_questions(
					previous_state=None,
					today_state=flow.today_state,
					user_agrees_deep=True
				)
				# Only add the deep question if not already asked
				for dq in deep_qs:
					if dq not in qs_list:
						exchanges.append(dq)
						deep_response = answer_callback(dq)
						exchanges.append(deep_response)
						flow.answer_question(dq, deep_response)
						break
			flow.deep_asked = True
	# Add gentle closure if needed
	if flow.low_energy or flow.stopped:
		exchanges.append(flow._gentle_stop_message())
	return exchanges

