from uuid import UUID

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status
# pyrefly: ignore [missing-import]
from sqlalchemy import select
# pyrefly: ignore [missing-import]
from sqlalchemy.ext.asyncio import AsyncSession
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import selectinload
from app.core.database import get_async_db
from app.models.organization_profile import OrganizationProfile
from app.models.roadmap import OrganizationTask, RoadmapTemplateStep
from app.models.roadmap_item import RoadmapItem
from app.models.user import User
from app.rule_engine.engine import process_answers
from app.schemas.questionnaire import (
    CriticalityCategory,
    LegalActResponse,
    OrganizationProfileResponse,
    QuestionnaireAnswers,
    RoadmapItemResponse,
    RoadmapResponse,
)
from app.schemas.roadmap import RoadmapTaskResponse, RoadmapTaskUpdate
from app.services.auth import get_current_user
from app.services.roadmap import RoadmapGeneratorService

router = APIRouter(prefix="/api/questionnaire", tags=["questionnaire"])


@router.post("/submit", response_model=list[RoadmapTaskResponse])
async def submit_questionnaire_for_roadmap_tasks(
    answers: QuestionnaireAnswers,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> list[RoadmapTaskResponse]:
    profile = await get_or_create_organization_profile(
        db=db,
        user_id=current_user.id,
        answers=answers,
    )

    service = RoadmapGeneratorService()
    tasks = await service.generate_for_answers(
        db=db,
        answers=answers,
        organization_id=profile.public_id,
    )
    return service.to_response(tasks)


@router.get("/tasks", response_model=list[RoadmapTaskResponse])
async def get_generated_roadmap_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> list[RoadmapTaskResponse]:
    profile = await db.scalar(
        select(OrganizationProfile).where(OrganizationProfile.user_id == current_user.id)
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire has not been completed yet",
        )

    tasks = await RoadmapGeneratorService().get_tasks_for_organization(
        db=db,
        organization_id=profile.public_id,
    )
    return RoadmapGeneratorService().to_response(tasks)


@router.get("/admin-status")
async def get_questionnaire_admin_status(
    current_user: User = Depends(get_current_user),
) -> dict[str, bool]:
    return {"can_edit_roadmap": current_user.is_admin}


@router.put("/tasks/{task_id}", response_model=RoadmapTaskResponse)
async def update_roadmap_task(
    task_id: UUID,
    payload: RoadmapTaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> RoadmapTaskResponse:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can edit roadmap tasks",
        )

    task = await RoadmapGeneratorService().update_task(
        db=db,
        task_id=task_id,
        payload=payload,
    )
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap task not found",
        )

    return RoadmapTaskResponse.model_validate(task)


@router.post("", response_model=RoadmapResponse)
async def submit_questionnaire(
    answers: QuestionnaireAnswers,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> RoadmapResponse:
    return await process_answers(answers=answers, user_id=current_user.id, db=db)


async def get_or_create_organization_profile(
    db: AsyncSession,
    user_id: int,
    answers: QuestionnaireAnswers,
) -> OrganizationProfile:
    profile = await db.scalar(
        select(OrganizationProfile).where(OrganizationProfile.user_id == user_id)
    )

    if profile is None:
        profile = OrganizationProfile(
            user_id=user_id,
            org_type=answers.org_type.value,
            is_oki_operator=answers.is_oki_or_okii,
            criticality_category=category_to_int(answers.category),
        )
        db.add(profile)
    else:
        profile.org_type = answers.org_type.value
        profile.is_oki_operator = answers.is_oki_or_okii
        profile.criticality_category = category_to_int(answers.category)

    await db.flush()
    return profile


def category_to_int(category: CriticalityCategory | None) -> int | None:
    if category is None:
        return None

    return {
        CriticalityCategory.CAT_1: 1,
        CriticalityCategory.CAT_2: 2,
        CriticalityCategory.CAT_3: 3,
        CriticalityCategory.CAT_4: 4,
    }[category]


@router.get("/roadmap", response_model=RoadmapResponse)
async def get_generated_roadmap(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> RoadmapResponse:
    profile = await db.scalar(
        select(OrganizationProfile).where(OrganizationProfile.user_id == current_user.id)
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire has not been completed yet",
        )

    items = list(
        (await db.scalars(
            select(RoadmapItem)
            .where(RoadmapItem.user_id == current_user.id)
            .options(selectinload(RoadmapItem.act))
            .order_by(RoadmapItem.order_index)
        )).all()
    )

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
            for item in items
        ],
    )
