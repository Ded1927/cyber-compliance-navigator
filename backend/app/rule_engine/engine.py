from dataclasses import dataclass

# pyrefly: ignore [missing-import]
from sqlalchemy import delete, select
# pyrefly: ignore [missing-import]
from sqlalchemy.ext.asyncio import AsyncSession
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import selectinload

from app.core.database import AsyncSessionLocal
from app.models.legal_act import LegalAct
from app.models.organization_profile import OrganizationProfile
from app.models.roadmap_item import RoadmapItem, RoadmapStatus
from app.schemas.questionnaire import (
    CriticalityCategory,
    DataType,
    LegalActResponse,
    OrganizationProfileResponse,
    QuestionnaireAnswers,
    RoadmapItemResponse,
    RoadmapResponse,
)


@dataclass(frozen=True)
class LegalActSeed:
    title: str
    number_date: str
    act_type: str
    status: str
    official_url: str | None
    short_explanation: str


@dataclass(frozen=True)
class RoadmapRule:
    step_name: str
    description: str
    act: LegalActSeed


BASE_LEGAL_ACT = LegalActSeed(
    title="Закон України Про основні засади забезпечення кібербезпеки України",
    number_date="№ 2163-VIII від 05.10.2017",
    act_type="law",
    status="active",
    official_url=None,
    short_explanation="Базовий закон для визначення ролей, обов'язків і підходів у сфері кібербезпеки.",
)

CMU_712 = LegalActSeed(
    title="Постанова КМУ № 712",
    number_date="№ 712",
    act_type="resolution",
    status="active",
    official_url=None,
    short_explanation="Вимоги для організацій, які обробляють державні інформаційні ресурси або інформацію з обмеженим доступом.",
)

CMU_373 = LegalActSeed(
    title="Постанова КМУ № 373",
    number_date="№ 373",
    act_type="resolution",
    status="active",
    official_url=None,
    short_explanation="Вимоги щодо організації захисту інформації в інформаційних, електронних комунікаційних та інформаційно-комунікаційних системах.",
)

class RuleEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_answers(self, answers: QuestionnaireAnswers, user_id: int) -> RoadmapResponse:
        try:
            profile = await self._upsert_organization_profile(answers=answers, user_id=user_id)
            await self._clear_existing_primary_roadmap(user_id=user_id)

            rules = self._select_rules(answers)
            for index, rule in enumerate(rules, start=1):
                await self._create_roadmap_item(
                    user_id=user_id,
                    rule=rule,
                    order_index=index,
                )

            await self.db.commit()
            await self.db.refresh(profile)
        except Exception:
            await self.db.rollback()
            raise

        roadmap_items = list(
            (await self.db.scalars(
                select(RoadmapItem)
                .where(RoadmapItem.user_id == user_id)
                .options(selectinload(RoadmapItem.act))
                .order_by(RoadmapItem.order_index)
            )).all()
        )

        return self._build_response(profile=profile, roadmap_items=roadmap_items)

    async def _upsert_organization_profile(
        self,
        answers: QuestionnaireAnswers,
        user_id: int,
    ) -> OrganizationProfile:
        profile = await self.db.scalar(
            select(OrganizationProfile).where(OrganizationProfile.user_id == user_id)
        )

        values = {
            "org_type": answers.org_type.value,
            "name_optional": None,
            "edrpou_optional": None,
            "is_oki_operator": answers.is_oki_or_okii,
            "criticality_category": category_to_int(answers.category),
        }

        if profile is None:
            profile = OrganizationProfile(user_id=user_id, **values)
            self.db.add(profile)
            return profile

        for field_name, field_value in values.items():
            setattr(profile, field_name, field_value)
        return profile

    async def _clear_existing_primary_roadmap(self, user_id: int) -> None:
        await self.db.execute(delete(RoadmapItem).where(RoadmapItem.user_id == user_id))

    def _select_rules(self, answers: QuestionnaireAnswers) -> list[RoadmapRule]:
        rules = [
            RoadmapRule(
                step_name="Визначити кібербезпекову роль організації",
                description=(
                    "Зафіксувати тип організації, відповідальних осіб, контур систем "
                    "та первинні обов'язки у сфері кібербезпеки."
                ),
                act=BASE_LEGAL_ACT,
            )
        ]

        if answers.data_type in {DataType.DIR, DataType.IZOD, DataType.DIR_IZOD}:
            rules.extend(
                [
                    RoadmapRule(
                        step_name="Провести інвентаризацію ДІР/ІзОД",
                        description=(
                            "Описати державні інформаційні ресурси та/або інформацію "
                            "з обмеженим доступом, що обробляються в системах організації."
                        ),
                        act=CMU_712,
                    ),
                    RoadmapRule(
                        step_name="Перевірити вимоги до захисту інформації",
                        description=(
                            "Визначити необхідні організаційні та технічні заходи захисту "
                            "для систем, у яких обробляються ДІР/ІзОД."
                        ),
                        act=CMU_373,
                    ),
                ]
            )

        return rules

    async def _create_roadmap_item(
        self,
        user_id: int,
        rule: RoadmapRule,
        order_index: int,
    ) -> RoadmapItem:
        act = await self._get_or_create_legal_act(rule.act)
        roadmap_item = RoadmapItem(
            user_id=user_id,
            act=act,
            step_name=rule.step_name,
            description=rule.description,
            status=RoadmapStatus.NOT_STARTED,
            order_index=order_index,
        )
        self.db.add(roadmap_item)
        return roadmap_item

    async def _get_or_create_legal_act(self, seed: LegalActSeed) -> LegalAct:
        legal_act = await self.db.scalar(
            select(LegalAct).where(
                LegalAct.title == seed.title,
                LegalAct.number_date == seed.number_date,
            )
        )
        if legal_act is not None:
            return legal_act

        legal_act = LegalAct(
            title=seed.title,
            number_date=seed.number_date,
            act_type=seed.act_type,
            status=seed.status,
            official_url=seed.official_url,
            short_explanation=seed.short_explanation,
        )
        self.db.add(legal_act)
        await self.db.flush()
        return legal_act

    def _build_response(
        self,
        profile: OrganizationProfile,
        roadmap_items: list[RoadmapItem],
    ) -> RoadmapResponse:
        return RoadmapResponse(
            organization_profile=OrganizationProfileResponse.model_validate(profile),
            items=[
                RoadmapItemResponse(
                    id=item.id,
                    act_id=item.act_id,
                    step_name=item.step_name,
                    description=item.description,
                    status=int(item.status),
                    order_index=item.order_index,
                    legal_act=LegalActResponse.model_validate(item.act),
                )
                for item in roadmap_items
            ],
        )


async def process_answers(
    answers: QuestionnaireAnswers,
    user_id: int,
    db: AsyncSession | None = None,
) -> RoadmapResponse:
    if db is not None:
        return await RuleEngine(db).process_answers(answers=answers, user_id=user_id)

    async with AsyncSessionLocal() as session:
        return await RuleEngine(session).process_answers(answers=answers, user_id=user_id)


def category_to_int(category: CriticalityCategory | None) -> int | None:
    if category is None:
        return None

    return {
        CriticalityCategory.CAT_1: 1,
        CriticalityCategory.CAT_2: 2,
        CriticalityCategory.CAT_3: 3,
        CriticalityCategory.CAT_4: 4,
    }[category]
