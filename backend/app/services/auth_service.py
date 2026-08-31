import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from backend.app.config.database import db_manager
from backend.app.utils.security import hash_password, verify_password, create_access_token
from backend.app.schemas.auth import UserRegisterRequest, UserLoginRequest
from backend.app.utils.logger import logger

class AuthService:
    def __init__(self):
        pass

    @property
    def users_collection(self):
        return db_manager.get_collection("users")

    async def register_user(self, req: UserRegisterRequest) -> Dict[str, Any]:
        email = req.email.strip().lower()
        existing = await self.users_collection.find_one({"email": email})
        if existing:
            raise ValueError("An account with this email address already exists.")

        user_id = str(uuid.uuid4())
        hashed = hash_password(req.password)
        
        user_doc = {
            "_id": user_id,
            "name": req.name.strip(),
            "email": email,
            "passwordHash": hashed,
            "role": req.role if req.role in ["student", "admin"] else "student",
            "createdAt": datetime.utcnow().isoformat(),
            "lastLogin": None
        }

        await self.users_collection.insert_one(user_doc)
        token = create_access_token({"sub": user_id, "email": email, "role": user_doc["role"]})
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "name": user_doc["name"],
                "email": user_doc["email"],
                "role": user_doc["role"],
                "createdAt": user_doc["createdAt"],
                "lastLogin": user_doc["lastLogin"]
            }
        }

    async def login_user(self, req: UserLoginRequest) -> Dict[str, Any]:
        email = req.email.strip().lower()
        user_doc = await self.users_collection.find_one({"email": email})
        if not user_doc:
            raise ValueError("Invalid email or password.")

        if not verify_password(req.password, user_doc.get("passwordHash", "")):
            raise ValueError("Invalid email or password.")

        now_str = datetime.utcnow().isoformat()
        await self.users_collection.update_one(
            {"_id": user_doc["_id"]},
            {"$set": {"lastLogin": now_str}}
        )

        token = create_access_token({
            "sub": str(user_doc["_id"]),
            "email": user_doc["email"],
            "role": user_doc.get("role", "student")
        })

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": str(user_doc["_id"]),
                "name": user_doc.get("name", "Student"),
                "email": user_doc["email"],
                "role": user_doc.get("role", "student"),
                "createdAt": str(user_doc.get("createdAt", "")),
                "lastLogin": now_str
            }
        }

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        user_doc = await self.users_collection.find_one({"_id": user_id})
        if not user_doc:
            return None
        return {
            "id": str(user_doc["_id"]),
            "name": user_doc.get("name", ""),
            "email": user_doc.get("email", ""),
            "role": user_doc.get("role", "student"),
            "createdAt": str(user_doc.get("createdAt", "")),
            "lastLogin": user_doc.get("lastLogin")
        }

    async def seed_default_users(self):
        """Seed default admin and demo student account."""
        admin = await self.users_collection.find_one({"email": "admin@college.edu"})
        if not admin:
            logger.info("Seeding default admin user: admin@college.edu")
            await self.users_collection.insert_one({
                "_id": "admin-default-id",
                "name": "Academic Administrator",
                "email": "admin@college.edu",
                "passwordHash": hash_password("Admin@123"),
                "role": "admin",
                "createdAt": datetime.utcnow().isoformat(),
                "lastLogin": None
            })

        student = await self.users_collection.find_one({"email": "student@college.edu"})
        if not student:
            logger.info("Seeding demo student user: student@college.edu")
            await self.users_collection.insert_one({
                "_id": "student-demo-id",
                "name": "Demo Student",
                "email": "student@college.edu",
                "passwordHash": hash_password("Student@123"),
                "role": "student",
                "createdAt": datetime.utcnow().isoformat(),
                "lastLogin": None
            })

auth_service = AuthService()
