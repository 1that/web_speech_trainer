from app.localisation import *
from ..criterion_base import BaseCriterion
from ..criterion_result import CriterionResult
from ..utils import get_fillers_number_without_slides


class FillersRatioWithoutSlidesCriterion(BaseCriterion):

    PARAMETERS = dict(
        fillers=list.__name__
    )

    def __init__(self, parameters, dependent_criteria, name=''):
        if 'fillers' not in parameters:
            raise ValueError(
                'parameters should contain {}.'.format('fillers'))
    
        super().__init__(
            name=name,
            parameters=parameters,
            dependent_criteria=dependent_criteria,
        )

    @property
    def description(self):
        return {
        "Критерий": t(self.name),
        "Описание":t(f"проверяет, что в речи нет слов-паразитов, используются слова из списка {self.parameters['fillers']}"),
        "Оценка":t("(1 - доля слов-паразитов)")
        } 


    def apply(self, audio, presentation, training_id, criteria_results):
        total_words = audio.audio_stats['total_words']
        if total_words == 0:
            return CriterionResult(1)
        
        fillers = self.parameters['fillers']
        fillers_number = get_fillers_number_without_slides(fillers, audio)
        fillers_ratio = fillers_number / total_words

        if fillers_ratio > 0.5:
            verdict = t(f"Слишком много слов-паразитов: {fillers_number} из {total_words} слов.")
        elif fillers_number > 0:
            verdict = t(f"В речи присутствуют слова-паразиты: {fillers_number} из {total_words} слов.")
        else:
            verdict = t("В речи отсутствуют слова-паразиты.")

        return CriterionResult(
            result=(1 - fillers_ratio),
            verdict=verdict
        )
