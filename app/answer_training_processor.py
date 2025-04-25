import sys
from time import sleep

from app.audio import Audio
from app.config import Config
from app.criteria_pack import CriteriaPackFactory
from app.feedback_evaluator import FeedbackEvaluatorFactory
from app.mongo_odm import (CriterionPackDBManager, DBManager, 
                           AnswerTrainingsToProcessDBManager, 
                           AnswerTrainingsDBManager, 
                           AnswerRecordsDBManager,
                           TaskAttemptsDBManager)
from app.training import Training
from app.audio_recognizer import WhisperAudioRecognizer
from app.root_logger import get_root_logger

logger = get_root_logger(service_name='answer_training_processor')


class AnswerTrainingProcessor:
    def run(self):
        while True:
            try:
                training_id = AnswerTrainingsToProcessDBManager().extract_training_id_to_process()
                if not training_id:
                    sleep(10)
                    continue
                logger.info(f'Extracted training with training_id = {training_id}.')

                training_db = AnswerTrainingsDBManager().get_answer_training(training_id)
                if training_db is None:
                    verdict = f'Training with training_id = {training_id} was not found.'
                    AnswerTrainingsDBManager().append_verdict(training_id, verdict)
                    AnswerTrainingsDBManager().set_score(training_id, 0)
                    logger.warning(verdict)
                    continue

                logger.info(f'Processing training with training_id = {training_id}.')

                audio_files = []
                answer_recored_ids = training_db.answer_record_ids

                for answer_record_id in answer_recored_ids:
                    answer_record_db = AnswerRecordsDBManager().get_record(answer_record_id)
                    audio_file = DBManager().get_file(answer_record_db.record_file_id)
                    if audio_file is None:
                        logger.warning(f'Audio file with record_id = {answer_record_db.record_file_id} not found for training_id = {training_id}.')
                        continue
                    audio_files.append(audio_file)

                audio_recognizer = WhisperAudioRecognizer(url=Config.c.whisper.url)
                
                criteria_pack_id = training_db.criteria_pack_id
                criteria_pack = CriteriaPackFactory().get_criteria_pack(criteria_pack_id)
                criteria_pack_db = CriterionPackDBManager().get_criterion_pack_by_name(criteria_pack.name)

                feedback_evaluator_id = training_db.feedback_evaluator_id
                feedback_evaluator = FeedbackEvaluatorFactory().get_feedback_evaluator(feedback_evaluator_id)(criteria_pack_db.criterion_weights)

                total_score = 0
                for audio_file in audio_files:
                    recognized_audio = audio_recognizer.recognize(audio_file)

                    logger.info(f'Successful audio recognized:')

                    audio = Audio(
                        recognized_audio=recognized_audio,
                        training_type='answer'
                    )

                    training = Training(
                        training_id=training_id,
                        audio=audio,
                        presentation=None,
                        criteria_pack=criteria_pack,
                        feedback_evaluator=feedback_evaluator,
                        training_type='answer_training',
                    )

                    try:
                        feedback = training.evaluate_feedback()
                        logger.info(f'Feedback score for current audio: {feedback.score}.')
                        total_score += feedback.score
                    except Exception as e:
                        verdict = f'Feedback evaluation for a training with training_id = {training_id} has failed.\n{e}'
                        AnswerTrainingsDBManager().append_verdict(training_id, verdict)
                        AnswerTrainingsDBManager().set_score(training_id, 0)
                        logger.warning(verdict)
                        continue

                logger.info(f'Total feedback score: {total_score}.')
                AnswerTrainingsDBManager().set_score(training_id, total_score)
                task_attempt_id = training_db.task_attempt_id
                TaskAttemptsDBManager().update_scores(task_attempt_id, training_id, total_score)
            except Exception as e:
                logger.error(f'Unknown exception.\n{e}')


if __name__ == "__main__":
    import nltk
    nltk.download('stopwords')
    nltk.download('punkt')
    
    Config.init_config(sys.argv[1])
    answer_training_processor = AnswerTrainingProcessor()
    answer_training_processor.run()
