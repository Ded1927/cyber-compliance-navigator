import os
from collections.abc import AsyncGenerator, Generator
from uuid import uuid4

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://cyberlaw:cyberlaw_password@db:5432/cyberlaw",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
async_engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    import app.models  # noqa: F401
    from app.services.auth import get_password_hash

    with engine.begin() as connection:
        Base.metadata.create_all(
            bind=connection,
            tables=[
                table
                for table in Base.metadata.sorted_tables
                if table.name not in {"organization_tasks"}
            ],
        )
        connection.execute(
            text("ALTER TABLE legal_acts ADD COLUMN IF NOT EXISTS description TEXT")
        )
        connection.execute(
            text("ALTER TABLE legal_acts ADD COLUMN IF NOT EXISTS official_link VARCHAR(2048)")
        )
        connection.execute(
            text("ALTER TABLE legal_acts ADD COLUMN IF NOT EXISTS date_adopted DATE")
        )
        connection.execute(
            text("ALTER TABLE organization_profiles ADD COLUMN IF NOT EXISTS public_id UUID")
        )
        missing_public_ids = connection.execute(
            text("SELECT id FROM organization_profiles WHERE public_id IS NULL")
        ).scalars()
        for profile_id in missing_public_ids:
            connection.execute(
                text(
                    "UPDATE organization_profiles "
                    "SET public_id = :public_id "
                    "WHERE id = :profile_id"
                ),
                {"public_id": uuid4(), "profile_id": profile_id},
            )
        connection.execute(
            text(
                "ALTER TABLE organization_profiles "
                "ALTER COLUMN public_id SET NOT NULL"
            )
        )
        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS "
                "ix_organization_profiles_public_id "
                "ON organization_profiles (public_id)"
            )
        )
        Base.metadata.create_all(bind=connection)
        connection.execute(
            text(
                "ALTER TABLE roadmap_template_steps "
                "ADD COLUMN IF NOT EXISTS references_text TEXT"
            )
        )
        seed_default_roadmap_catalog(connection)
        seed_test_accounts(connection, get_password_hash)


def seed_test_accounts(connection, hash_password) -> None:
    accounts = [
        {
            "email": "user@cyberlaw.ua",
            "password": "User12345!",
            "is_admin": False,
        },
        {
            "email": "admin@cyberlaw.ua",
            "password": "Admin12345!",
            "is_admin": True,
        },
    ]

    for account in accounts:
        exists = connection.execute(
            text("SELECT 1 FROM users WHERE email = :email"),
            {"email": account["email"]},
        ).first()
        if exists:
            connection.execute(
                text(
                    "UPDATE users "
                    "SET hashed_password = :hashed_password, is_admin = :is_admin "
                    "WHERE email = :email"
                ),
                {
                    "email": account["email"],
                    "hashed_password": hash_password(account["password"]),
                    "is_admin": account["is_admin"],
                },
            )
            continue

        connection.execute(
            text(
                "INSERT INTO users "
                "(email, hashed_password, is_active, is_admin) "
                "VALUES (:email, :hashed_password, true, :is_admin)"
            ),
            {
                "email": account["email"],
                "hashed_password": hash_password(account["password"]),
                "is_admin": account["is_admin"],
            },
        )


def seed_default_roadmap_catalog(connection) -> None:
    template_count = connection.execute(
        text("SELECT COUNT(*) FROM roadmap_template_steps")
    ).scalar_one()
    if template_count:
        return

    legal_acts = {
        "Закон №1882-IX": connection.execute(
            text(
                "INSERT INTO legal_acts "
                "(title, description, official_link, act_type, status) "
                "VALUES (:title, :description, :official_link, 'law', 'active') "
                "RETURNING id"
            ),
            {
                "title": "Закон №1882-IX",
                "description": "Законодавча основа організації кібербезпеки та відповідальності.",
                "official_link": None,
            },
        ).scalar_one(),
        "Наказ №75": connection.execute(
            text(
                "INSERT INTO legal_acts "
                "(title, description, official_link, act_type, status) "
                "VALUES (:title, :description, :official_link, 'order', 'active') "
                "RETURNING id"
            ),
            {
                "title": "Наказ №75",
                "description": "Базові заходи кіберзахисту для об'єктів критичної інфраструктури.",
                "official_link": None,
            },
        ).scalar_one(),
        "Постанова №373": connection.execute(
            text(
                "INSERT INTO legal_acts "
                "(title, description, official_link, act_type, status) "
                "VALUES (:title, :description, :official_link, 'resolution', 'active') "
                "RETURNING id"
            ),
            {
                "title": "Постанова №373",
                "description": "Вимоги щодо захисту інформації та КСЗІ.",
                "official_link": None,
            },
        ).scalar_one(),
    }

    template_rows = [
        {
            "title": "Призначити CISO (Керівника з ІБ)",
            "description": "Визначити відповідальну особу за кібербезпеку та закріпити повноваження наказом.",
            "instructions_text": "Підготуйте наказ про призначення, опишіть повноваження CISO, канали ескалації інцидентів та регулярну звітність керівництву.",
            "references_text": "Закон №1882-IX; внутрішній наказ про розподіл ролей; посадова інструкція відповідального за інформаційну безпеку.",
            "legal_act_id": legal_acts["Закон №1882-IX"],
            "target_org_type": None,
            "target_is_oki_okii": None,
            "target_category": None,
            "target_data_type": None,
            "deadline_days": 30,
        },
        {
            "title": "Розробити політику кібербезпеки",
            "description": "Підготувати та затвердити політику кібербезпеки з правилами управління ризиками, доступом та інцидентами.",
            "instructions_text": "Почніть з політики верхнього рівня: цілі захисту, ролі, правила доступу, резервне копіювання, реагування на інциденти та перегляд політики.",
            "references_text": "Закон №1882-IX; ISO/IEC 27001 як орієнтир; внутрішній регламент управління доступом та інцидентами.",
            "legal_act_id": legal_acts["Закон №1882-IX"],
            "target_org_type": None,
            "target_is_oki_okii": None,
            "target_category": None,
            "target_data_type": None,
            "deadline_days": 60,
        },
        {
            "title": "Впровадити розширені базові заходи кіберзахисту (Наказ №75)",
            "description": "Запровадити посилені організаційні та технічні заходи для об'єктів високої критичності.",
            "instructions_text": "Сформуйте перелік критичних активів, визначте відповідальних, впровадьте контроль доступу, журналювання, резервування, моніторинг та порядок реагування.",
            "references_text": "Наказ №75; профіль базових заходів кіберзахисту; план захисту критичних інформаційних систем.",
            "legal_act_id": legal_acts["Наказ №75"],
            "target_org_type": None,
            "target_is_oki_okii": True,
            "target_category": 1,
            "target_data_type": None,
            "deadline_days": 90,
        },
        {
            "title": "Впровадити розширені базові заходи кіберзахисту (Наказ №75)",
            "description": "Запровадити посилені організаційні та технічні заходи для об'єктів високої критичності.",
            "instructions_text": "Сформуйте перелік критичних активів, визначте відповідальних, впровадьте контроль доступу, журналювання, резервування, моніторинг та порядок реагування.",
            "references_text": "Наказ №75; профіль базових заходів кіберзахисту; план захисту критичних інформаційних систем.",
            "legal_act_id": legal_acts["Наказ №75"],
            "target_org_type": None,
            "target_is_oki_okii": True,
            "target_category": 2,
            "target_data_type": None,
            "deadline_days": 90,
        },
        {
            "title": "Провести незалежний аудит ІБ",
            "description": "Залучити незалежних фахівців для перевірки стану інформаційної безпеки.",
            "instructions_text": "Підготуйте scope аудиту, перелік систем, відповідальних осіб, докази виконання контролів та критерії приймання звіту.",
            "references_text": "Наказ №75; програма аудиту ІБ; звіт незалежного аудиту; план коригувальних дій.",
            "legal_act_id": legal_acts["Наказ №75"],
            "target_org_type": None,
            "target_is_oki_okii": True,
            "target_category": 1,
            "target_data_type": None,
            "deadline_days": 120,
        },
        {
            "title": "Провести незалежний аудит ІБ",
            "description": "Залучити незалежних фахівців для перевірки стану інформаційної безпеки.",
            "instructions_text": "Підготуйте scope аудиту, перелік систем, відповідальних осіб, докази виконання контролів та критерії приймання звіту.",
            "references_text": "Наказ №75; програма аудиту ІБ; звіт незалежного аудиту; план коригувальних дій.",
            "legal_act_id": legal_acts["Наказ №75"],
            "target_org_type": None,
            "target_is_oki_okii": True,
            "target_category": 2,
            "target_data_type": None,
            "deadline_days": 120,
        },
        {
            "title": "Впровадити стандартні базові заходи (Наказ №75)",
            "description": "Реалізувати стандартний набір базових заходів кіберзахисту відповідно до категорії критичності.",
            "instructions_text": "Почніть з інвентаризації активів, правил доступу, резервного копіювання, журналювання та процедури реагування.",
            "references_text": "Наказ №75; чеклист базових заходів; внутрішній план впровадження контролів.",
            "legal_act_id": legal_acts["Наказ №75"],
            "target_org_type": None,
            "target_is_oki_okii": True,
            "target_category": 3,
            "target_data_type": None,
            "deadline_days": 90,
        },
        {
            "title": "Впровадити стандартні базові заходи (Наказ №75)",
            "description": "Реалізувати стандартний набір базових заходів кіберзахисту відповідно до категорії критичності.",
            "instructions_text": "Почніть з інвентаризації активів, правил доступу, резервного копіювання, журналювання та процедури реагування.",
            "references_text": "Наказ №75; чеклист базових заходів; внутрішній план впровадження контролів.",
            "legal_act_id": legal_acts["Наказ №75"],
            "target_org_type": None,
            "target_is_oki_okii": True,
            "target_category": 4,
            "target_data_type": None,
            "deadline_days": 90,
        },
        {
            "title": "Створити КСЗІ або пройти авторизацію з безпеки (Постанова №373)",
            "description": "Визначити необхідний режим захисту для ДІР або ІзОД та пройти відповідну процедуру підтвердження безпеки.",
            "instructions_text": "Визначте склад системи, класифікуйте інформацію, підготуйте модель загроз, комплект документації та план проходження оцінки.",
            "references_text": "Постанова №373; документація КСЗІ; модель загроз; акт або висновок за результатами оцінки захищеності.",
            "legal_act_id": legal_acts["Постанова №373"],
            "target_org_type": None,
            "target_is_oki_okii": None,
            "target_category": None,
            "target_data_type": "dir",
            "deadline_days": 180,
        },
        {
            "title": "Створити КСЗІ або пройти авторизацію з безпеки (Постанова №373)",
            "description": "Визначити необхідний режим захисту для ДІР або ІзОД та пройти відповідну процедуру підтвердження безпеки.",
            "instructions_text": "Визначте склад системи, класифікуйте інформацію, підготуйте модель загроз, комплект документації та план проходження оцінки.",
            "references_text": "Постанова №373; документація КСЗІ; модель загроз; акт або висновок за результатами оцінки захищеності.",
            "legal_act_id": legal_acts["Постанова №373"],
            "target_org_type": None,
            "target_is_oki_okii": None,
            "target_category": None,
            "target_data_type": "izod",
            "deadline_days": 180,
        },
        {
            "title": "Створити КСЗІ або пройти авторизацію з безпеки (Постанова №373)",
            "description": "Визначити необхідний режим захисту для ДІР та ІзОД і пройти відповідну процедуру підтвердження безпеки.",
            "instructions_text": "Опишіть обидва контури обробки інформації, класифікуйте дані, підготуйте модель загроз, комплект документації та план проходження оцінки.",
            "references_text": "Постанова №373; документація КСЗІ; модель загроз; акт або висновок за результатами оцінки захищеності.",
            "legal_act_id": legal_acts["Постанова №373"],
            "target_org_type": None,
            "target_is_oki_okii": None,
            "target_category": None,
            "target_data_type": "dir_izod",
            "deadline_days": 180,
        },
    ]

    for row in template_rows:
        connection.execute(
            text(
                "INSERT INTO roadmap_template_steps "
                "(title, description, instructions_text, references_text, legal_act_id, "
                "target_org_type, target_is_oki_okii, target_category, target_data_type, deadline_days) "
                "VALUES (:title, :description, :instructions_text, :references_text, :legal_act_id, "
                ":target_org_type, :target_is_oki_okii, :target_category, :target_data_type, :deadline_days)"
            ),
            row,
        )


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db:
        yield db
