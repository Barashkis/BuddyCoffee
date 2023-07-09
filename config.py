import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from pytz import timezone


load_dotenv()

token = os.getenv('TOKEN')

admins: List[int] = eval(os.getenv('ADMINS', '[]'))

postgres_user = os.getenv('POSTGRES_USER')
postgres_password = os.getenv('POSTGRES_PASSWORD')
postgres_host = os.getenv('POSTGRES_HOST')
postgres_name = os.getenv('POSTGRES_NAME')

zoom_api_key = os.getenv('ZOOM_API_KEY')
zoom_api_secret = os.getenv('ZOOM_API_SECRET')

tz = timezone('Europe/Moscow')

logs_path = Path(Path().resolve(), 'logfile.log')
migrations_folder = 'versions'

meetings_per_page = 9
slots_per_page = 9
users_per_page = 1

directions_list = {
    1: 'Проектирование и строительство',
    2: 'Цифровизация',
    3: 'Экология',
    4: 'Северный и морской путь',
    5: 'Ядерная медицина',
    6: 'Производство',
    7: 'Наука',
    8: 'Новые материалы',
    9: 'Международная деятельность',
    10: 'Атомная и альтернативная энергетика'
}

divisions_list = {
    1: 'Горнодобывающий дивизион',
    2: 'Завершающая стадия жизненного цикла',
    3: 'Изотопный комплекс',
    4: 'Инжиниринг и сооружение',
    5: 'Машиностроительный дивизион',
    6: 'Научный дивизион',
    7: 'Перспективные материалы и технологии',
    8: 'Сбыт и трейдинг',
    9: 'Топливный дивизион',
    10: 'Электроэнергетический дивизион',
    11: 'Энергомашиностроительный дивизион',
    12: 'Ядерный оружейный комплекс',
    13: 'АХО',
    14: 'Дирекция Северного морского пути',
    'other': 'Другой'
}

topics_list = {
    1: 'Построение карьеры и развитие',
    2: 'Профессии и их функциональность',
    3: 'Опыт адаптации в атомной отрасли и наставничество',
    4: 'Текущие проекты',
    5: 'Корпоративные ценности и команда',
    6: 'Мероприятие и поддержка молодежи, начинающих специалистов',
    7: 'О Росатоме',
    8: 'Требуемые hard и soft-скиллы',
    9: 'Возможности для развития'
}

expert_menu_list = {
    'search_applicants': 'Посмотреть анкеты соискателей',
    'expert_meetings': 'Мои встречи',
    'add_photo_e': 'Добавить фото к анкете',
    'change_prof_e': 'Изменить профиль',
    'change_agreement_to_show_contacts': 'Согласие на сообщение контактных данных соискателям'
}

applicant_menu_list = {
    'search_experts': 'Начать поиск специалистов',
    'applicant_meetings': 'Мои встречи',
    'add_photo_a': 'Добавить фото к анкете',
    'change_profile_a': 'Изменить профиль',
    'faq_a': 'FAQ'
}

applicant_profile_list = {
    'change_firstname': 'Имя',
    'change_lastname': 'Фамилия',
    'change_direction': 'Направление',
    'change_profile': 'Опыт',
    'change_institution': 'Учебное заведение',
    'change_grad_year': 'Год окончания',
    'change_empl_region': 'Регион трудоустройства',
    'change_hobby': 'Хобби',
    'change_topics': 'Темы на обсуждение',
    'change_topics_details': 'Вопросы ко встрече',
    'change_profile_a': 'Назад'
}

expert_profile_list = {
    'change_fullname': 'Имя',
    'change_direction': 'Направление',
    'change_division': 'Дивизион',
    'change_profile': 'Опыт',
    'change_topics': 'Темы на обсуждение',
    'change_profile_e': 'Назад'
}
