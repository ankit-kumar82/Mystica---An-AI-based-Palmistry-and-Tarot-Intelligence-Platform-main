from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import jwt
import json
import random  # Added for auto-assignment
from datetime import datetime, timezone
from database import db
from routers.auth import oauth2_scheme, SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/api/consultations", tags=["Consultations"])

class ConsultationCreate(BaseModel):
    readingId: str
    specialistType: str  
    clientQuestion: Optional[str] = None

class ConsultationReview(BaseModel):
    specialistNotes: str
    summary: Optional[str] = None
    rating: Optional[int] = None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        user = await db.user.find_unique(where={"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/")
async def create_consultation(data: ConsultationCreate, user=Depends(get_current_user)):
    reading = await db.reading.find_unique(where={"id": data.readingId})
    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")

    # AUTO-ASSIGNMENT LOGIC
    assigned_specialist_id = None
    try:
        specialist_keyword = data.specialistType.split('_')[0]
        
        available_specialists = await db.user.find_many(
            where={
                "role": {
                    "contains": specialist_keyword,
                    "mode": "insensitive"
                }
            }
        )
        
        if available_specialists:
            assigned_specialist_id = random.choice(available_specialists).id
            print(f"Ticket auto-assigned to Specialist ID: {assigned_specialist_id}")
    except Exception as e:
        print(f"Auto-assignment failed, defaulting to NULL: {e}")

    consultation = await db.consultation.create(
        data={
            "clientId": user.id,
            "readingId": data.readingId,
            "specialistType": data.specialistType,
            "clientQuestion": data.clientQuestion,
            "specialistId": assigned_specialist_id, # Locks the ticket to the chosen specialist
            "status": "Pending",
        }
    )
    
    await db.activitylog.create(
        data={
            "userId": user.id,
            "action": "consultation_booked",
            "metadata": json.dumps({"specialistType": data.specialistType})
        }
    )
    
    return consultation

@router.get("/")
async def get_consultations(user=Depends(get_current_user)):
    role = user.role.lower()

    # USER INBOX VIEW: Users only see their own requested tickets
    if role == "user":
        tickets = await db.consultation.find_many(
            where={"clientId": user.id},
            include={"specialist": True, "reading": True},
            order={"createdAt": "desc"},
        )
        return tickets

    # SPECIALIST QUEUE VIEW
    if "palm" in role:
        specialist_type = "palm_reader"
    elif "tarot" in role:
        specialist_type = "tarot_reader"
    else:
        specialist_type = "spiritual_consultant"

    # STRICT ROUTING: Specialists ONLY see tickets assigned to them
    tickets = await db.consultation.find_many(
        where={
            "specialistType": specialist_type,
            "specialistId": user.id 
        },
        include={"client": {"include": {"profile": True}}, "reading": True},
        order={"createdAt": "desc"},
    )

    if specialist_type == "spiritual_consultant":
        enriched_tickets = []
        for ticket in tickets:
            t_dict = ticket.model_dump() if hasattr(ticket, "model_dump") else dict(ticket)

            if getattr(ticket, "client", None):
                t_dict["client"] = ticket.client.model_dump() if hasattr(ticket.client, "model_dump") else dict(ticket.client)
                if getattr(ticket.client, "profile", None):
                    t_dict["client"]["profile"] = ticket.client.profile.model_dump() if hasattr(ticket.client.profile, "model_dump") else dict(ticket.client.profile)
            if getattr(ticket, "reading", None):
                t_dict["reading"] = ticket.reading.model_dump() if hasattr(ticket.reading, "model_dump") else dict(ticket.reading)

            user_history = await db.reading.find_many(
                where={"userId": ticket.clientId},
                order={"createdAt": "desc"},
                take=10,
            )

            latest_palm = next(
                (r for r in user_history if r.readingType and r.readingType.lower() == "palm"),
                None,
            )
            latest_tarot = next(
                (r for r in user_history if r.readingType and r.readingType.lower() == "tarot"),
                None,
            )

            t_dict["latestPalm"] = (
                latest_palm.model_dump() if hasattr(latest_palm, "model_dump")
                else (dict(latest_palm) if latest_palm else None)
            )
            t_dict["latestTarot"] = (
                latest_tarot.model_dump() if hasattr(latest_tarot, "model_dump")
                else (dict(latest_tarot) if latest_tarot else None)
            )

            enriched_tickets.append(t_dict)

        return enriched_tickets

    return tickets

@router.get("/stats")
async def get_consultation_stats(user=Depends(get_current_user)):
    # SPECIALIST DASHBOARD STATS: Counts only tickets assigned to this specialist
    pending_count = await db.consultation.count(
        where={
            "specialistId": user.id,
            "status": "Pending"
        }
    )
    
    completed_count = await db.consultation.count(
        where={
            "specialistId": user.id,
            "status": "Completed"
        }
    )

    return {
        "pending": pending_count,
        "completedAllTime": completed_count
    }

@router.patch("/{consultation_id}/review")
async def review_consultation(
    consultation_id: str, data: ConsultationReview, user=Depends(get_current_user)
):
    role = user.role.lower()
    if role == "user":
        raise HTTPException(status_code=403, detail="Users cannot review tickets")

    # SECURITY CHECK: Block specialists from reviewing tickets assigned to someone else
    ticket = await db.consultation.find_unique(where={"id": consultation_id})
    if not ticket or (ticket.specialistId and ticket.specialistId != user.id):
        raise HTTPException(status_code=403, detail="This ticket is assigned to a different specialist.")

    updated = await db.consultation.update(
        where={"id": consultation_id},
        data={
            "status": "Completed",
            "specialistNotes": data.specialistNotes, 
            "reviewedAt": datetime.now(timezone.utc)
        },
    )

    await db.notification.create(
        data={
            "userId": updated.clientId,
            "title": "Consultation Ready",
            "message": f"Your specialist has completed your reading. Check your vault to view the insights.",
            "type": "normal",
            "isRead": False
        }
    )
    
    await db.activitylog.create(
        data={
            "userId": user.id, 
            "action": "consultation_completed",
            "metadata": json.dumps({"ticketId": consultation_id})
        }
    )
    
    return updated

@router.get("/{consultation_id}/view")
async def view_completed_review(consultation_id: str, user=Depends(get_current_user)):
    ticket = await db.consultation.find_unique(where={"id": consultation_id})
    if not ticket or ticket.clientId != user.id:
        raise HTTPException(status_code=404, detail="Ticket not found")

    await db.activitylog.create(
        data={
            "userId": user.id,
            "action": "review_viewed",
            "metadata": json.dumps({"ticketId": consultation_id, "specialistType": ticket.specialistType})
        }
    )
    
    return ticket