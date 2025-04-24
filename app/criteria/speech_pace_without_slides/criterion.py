from bson import ObjectId
import time

from app.audio import Audio
from app.localisation import *
from app.presentation import Presentation
from ..criterion_base import BaseCriterion
from ..criterion_result import CriterionResult
from ..utils import get_proportional_result


class SpeechPaceWithoutSlidesCriterion(BaseCriterion):

    PARAMETERS = dict(
        minimal_allowed_pace=int.__name__,
        maximal_allowed_pace=int.__name__
    )

    def __init__(self, parameters, dependent_criteria, name=''):
        for parameter in ['minimal_allowed_pace', 'maximal_allowed_pace']:
            if parameter not in parameters:
                raise ValueError(
                    'parameters should contain {}.'.format(parameter))
        super().__init__(
            name=name,
            parameters=parameters,
            dependent_criteria=dependent_criteria,
        )

    @property
    def description(self) -> str:
        return {
                "Критерий": t(self.name),
                "Описание": t(f"проверяет, что скорость речи находится в пределах от {self.parameters['minimal_allowed_pace']} до {self.parameters['maximal_allowed_pace']} слов в минуту"), 
                "Оценка": t(f"оценка: 1, если выполнен, (p / {self.parameters['minimal_allowed_pace']}), если темп p слишком медленный, ({self.parameters['maximal_allowed_pace']} / p), если темп p слишком быстрый")
            }

    def apply(self, audio: Audio, presentation: Presentation, training_id: ObjectId, criteria_results: dict) \
            -> CriterionResult:
        minimal_allowed_pace = self.parameters['minimal_allowed_pace']
        maximal_allowed_pace = self.parameters['maximal_allowed_pace']
        pace = audio.audio_stats['words_per_minute']

        if pace < minimal_allowed_pace:
            verdict = t(f"Скорость речи слишком медленная: {pace} слов в минуту.")
        elif pace > maximal_allowed_pace:
            verdict = t(f"Скорость речи слишком быстрая: {pace} слов в минуту.")
        else:
            verdict = t(f"Скорость речи находится в допустимых пределах: {pace} слов в минуту.")

        return CriterionResult(
            result=get_proportional_result(
                pace, minimal_allowed_pace, maximal_allowed_pace),
            verdict=verdict,
        )