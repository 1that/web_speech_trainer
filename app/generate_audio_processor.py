import sys
from time import sleep
from app.config import Config
from app.mongo_odm import (QuestionsDBManager, DBManager, 
                           QuestionsToProcessDBManager, 
                           QuestionsDBManager)
from app.tts.silero_tts import SileroTTS
from app.root_logger import get_root_logger

logger = get_root_logger(service_name='generate_audio_processor')


class GenerateAudioProcessor:
    def __init__(self):
        self.silero = SileroTTS(url=Config.c.silero_tts.url)

    def run(self):
        while True:
            try:
                question_id = self._extract_id()
                if not question_id:
                    sleep(10)
                    continue

                question = QuestionsDBManager().get_question(question_id)
                if not question:
                    logger.warning(f"Question with ID {question_id} not found.")
                    continue

                logger.info(f"Processing question with question_id = {question_id}.")
                self._process_question(question)

            except Exception as e:
                logger.error(f"Unknown exception.\n{e}")

    def _extract_id(self):
        question_id = QuestionsToProcessDBManager().extract_question_id_to_process()
        if question_id:
            logger.info(f"Extracted question with question_id = {question_id}.")
        return question_id

    def _process_question(self, question):
        try:
            logger.info(f"Generating audio for question: {question.question}")
            audio_data = self.silero.generate_audio(question.question)

            audio_file_id = DBManager().add_file(audio_data, filename=f"{question}.wav")
            logger.info(f"Audio file saved with ID: {audio_file_id}")

            QuestionsDBManager().update_question_audio_id(question.pk, audio_file_id)

        except Exception as e:
            logger.error(f"Failed to process question '{question.question}': {e}")


if __name__ == "__main__":
    Config.init_config(sys.argv[1])
    generate_audio_processor = GenerateAudioProcessor()
    generate_audio_processor.run()