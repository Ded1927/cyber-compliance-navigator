from uuid import UUID

# pyrefly: ignore [missing-import]
from sqlalchemy import and_, or_, select
# pyrefly: ignore [missing-import]
from sqlalchemy.ext.asyncio import AsyncSession
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import selectinload

from app.models.roadmap import OrganizationTask, RoadmapTemplateStep
from app.schemas.questionnaire import (
    CriticalityCategory,
    DataType,
    QuestionnaireAnswers,
)
from app.schemas.roadmap import OrganizationTaskResponse, RoadmapTaskUpdate

class RoadmapGeneratorService:
    async def generate_for_answers(
        self,
        db: AsyncSession,
        answers: QuestionnaireAnswers,
        organization_id: UUID,
    ) -> list[OrganizationTask]:
        templates = await self.find_matching_templates(db=db, answers=answers)
        existing_template_ids = set(
            (await db.scalars(
                select(OrganizationTask.template_id).where(
                    OrganizationTask.organization_id == organization_id
                )
            )).all()
        )

        for template in templates:
            if template.id in existing_template_ids:
                continue

            task = OrganizationTask(
                organization_id=organization_id,
                template_id=template.id,
            )
            db.add(task)
            existing_template_ids.add(template.id)

        await db.commit()
        return await self.get_tasks_for_organization(
            db=db,
            organization_id=organization_id,
        )

    async def find_matching_templates(
        self,
        db: AsyncSession,
        answers: QuestionnaireAnswers,
    ) -> list[RoadmapTemplateStep]:
        category = category_to_int(answers.category)
        data_type_values = matching_data_type_values(answers.data_type)

        result = await db.scalars(
            select(RoadmapTemplateStep)
            .options(selectinload(RoadmapTemplateStep.legal_act))
            .where(
                and_(
                    or_(
                        RoadmapTemplateStep.target_org_type.is_(None),
                        RoadmapTemplateStep.target_org_type == answers.org_type.value,
                    ),
                    or_(
                        RoadmapTemplateStep.target_is_oki_okii.is_(None),
                        RoadmapTemplateStep.target_is_oki_okii == answers.is_oki_or_okii,
                    ),
                    or_(
                        RoadmapTemplateStep.target_category.is_(None),
                        RoadmapTemplateStep.target_category == category,
                    ),
                    or_(
                        RoadmapTemplateStep.target_data_type.is_(None),
                        RoadmapTemplateStep.target_data_type.in_(data_type_values),
                    ),
                )
            )
            .order_by(RoadmapTemplateStep.deadline_days, RoadmapTemplateStep.id)
        )
        return list(result.all())

    async def get_tasks_for_organization(
        self,
        db: AsyncSession,
        organization_id: UUID,
    ) -> list[OrganizationTask]:
        result = await db.scalars(
            select(OrganizationTask)
            .options(
                selectinload(OrganizationTask.template).selectinload(
                    RoadmapTemplateStep.legal_act
                )
            )
            .where(OrganizationTask.organization_id == organization_id)
            .order_by(RoadmapTemplateStep.deadline_days, OrganizationTask.id)
            .join(OrganizationTask.template)
        )
        return list(result.all())

    def to_response(self, tasks: list[OrganizationTask]) -> list[OrganizationTaskResponse]:
        return [OrganizationTaskResponse.model_validate(task) for task in tasks]

    async def update_task(
        self,
        db: AsyncSession,
        task_id: UUID,
        payload: RoadmapTaskUpdate,
    ) -> OrganizationTask | None:
        task = await db.get(
            OrganizationTask,
            task_id,
            options=[
                selectinload(OrganizationTask.template).selectinload(
                    RoadmapTemplateStep.legal_act
                )
            ],
        )
        if task is None:
            return None

        task.template.title = payload.title
        task.template.description = payload.description
        task.template.instructions_text = payload.guidance
        task.template.references_text = payload.references
        task.template.deadline_days = payload.deadline_days

        await db.commit()
        await db.refresh(task)
        await db.refresh(task.template)
        return task


def category_to_int(category: CriticalityCategory | None) -> int | None:
    if category is None:
        return None

    return {
        CriticalityCategory.CAT_1: 1,
        CriticalityCategory.CAT_2: 2,
        CriticalityCategory.CAT_3: 3,
        CriticalityCategory.CAT_4: 4,
    }[category]


def matching_data_type_values(data_type: DataType) -> set[str]:
    return {data_type.value}
