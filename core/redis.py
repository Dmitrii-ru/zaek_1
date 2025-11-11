import redis
from django.conf import settings


class UserStatsService:
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_USER_STATS['HOST'],
            port=settings.REDIS_USER_STATS['PORT'],
            db=settings.REDIS_USER_STATS['DB'],
            password=settings.REDIS_USER_STATS['PASSWORD'],
            decode_responses=True
        )

    def get_user_key(self, telegram_id):
        return f"user:{telegram_id}:answered_questions"

    def add_correct_answer(self, telegram_id, question_id):
        """Добавляет вопрос в список верно отвеченных"""
        key = self.get_user_key(telegram_id)
        self.redis.sadd(key, question_id)

    def get_answered_questions(self, telegram_id):
        """Возвращает множество верно отвеченных вопросов"""
        key = self.get_user_key(telegram_id)
        return self.redis.smembers(key) or set()




    def reset_user_stats(self, telegram_id):
        """Сбрасывает статистику пользователя"""
        key = self.get_user_key(telegram_id)
        self.redis.delete(key)

    def get_user_score(self, telegram_id):
        """Возвращает количество верно отвеченных вопросов"""
        key = self.get_user_key(telegram_id)
        return self.redis.scard(key)


    def remove_category_questions(self, telegram_id, category_question_ids):
        """Удаляет вопросы по их ID из списка верно отвеченных"""
        if category_question_ids:
            question_ids_str = [qid for qid in category_question_ids]
            key = self.get_user_key(telegram_id)
            if question_ids_str:
                self.redis.srem(key, *question_ids_str)



user_stats_service = UserStatsService()