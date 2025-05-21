class Training:
    def __init__(self, 
                 training_id, 
                 audio, 
                 presentation, 
                 criteria_pack, 
                 feedback_evaluator,
                 training_type,
                 question=None):
        self.training_id = training_id
        self.audio = audio
        self.presentation = presentation
        self.criteria_pack = criteria_pack
        self.feedback_evaluator = feedback_evaluator
        self.training_type = training_type
        self.question = question

    def evaluate_feedback(self):
        criteria_results = self.criteria_pack.apply(
            self.audio, 
            self.presentation,
            self.training_id,
            self.training_type,
            self.question)
        return self.feedback_evaluator.evaluate_feedback(criteria_results)

