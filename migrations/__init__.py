from glob import glob
from pathlib import Path

from sqlalchemy import (
    TextClause,
    text,
)
from sqlalchemy.orm import sessionmaker

from config import migrations_folder
from database import Migration
from logger import logger


__all__ = (
    "run_migrations",
)


class MigrationError(Exception):
    pass


def _read_migration(filepath: Path) -> TextClause:
    statements = []
    with open(filepath, encoding='utf-8') as file:
        for line in file.readlines():
            statements.append(line)

    return text('\n'.join(statements))


def run_migrations(s: sessionmaker, db_folder: str) -> None:
    with s.begin() as session:
        session.execute(
            text(
                '''
                CREATE TABLE IF NOT EXISTS _migration (
                    id SERIAL,
                    version INTEGER DEFAULT 0
                );
                '''
            )
        )
        migration_record = session.query(Migration).first()
        if migration_record is None:
            session.add(Migration())
            migration_record = session.query(Migration).first()
        current_version = migration_record.version

        unused_migrations = []
        for migration in glob(str(Path(migrations_folder, db_folder, f'{"[0-9]" * 3}.sql'))):
            version = int(Path(migration).stem)
            if version > current_version:
                unused_migrations.append(version)

        if unused_migrations:
            unused_migrations.sort()
            expected_migrations = [i for i in range(current_version + 1, unused_migrations[-1] + 1)]
            if len(expected_migrations) != len(unused_migrations):
                raise MigrationError(
                    'Found missing migration versions: '
                    f'{", ".join(sorted(map(str, set(expected_migrations) - set(unused_migrations))))}.'
                )

            for version in unused_migrations:
                filepath = Path(migrations_folder, db_folder, f'{str(version).rjust(3, "0")}.sql')
                session.execute(_read_migration(filepath))

                logger.debug(f'Executed migration {filepath}')
                migration_record.version += 1