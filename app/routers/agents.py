from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models import Agent, User, UserRole
from app.schemas.agent import AgentCreate, AgentUpdate, AgentOut
from app.services.audit import log_action

router = APIRouter(prefix="/agents", tags=["agents"])

MANAGER_ROLES = (UserRole.ADMIN_CEO, UserRole.CFO, UserRole.FINANCE_MANAGER)


@router.get("", response_model=list[AgentOut])
def list_agents(
    search: str | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*MANAGER_ROLES)),
):
    q = db.query(Agent)
    if search:
        like = f"%{search}%"
        q = q.filter(or_(Agent.business_name.ilike(like), Agent.email.ilike(like)))
    return q.order_by(Agent.created_at.desc()).all()


@router.post("", response_model=AgentOut, status_code=201)
def create_agent(
    payload: AgentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*MANAGER_ROLES)),
):
    agent = Agent(**payload.model_dump())
    db.add(agent)
    db.flush()
    log_action(db, user, "Created agent", "Agent", agent.id, agent.business_name)
    db.commit()
    db.refresh(agent)
    return agent


@router.get("/{agent_id}", response_model=AgentOut)
def get_agent(agent_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(*MANAGER_ROLES))):
    agent = db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")
    return agent


@router.patch("/{agent_id}", response_model=AgentOut)
def update_agent(
    agent_id: int,
    payload: AgentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*MANAGER_ROLES)),
):
    agent = db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(agent, k, v)
    log_action(db, user, "Updated agent", "Agent", agent.id)
    db.commit()
    db.refresh(agent)
    return agent


@router.delete("/{agent_id}", status_code=204)
def delete_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ADMIN_CEO, UserRole.CFO)),
):
    agent = db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")
    db.delete(agent)
    log_action(db, user, "Deleted agent", "Agent", agent_id)
    db.commit()
