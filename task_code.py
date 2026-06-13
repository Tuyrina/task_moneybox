from datetime import datetime, timedelta
import json 

class Goal:
    def __init__(self, name: str, target_amount: float, category: str, deadline: str=None):
        self.name = name
        self.target_amount = target_amount
        self.category = category
        self.current_balance = 0.0
        self.status = 'В процессе'

        self.deadline = datetime.strptime(deadline, '%Y-%m-%d') if deadline else None
        self.history = []
    def update_status(self):
        if self.current_balance >= self.target_amount and self.status != 'Выполнена':
            self.status = 'Выполнена'
            print(f'Поздравляем! Цель: {self.name} официально достигнута!')
        else:
            self.status = 'В процессе'
    def deposit(self, amount: float, date_str=None):
        if amount <= 0:
            return
        deposit_date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.now()
        if self.current_balance + amount > self.target_amount:
            print(f'Превышение лимита для "{self.name}". Доступно для внесения {self.target_amount - self.current_balance}')
            return
        self.current_balance += amount
        self.history.append((deposit_date, amount))
        self.update_status()
        self.check_milestones()

    def get_progress(self) -> float:
        return round((self.current_balance / self.target_amount) * 100, 2) if self.target_amount > 0 else 0.0
    def check_milestones(self):
        progress = self.get_progress()
        if 50.0 <= progress < 100.0:
            print(f'Прогресс по цели "{self.name}": пройдено более половины пути!({progress}%)')
    def check_deadline_reminder(self):
        if not self.deadline or self.status == "Выполнена":
            return
        days_left = (self.deadline - datetime.now()).days
        if 0 <= days_left <= 3:
            print(f'Внимание! До завершения цели "{self.name}" осталось всего {days_left} дня(ей)!')
        elif days_left < 0:
            print(f'Срок по цели "{self.name}" ИСТЕК на {abs(days_left)} дня(ей) назад!')
    def predict_completion_date(self) -> str:
        if self.status == 'Выполнена':
            return 'Уже выполнена'
        if len(self.history) < 2:
            return 'Недостаточно данных для прогноза (нужно хотя бы два пополнения)'
        total_days = (self.history[-1][0] - self.history[0][0]).days
        if total_days <= 0:
            return 'Недостаточно временных данных для расчета интенсивности'
        total_saved = sum(sum_val for _, sum_val in self.history)
        avg_per_day = total_saved / total_days
        if avg_per_day <= 0:
            return 'Накопления не увеличиваются'
        remaining_amount = self.target_amount - self.current_balance
        days_needed = int(remaining_amount / avg_per_day)
        predicted_date = datetime.now() + timedelta(days=days_needed)
        return predicted_date.strftime('%Y-%m-%d')

class GoalManager:
    def __init__(self):
        self.goals = []
        self.allowed_categories = {"Работа", "Здоровье", "Образование", "Техника", "Отпуск"}
    def add_goal(self, goal: Goal):
        if goal.category in self.allowed_categories:
            self.goals.append(goal)
            print(f'Цель "{goal.name}" добавлена в категорию "{goal.category}"')
        else:
            print(f'Категория "{goal.category}" не поддерживается. Разрешенные: {self.allowed_categories}')
    def remove_goal_by_name(self, name: str):
        for goal in self.goals:
            if goal.name == name:
                self.goals.remove(goal)
                self.save_to_json()
                print(f'Цель "{name}" успешно удалена из системы.')
                return
            print(f'Цель с названием "{name}" не найдена.')
    def get_total_progress(self) -> float:
        if not  self.goals: return 0.0
        total_target = sum(g.target_amount for g in self.goals)
        total_current = sum(g.current_balance for g in self.goals)
        return round((total_current / total_target) * 100, 2) if total_target > 0 else 0.0
    def save_to_json(self, filename: str = "goals.json"):
        data_to_save = []
        for goal in self.goals:
            history_serialized = [
                {"date": date.strftime('%Y-%m-%d'), 'amount': amount}
                for date, amount in goal.history
            ]
            goal_data = {
                "name": goal.name,
                "category": goal.category,
                "target_amount": goal.target_amount,
                "current_balance": goal.current_balance,
                "status": goal.status,
                "deadline": goal.deadline.strftime('%Y-%m-%d') if goal.deadline else None,
                "history": history_serialized
            }
            data_to_save.append(goal_data)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        print(f'Данные успешно сохранены в файл "{filename}"')
    def load_from_json(self, filename: str = 'goals.json'):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.goals = []
            for item in data:
                goal = Goal(
                    name=item["name"],
                    target_amount=item["target_amount"],
                    category=item["category"],
                    deadline=item["deadline"] 
                )
                goal.current_balance = item["current_balance"]
                goal.status = item["status"]
                
                goal.history = [
                    (datetime.datetime.strptime(h["date"], '%Y-%m-%d').date(), h["amount"])
                    for h in item["history"]
                ]
                self.goals.append(goal)
            print(f"Данные успешно загружены из файла '{filename}'. Восстановлено целей: {len(self.goals)}")
        except FileNotFoundError:
            print(f"Файл '{filename}' не найден. Начинаем с пустого списка.")

manager = GoalManager()

print("--- 1. Создание и Категоризация ---")
laptop_goal = Goal("Купить MacBook", target_amount=150000, category="Техника", deadline="2026-06-30")
manager.add_goal(laptop_goal)

print("\n--- 2. Пополнения и аналитика (Повышенный уровень) ---")
laptop_goal.deposit(30000, date_str="2026-05-01")
laptop_goal.deposit(30000, date_str="2026-05-15")
laptop_goal.deposit(20000, date_str="2026-06-01")

print(f'Текущий прогресс цели: {laptop_goal.get_progress()}%')
print(f'Прогноз даты завершения цели: {laptop_goal.predict_completion_date()}')

print("\n--- 3. Проверка уведомлений и времени ---")
laptop_goal.check_deadline_reminder()

print('/n---Сохранение данных---')
manager.save_to_json('goals.json')
print("\n--- 4. Удаление цели из общего списка ---")
manager.remove_goal_by_name("Купить MacBook")

                

