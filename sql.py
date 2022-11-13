import sqlite3


class Database:
    def __init__(self, path_to_db="main.db"):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()
        connection = self.connection
        # connection.set_trace_callback(db_logger)
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)

        if commit:
            connection.commit()
        if fetchall:
            data = cursor.fetchall()
        if fetchone:
            data = cursor.fetchone()
        connection.close()
        return data

    def cr_table_applicants(self):
        sql = """
        CREATE TABLE applicants (
            user_id INTEGER PRIMARY KEY,
            join_date TEXT,
            username TEXT,
            firstname TEXT,
            lastname TEXT,
            wr_firstname TEXT,
            wr_lastname TEXT,
            direction TEXT,
            profile TEXT,
            institution TEXT,
            grad_year INTEGER,
            empl_region TEXT,
            hobby TEXT,
            topics TEXT,
            topics_details TEXT,
            status TEXT,
            photo TEXT
            );
"""
        self.execute(sql, commit=True)

    def cr_table_experts(self):
        sql = """
        CREATE TABLE experts (
            user_id INTEGER PRIMARY KEY,
            join_date TEXT,
            username TEXT,
            firstname TEXT,
            lastname TEXT,
            wr_fullname TEXT,
            direction TEXT,
            division TEXT,
            wr_division TEXT,
            position TEXT,
            profile TEXT,
            slots TEXT,
            topics TEXT,
            wr_username TEXT,
            status TEXT,
            photo TEXT
            );
"""
        self.execute(sql, commit=True)

    def cr_table_meetings(self):
        sql = """
        CREATE TABLE meetings (
            meeting_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            expert TEXT,
            applicant TEXT,
            meeting_date TEXT,
            status TEXT,
            link TEXT,
            expert_fb INTEGER,
            applicant_fb INTEGER,
            notifications_ids TEXT
            );
"""
        self.execute(sql, commit=True)

    def cr_table_admins(self):
        sql = """
        CREATE TABLE admins (
            admin_id INTEGER PRIMARY KEY
            );
"""
        self.execute(sql, commit=True)

    def cr_table_stats(self):
        sql = """
        CREATE TABLE stats (
            role TEXT,
            total_pressed INTEGER DEFAULT 0
            );
"""
        self.execute(sql, commit=True)

    def cr_table_local_contacts(self):
        sql = """
        CREATE TABLE local_contacts (
            init_by INTEGER,
            second_user INTEGER,
            status TEXT
            );
    """
        self.execute(sql, commit=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def add_new_column(self, table, column, data_type):
        sql = f"""
        ALTER TABLE {table}
        ADD {column} {data_type};
        """
        return self.execute(sql, commit=True)

    def add_expert(self, user_id, join_date, username, firstname, lastname):
        sql = f"""
        INSERT INTO experts(user_id, join_date, username, firstname, lastname) VALUES(?, ?, ?, ?, ?)
        """
        return self.execute(sql, parameters=(user_id, join_date, username, firstname, lastname), commit=True)

    def add_applicant(self, user_id, join_date, username, firstname, lastname):
        sql = f"""
        INSERT INTO applicants(user_id, join_date, username, firstname, lastname) VALUES(?, ?, ?, ?, ?)
        """
        return self.execute(sql, parameters=(user_id, join_date, username, firstname, lastname), commit=True)

    def add_admin(self, admin_id):
        sql = f"""
        INSERT INTO admins(admin_id) VALUES({admin_id})
        """
        return self.execute(sql, commit=True)

    def add_initial_stats(self):
        sql = f"""
        INSERT INTO stats(role) 
        VALUES('experts'), ('applicants');
        """
        return self.execute(sql, commit=True)

    def add_local_contact(self, init_by, second_user, status):
        sql = f"""
        INSERT INTO local_contacts(init_by, second_user, status) VALUES(?, ?, ?)
        """
        return self.execute(sql, parameters=(init_by, second_user, status), commit=True)

    def get_admins(self):
        sql = f"""
        SELECT * FROM admins
        """
        return self.execute(sql, fetchall=True)

    def update_user(self, table, column, user_id, data):
        sql = f'''
        UPDATE {table} SET {column}=? WHERE user_id={user_id}
        '''
        return self.execute(sql, parameters=(data,), commit=True)

    def remove_user(self, table, user_id):
        sql = f'''
        DELETE FROM {table} WHERE user_id={user_id};
        '''
        return self.execute(sql, commit=True)

    def update_meeting(self, column, meeting_id, data):
        sql = f'''
        UPDATE meetings SET {column}=? WHERE meeting_id={meeting_id}
        '''
        return self.execute(sql, parameters=(data,), commit=True)

    def get_applicant(self, user_id):
        sql = f'''
        SELECT * FROM applicants WHERE user_id={user_id}
        '''
        return self.execute(sql, fetchone=True)

    def get_expert(self, user_id):
        sql = f'''
        SELECT * FROM experts WHERE user_id={user_id}
        '''
        return self.execute(sql, fetchone=True)

    def get_experts_to_confirm(self):
        sql = f'''
        SELECT * FROM experts WHERE status = 'На модерации'
        '''
        return self.execute(sql, fetchall=True)

    def get_experts(self):
        sql = f'''
        SELECT * FROM experts
        '''
        return self.execute(sql, fetchall=True)

    def get_applicants(self):
        sql = f'''
        SELECT * FROM applicants
        '''
        return self.execute(sql, fetchall=True)

    def get_inactive_applicants(self):
        sql = f'''
        SELECT user_id FROM applicants WHERE status is NULL
        '''
        return self.execute(sql, fetchall=True)

    def get_applicant_meetings(self, user_id):
        sql = f'''
        SELECT * FROM meetings 
        WHERE applicant={user_id} AND 
        status NOT IN ("Отменена экспертом", "Отменена соискателем", "Отклонена соискателем", 
        "Отклонена экспертом", "Состоялась", "Отменена")
        '''
        return self.execute(sql, fetchall=True)

    def get_expert_meetings(self, user_id):
        sql = f'''
        SELECT * FROM meetings 
        WHERE expert={user_id} AND 
        status NOT IN ("Отменена экспертом", "Отменена соискателем", "Отклонена соискателем", 
        "Отклонена экспертом", "Состоялась", "Отменена")
        '''
        return self.execute(sql, fetchall=True)

    def add_meeting(self, date, expert_id, applicant_id, slot, status):
        sql = f"""
        INSERT INTO meetings(date, expert, applicant, meeting_date, status) 
        VALUES('{date}', {expert_id}, {applicant_id}, '{slot}', '{status}')
        """
        return self.execute(sql, commit=True)

    def get_meeting(self, meeting_id):
        sql = f'''
        SELECT * FROM meetings WHERE meeting_id={meeting_id}
        '''
        return self.execute(sql, fetchone=True)

    def get_last_insert_meeting_id(self, expert_id, applicant_id):
        sql = f'''
        SELECT MAX(meeting_id) FROM meetings WHERE expert={expert_id} AND applicant={applicant_id};
        '''
        return self.execute(sql, fetchone=True)

    def get_stats(self):
        sql = '''
        SELECT * FROM stats;
        '''
        return self.execute(sql, fetchall=True)

    def update_stat(self, role):
        sql = f'''
        UPDATE stats SET total_pressed=total_pressed+1 WHERE role='{role}';
        '''
        return self.execute(sql, commit=True)

    def get_meeting_fb_e(self):
        sql = f'''
        SELECT * FROM meetings WHERE expert_fb="Ожидает отзыва" ORDER BY 1 DESC LIMIT 1
        '''
        return self.execute(sql, fetchone=True)

    def delete_user(self, table, user_id):
        sql = f'''
        DELETE FROM {table} WHERE user_id={user_id};
        '''
        return self.execute(sql, commit=True)

    def get_meeting_fb_a(self):
        sql = f'''
        SELECT * FROM meetings WHERE applicant_fb="Ожидает отзыва" ORDER BY 1 DESC LIMIT 1
        '''
        return self.execute(sql, fetchone=True)

    def remove_job(self, job_id):
        sql = f'''
        DELETE FROM apscheduler_jobs WHERE id="{job_id}";
        '''
        return self.execute(sql, commit=True)

    def transfer_data(self, user_id, join_date, username, firstname, lastname, wr_firstname, wr_lastname, direction,
                      profile,
                      institution, grad_year, empl_region, hobby, topics, topics_details, status):
        sql = f'''
        INSERT INTO applicants(user_id, join_date, username, firstname, lastname, wr_firstname, wr_lastname, direction, profile,
        institution, grad_year, empl_region, hobby, topics, topics_details, status)
        VALUES(NULLIF(?, ''),NULLIF(?, ''),NULLIF(?, ''),NULLIF(?, ''),
        NULLIF(?, ''),NULLIF(?, ''),NULLIF(?, ''),NULLIF(?, ''),NULLIF(?, ''),NULLIF(?, ''),NULLIF(?, ''),
        NULLIF(?, ''),NULLIF(?, ''),NULLIF(?, ''),NULLIF(?, ''), NULLIF(?, ''))
        '''
        return self.execute(sql, parameters=(
        user_id, join_date, username, firstname, lastname, wr_firstname, wr_lastname, direction, profile,
        institution, grad_year, empl_region, hobby, topics, topics_details, status), commit=True)
