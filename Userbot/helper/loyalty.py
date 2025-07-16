from config import mongo_points, mongo_db
import hashlib

def add_loyalty_point(user_id: int):
    doc = mongo_points.find_one({"user_id": user_id})
    if doc:
        new_points = doc.get("points", 0) + 1
        mongo_points.update_one({"user_id": user_id}, {"$set": {"points": new_points}})
    else:
        new_points = 1
        mongo_points.insert_one({"user_id": user_id, "points": 1})
    return new_points

def get_loyalty_point(user_id: int):
    doc = mongo_points.find_one({"user_id": user_id})
    return doc.get("points", 0) if doc else 0

def set_loyalty_point(user_id: int, points: int):
    mongo_points.update_one({"user_id": user_id}, {"$set": {"points": points}}, upsert=True)

def reset_loyalty_point(user_id: int):
    mongo_points.update_one({"user_id": user_id}, {"$set": {"points": 0}})

def generate_referral_code(user_id, owner_id):
    """Generate unique code hash from user_id and owner_id."""
    raw = f"{user_id}-{owner_id}"
    return hashlib.sha256(raw.encode()).hexdigest()[:10]

def save_referral_code(user_id, code):
    """Save code, not used yet, status active."""
    mongo_db["referrals"].update_one(
        {"code": code},
        {"$set": {"user_id": user_id, "code": code, "used": False}},
        upsert=True,
    )

def get_referral_by_code(code):
    return mongo_db["referrals"].find_one({"code": code})

def blacklist_referral_code(code):
    mongo_db["referrals"].update_one({"code": code}, {"$set": {"used": True}})

def can_generate_new_code(user_id):
    # Allow if there is no active code
    active = mongo_db["referrals"].find_one({"user_id": user_id, "used": False})
    return active is None

def regenerate_referral_code(user_id, owner_id):
    code = generate_referral_code(user_id, owner_id)
    save_referral_code(user_id, code)
    return code