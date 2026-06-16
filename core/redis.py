import redis
from django.conf import settings


# core/redis.py - добавляем новые методы в класс UserStatsService

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

    def get_blocked_key(self, telegram_id):
        """Ключ для хранения заблокированных вопросов"""
        return f"user:{telegram_id}:blocked_questions"

    def get_blocked_until_key(self, telegram_id):
        """Ключ для хранения временных меток блокировки"""
        return f"user:{telegram_id}:blocked_until"

    def add_correct_answer(self, telegram_id, question_id):
        key = self.get_user_key(telegram_id)
        self.redis.sadd(key, question_id)

    def get_answered_questions(self, telegram_id):
        key = self.get_user_key(telegram_id)
        return self.redis.smembers(key) or set()

    def reset_user_stats(self, telegram_id):
        key = self.get_user_key(telegram_id)
        self.redis.delete(key)

    def get_user_score(self, telegram_id):
        key = self.get_user_key(telegram_id)
        return self.redis.scard(key)

    def remove_category_questions(self, telegram_id, category_question_ids):
        if category_question_ids:
            question_ids_str = [qid for qid in category_question_ids]
            key = self.get_user_key(telegram_id)
            if question_ids_str:
                self.redis.srem(key, *question_ids_str)

    # НОВЫЕ МЕТОДЫ ДЛЯ БЛОКИРОВОК:
    def block_question_for_month(self, telegram_id, question_id):
        """Блокирует вопрос на месяц (30 дней)"""
        from datetime import datetime, timedelta

        blocked_key = self.get_blocked_key(telegram_id)
        blocked_until_key = self.get_blocked_until_key(telegram_id)

        block_until = datetime.now() + timedelta(days=30)
        timestamp = int(block_until.timestamp())

        self.redis.hset(blocked_until_key, str(question_id), str(timestamp))
        self.redis.sadd(blocked_key, str(question_id))

        return block_until

    def get_blocked_questions(self, telegram_id):
        """Возвращает множество ID заблокированных вопросов"""
        blocked_key = self.get_blocked_key(telegram_id)
        return self.redis.smembers(blocked_key) or set()

    def get_blocked_with_expiry(self, telegram_id):
        """Возвращает словарь {question_id: timestamp_разблокировки}"""
        blocked_until_key = self.get_blocked_until_key(telegram_id)
        blocked_data = self.redis.hgetall(blocked_until_key) or {}

        from datetime import datetime
        current_timestamp = int(datetime.now().timestamp())

        expired_questions = []
        for qid, timestamp in blocked_data.items():
            if int(timestamp) <= current_timestamp:
                expired_questions.append(qid)

        if expired_questions:
            self.redis.hdel(blocked_until_key, *expired_questions)
            self.redis.srem(self.get_blocked_key(telegram_id), *expired_questions)
            for qid in expired_questions:
                blocked_data.pop(qid, None)

        return blocked_data

    def is_question_blocked(self, telegram_id, question_id):
        """Проверяет, заблокирован ли вопрос для пользователя"""
        blocked_until_key = self.get_blocked_until_key(telegram_id)
        timestamp = self.redis.hget(blocked_until_key, str(question_id))

        if timestamp is None:
            return False

        from datetime import datetime
        if int(timestamp) <= int(datetime.now().timestamp()):
            self.redis.hdel(blocked_until_key, str(question_id))
            self.redis.srem(self.get_blocked_key(telegram_id), str(question_id))
            return False

        return True

    def unblock_all_questions(self, telegram_id):
        """Снимает все блокировки с вопросов пользователя"""
        blocked_key = self.get_blocked_key(telegram_id)
        blocked_until_key = self.get_blocked_until_key(telegram_id)

        blocked_questions = self.redis.smembers(blocked_key)

        if blocked_questions:
            self.redis.delete(blocked_key)
            self.redis.delete(blocked_until_key)
            return len(blocked_questions)

        return 0

    def unblock_question(self, telegram_id, question_id):
        """Снимает блокировку с конкретного вопроса"""
        blocked_key = self.get_blocked_key(telegram_id)
        blocked_until_key = self.get_blocked_until_key(telegram_id)

        self.redis.srem(blocked_key, str(question_id))
        self.redis.hdel(blocked_until_key, str(question_id))


user_stats_service = UserStatsService()