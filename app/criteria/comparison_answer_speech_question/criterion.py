from bson import ObjectId

from app.root_logger import get_root_logger
from app.localisation import *
from ..criterion_base import BaseCriterion
from ..criterion_result import CriterionResult
from app.audio import Audio
from app.presentation import Presentation
from app.utils import normalize_text, delete_punctuation
from ..text_comparison import SlidesSimilarityEvaluator
import json

logger = get_root_logger('web')


class ComparisonAnswerSpeechQuestionCriterion(BaseCriterion):
    def __init__(self, parameters, dependent_criteria, name=''):
        super().__init__(
            name=name,
            parameters=parameters,
            dependent_criteria=dependent_criteria,
        )
        self.evaluator = SlidesSimilarityEvaluator()
        if 'answer_question_threshold' not in self.parameters:
            self.parameters['answer_question_threshold'] = 0.125

    @property
    def description(self):
        return {
            "Критерий": t(self.name),
            "Описание": t("Проверяет, насколько речь пользователя соответствует заданному вопросу по смыслу. Оценивает схожесть между текстом вопроса и ответом пользователя."),
            "Оценка": t("1, если значение соответствия речи вопросу равно или превышает заданный порог (от 0 до 1), иначе r / порог, где r — значение соответствия речи вопросу.")
        }

    def apply(self, audio: Audio, presentation: Presentation, training_id: ObjectId,
              criteria_results: dict, question: str) -> CriterionResult:
        
        recognized_words = audio.audio_stats['recognized_words']
        user_speech = []

        for w in recognized_words:
            user_speech.append(w.word.value.strip())

        user_speech = " ".join(normalize_text(user_speech))

        question_text = question if question is not None else ""
        question_text = " ".join(normalize_text(question_text.split()))

        self.evaluator.train_model([user_speech, question_text])

        similarity = self.evaluator.evaluate_semantic_similarity(user_speech, question_text)

        score = similarity / self.parameters['answer_question_threshold']

        if score >= 1:
            final_score = 1
            message = "Отлично"
        else:
            final_score = score
            message = f"Следует уделить внимание вопросу {question}"

        return CriterionResult(
            result=final_score,
            verdict=message
        )
