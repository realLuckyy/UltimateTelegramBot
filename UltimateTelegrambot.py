#!/usr/bin/env python3
import asyncio
from datetime import datetime, timedelta, timezone, time
from collections import defaultdict
from typing import Dict, Set, List, Tuple
import random
import hashlib
import base64

from telegram import (
    Update,
    ChatMember,
    ChatMemberUpdated,
    Message,
    MessageReactionUpdated,
    ReactionTypeEmoji,
)
from telegram.constants import ParseMode, ChatMemberStatus
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ChatMemberHandler,
    MessageReactionHandler,
    filters,
    ContextTypes,
)
from telegram.request import HTTPXRequest
from telegram.error import TimedOut, NetworkError, RetryAfter, Forbidden

# ========= CONFIG =========
TOKEN = "place_token_here"

# New-member enforcement
NEW_MEMBER_POST_WINDOW = timedelta(hours=1)
NEW_MEMBER_WARN_BEFORE = timedelta(minutes=15)

# Inactivity policy (general members)
INACTIVITY_WARN_AT = timedelta(hours=48)
INACTIVITY_KICK_AT = timedelta(hours=72)
CHECK_INTERVAL = timedelta(minutes=15)

# Daily top-poster window
DAILY_WINDOW = timedelta(hours=24)
WEEKLY_WINDOW = timedelta(days=7)

# Streak & Badge thresholds
DAILY_STREAK_THRESHOLD = 1  # posts per day
WEEKLY_STREAK_THRESHOLD = 5  # posts per week
STREAK_CHECK_INTERVAL = timedelta(hours=6)  # Check streaks every 6 hours

# Points for content
PTS_PHOTO = 1
PTS_VIDEO = 1
PTS_DOC   = 1
PTS_LINK  = 1

# Coin rewards
COIN_DAILY_POST = 10
COIN_STREAK_BONUS = 5
COIN_REACTION_RECEIVED = 2
COIN_CHALLENGE_COMPLETE = 50
COIN_LEVEL_UP = 25

# Referral rewards
COIN_REFERRAL_SIGNUP = 50    # Coins for referrer when someone signs up with their code
COIN_REFERRAL_WELCOME = 25   # Welcome bonus for new member using referral code
COIN_REFERRAL_MILESTONE = 100  # Bonus when referred user becomes active (posts 10+ times)
REFERRAL_ACTIVITY_THRESHOLD = 10  # Posts needed for referral milestone

# Title thresholds
TITLE_THRESHOLDS = [
    (0, "🆕 Newcomer"),
    (10, "🥉 Rookie"),
    (50, "⭐ Regular"),
    (150, "🔥 Active"),
    (300, "🏅 Veteran"),
    (500, "👑 Elite"),
    (1000, "🌟 Legend"),
    (2000, "🏆 Hall of Fame")
]

# Weekly challenges
WEEKLY_CHALLENGES = {
    "photo_spree": {
        "name": "Photo Spree",
        "description": "Share 20 photos this week",
        "target": 20,
        "type": "photo",
        "reward": 100,
        "emoji": "📸"
    },
    "streak_keeper": {
        "name": "Streak Keeper",
        "description": "Maintain a 5+ day streak",
        "target": 5,
        "type": "streak",
        "reward": 75,
        "emoji": "🔥"
    },
    "social_butterfly": {
        "name": "Social Butterfly",
        "description": "Get 30 reactions on your posts",
        "target": 30,
        "type": "reactions",
        "reward": 80,
        "emoji": "🦋"
    },
    "content_creator": {
        "name": "Content Creator",
        "description": "Post 15 pieces of content",
        "target": 15,
        "type": "posts",
        "reward": 90,
        "emoji": "🎨"
    },
    "early_bird": {
        "name": "Early Bird",
        "description": "Post 5 times between 6-9 AM",
        "target": 5,
        "type": "early_posts",
        "reward": 60,
        "emoji": "🌅"
    },
    "referral_master": {
        "name": "Referral Master",
        "description": "Refer 3 new members this week",
        "target": 3,
        "type": "referrals",
        "reward": 150,
        "emoji": "🤝"
    }
}

# Shop items
SHOP_ITEMS = {
    "custom_badge": {
        "name": "Custom Badge",
        "description": "Get a personalized badge for your profile",
        "price": 200,
        "type": "cosmetic",
        "emoji": "🎖️"
    },
    "xp_boost": {
        "name": "XP Booster",
        "description": "2x XP for 24 hours",
        "price": 150,
        "type": "boost",
        "duration": timedelta(hours=24),
        "emoji": "⚡"
    },
    "title_unlock": {
        "name": "Custom Title",
        "description": "Unlock a special custom title",
        "price": 300,
        "type": "title",
        "emoji": "👑"
    },
    "streak_freeze": {
        "name": "Streak Freeze",
        "description": "Protect your streak for 2 days",
        "price": 100,
        "type": "protection",
        "duration": timedelta(days=2),
        "emoji": "🧊"
    },
    "coin_boost": {
        "name": "Coin Multiplier",
        "description": "2x coins for 12 hours",
        "price": 120,
        "type": "boost",
        "duration": timedelta(hours=12),
        "emoji": "💰"
    },
    "referral_boost": {
        "name": "Referral Booster",
        "description": "2x referral rewards for 48 hours",
        "price": 180,
        "type": "boost",
        "duration": timedelta(hours=48),
        "emoji": "🤝"
    }
}

# Available badges to unlock
AVAILABLE_BADGES = {
    "social_master": {
        "name": "Social Master",
        "description": "Get 100+ reactions in a week",
        "requirement": "100 weekly reactions",
        "emoji": "🌟"
    },
    "content_king": {
        "name": "Content King",
        "description": "Post 50+ times in a week", 
        "requirement": "50 weekly posts",
        "emoji": "👑"
    },
    "early_adopter": {
        "name": "Early Adopter",
        "description": "One of the first 10 members",
        "requirement": "Be among first 10 members",
        "emoji": "🚀"
    },
    "consistency_champion": {
        "name": "Consistency Champion",
        "description": "Maintain 14+ day streak",
        "requirement": "14+ day posting streak",
        "emoji": "🏆"
    },
    "referral_champion": {
        "name": "Referral Champion",
        "description": "Successfully refer 10+ members",
        "requirement": "Refer 10+ active members",
        "emoji": "🤝"
    },
    "community_builder": {
        "name": "Community Builder",
        "description": "Refer 25+ members",
        "requirement": "Refer 25+ active members",
        "emoji": "🏗️"
    }
}

# Text blocks
RULES_TEXT = (
    "📌 <b>Rules</b>\n"
    "1️⃣ Post Real content (images, videos, links, etc).\n"
    "2️⃣ No selling / trading.\n"
    "3️⃣ Respect other members.\n"
    "4️⃣ Inactivity = warning → kick.\n"
    "5️⃣ This is a 18+ group.\n\n"
    "⚠️ Stay active or you may be removed."
)

HELP_TEXT = (
    "🤖 <b>Strictly🇬🇧Bot Commands</b>\n\n"
    "📌 /rules → Show group rules\n"
    "🆔 /chatid → Display this group's Chat ID\n"
    "📊 /stats → Show daily stats & top posters\n"
    "🏅 /achievements → Show your unlocked badges\n"
    "🏆 /top → Show today's top posters\n"
    "⭐ /level → Show your XP & Level\n"
    "🔥 /streak → Show your posting streak\n"
    "🎖️ /badges → Show available badges to unlock\n"
    "📈 /leaderboard → Show weekly leaderboard\n"
    "❤️ /reactions → Show weekly reaction reports\n"
    "👤 /profile → Show complete user profile\n"
    "🏅 /ranking → Show all-time rankings\n"
    "💰 /coins → Show your coin balance\n"
    "🛒 /shop → Browse the rewards shop\n"
    "🎯 /challenges → View weekly challenges\n"
    "👑 /title → Manage your title\n"
    "🤝 /referral → Manage your referral code & stats\n"
    "ℹ️ /help → Show this help menu\n\n"
    "⚠️ Activity Rules:\n"
    "- New members must post within 1h or risk removal.\n"
    "- Inactive = Warn at 48h → Kick at 72h.\n"
    "- Keep daily streaks for special rewards!\n"
    "- Complete challenges to earn coins! 💰\n"
    "- React to posts to spread the love! ❤️\n"
    "- Invite friends with your referral code! 🤝\n"
    "- 18+ group only. Stay active!"
)

UTC = timezone.utc

# ========= STATE (in-memory) =========
known_chats: Set[int] = set()
last_activity_utc: Dict[int, Dict[int, datetime]] = defaultdict(dict)
total_content_count: Dict[int, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
daily_content_count: Dict[int, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
weekly_content_count: Dict[int, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
warned_48h: Dict[int, Set[int]] = defaultdict(set)
new_member_deadline: Dict[int, Dict[int, datetime]] = defaultdict(dict)
new_member_warned: Dict[int, Set[int]] = defaultdict(set)

# Streaks & Badges
user_streaks: Dict[int, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
last_post_date: Dict[int, Dict[int, datetime]] = defaultdict(dict)

# Content type tracking
content_type_count: Dict[int, Dict[int, Dict[str, int]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

# Reaction tracking
post_reactions: Dict[int, Dict[int, Dict[str, int]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
weekly_most_loved: Dict[int, List[Tuple[int, int, int, str]]] = defaultdict(list)
message_authors: Dict[int, Dict[int, int]] = defaultdict(dict)
weekly_reaction_totals: Dict[int, Dict[int, int]] = defaultdict(lambda: defaultdict(int))

# Economy & Rewards System
user_coins: Dict[int, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
user_titles: Dict[int, Dict[int, str]] = defaultdict(dict)
user_inventory: Dict[int, Dict[int, List[str]]] = defaultdict(lambda: defaultdict(list))
active_boosts: Dict[int, Dict[int, Dict[str, datetime]]] = defaultdict(lambda: defaultdict(dict))

# Weekly Challenges System
weekly_challenge_progress: Dict[int, Dict[int, Dict[str, int]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
weekly_challenge_completed: Dict[int, Dict[int, Set[str]]] = defaultdict(lambda: defaultdict(set))
current_weekly_challenges: Set[str] = set()

# User join dates for badges
user_join_dates: Dict[int, Dict[int, datetime]] = defaultdict(dict)

# Referral System
user_referral_codes: Dict[int, Dict[int, str]] = defaultdict(dict)  # chat_id -> user_id -> referral_code
referral_relationships: Dict[int, Dict[int, int]] = defaultdict(dict)  # chat_id -> referee_id -> referrer_id
referral_stats: Dict[int, Dict[int, Dict[str, int]]] = defaultdict(lambda: defaultdict(lambda: {"total_referrals": 0, "active_referrals": 0, "pending_rewards": 0}))
weekly_referral_count: Dict[int, Dict[int, int]] = defaultdict(lambda: defaultdict(int))  # For weekly challenge
referral_milestones_claimed: Dict[int, Set[Tuple[int, int]]] = defaultdict(set)  # chat_id -> set of (referrer_id, referee_id) pairs

class Ach:
    FirstPost = "🎉 First Post"
    HundredUploads = "💯 100 Uploads"
    TopPosterDay = "🏆 Top Poster (Daily)"
    StreakMaster3 = "🔥 Streak Master (3 days)"
    StreakMaster7 = "🚀 Streak Master (7 days)"
    StreakMaster30 = "👑 Streak Master (30 days)"
    WeeklyWarrior = "⚔️ Weekly Warrior"
    ReactionKing = "👑 Reaction King"
    ConsistentPoster = "📅 Consistent Poster"
    EarlyBird = "🌅 Early Bird"
    NightOwl = "🦉 Night Owl"
    PhotoMaster = "📸 Photo Master"
    VideoMaster = "🎥 Video Master"
    LinkMaster = "🔗 Link Master"
    LoveGiver = "❤️ Love Giver"
    ReferralMaster = "🤝 Referral Master"
    CommunityBuilder = "🏗️ Community Builder"

achievements: Dict[int, Dict[int, Set[str]]] = defaultdict(lambda: defaultdict(set))

# === XP & Levels ===
xp_levels: Dict[int, Dict[int, int]] = defaultdict(lambda: defaultdict(int))

def calc_level(xp: int) -> int:
    return int((xp ** 0.5) // 1)

def get_user_title(chat_id: int, user_id: int) -> str:
    if user_id in user_titles[chat_id]:
        return user_titles[chat_id][user_id]
    
    xp = xp_levels[chat_id][user_id]
    for threshold, title in reversed(TITLE_THRESHOLDS):
        if xp >= threshold:
            return title
    return TITLE_THRESHOLDS[0][1]

def has_active_boost(chat_id: int, user_id: int, boost_type: str) -> bool:
    if boost_type in active_boosts[chat_id][user_id]:
        expiry = active_boosts[chat_id][user_id][boost_type]
        if now_utc() < expiry:
            return True
        else:
            del active_boosts[chat_id][user_id][boost_type]
    return False

def get_multiplier(chat_id: int, user_id: int, reward_type: str) -> float:
    multiplier = 1.0
    if reward_type == "xp" and has_active_boost(chat_id, user_id, "xp_boost"):
        multiplier *= 2.0
    elif reward_type == "coins" and has_active_boost(chat_id, user_id, "coin_boost"):
        multiplier *= 2.0
    elif reward_type == "referral" and has_active_boost(chat_id, user_id, "referral_boost"):
        multiplier *= 2.0
    return multiplier

def select_weekly_challenges() -> Set[str]:
    return set(random.sample(list(WEEKLY_CHALLENGES.keys()), min(3, len(WEEKLY_CHALLENGES))))

def generate_referral_code(user_id: int, chat_id: int) -> str:
    """Generate a unique referral code for a user"""
    data = f"{user_id}:{chat_id}:{now_utc().timestamp()}"
    hash_obj = hashlib.sha256(data.encode())
    hash_hex = hash_obj.hexdigest()[:12]  # Take first 12 characters
    return f"REF{hash_hex.upper()}"

def get_user_referral_code(chat_id: int, user_id: int) -> str:
    """Get or create a referral code for a user"""
    if user_id not in user_referral_codes[chat_id]:
        user_referral_codes[chat_id][user_id] = generate_referral_code(user_id, chat_id)
    return user_referral_codes[chat_id][user_id]

def find_user_by_referral_code(chat_id: int, code: str) -> int:
    """Find user ID by referral code"""
    for user_id, user_code in user_referral_codes[chat_id].items():
        if user_code == code:
            return user_id
    return None

# ========= UTIL =========
def now_utc() -> datetime:
    return datetime.now(UTC)

def escape_html(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def fmt_span(td: timedelta) -> str:
    total_seconds = int(td.total_seconds())
    if total_seconds < 0:
        total_seconds = 0
    days, rem = divmod(total_seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    if days > 0: return f"{days}d"
    if hours > 0: return f"{hours}h"
    if minutes > 0: return f"{minutes}m"
    return f"{seconds}s"

async def mention(app: Application, chat_id: int, user_id: int) -> str:
    try:
        cm = await app.bot.get_chat_member(chat_id, user_id)
        name = cm.user.first_name or cm.user.username or "User"
        return f'<a href="tg://user?id={user_id}">{escape_html(name)}</a>'
    except Exception:
        return f'<a href="tg://user?id={user_id}">User</a>'

async def reply_in_same_topic(update: Update, text: str, parse_mode=ParseMode.HTML):
    msg = update.effective_message
    thread_id = getattr(msg, "message_thread_id", None)
    if thread_id:
        await msg.chat.send_message(text=text, parse_mode=parse_mode, message_thread_id=thread_id)
    else:
        await msg.chat.send_message(text=text, parse_mode=parse_mode)

async def safe_notify(context: ContextTypes.DEFAULT_TYPE, chat_id: int, html: str):
    max_attempts = 5
    delay = 1.5
    for attempt in range(1, max_attempts + 1):
        try:
            await context.bot.send_message(chat_id, html, parse_mode=ParseMode.HTML)
            return
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after + 0.5)
        except (TimedOut, NetworkError):
            await asyncio.sleep(delay)
            delay *= 2
        except Forbidden as e:
            print(f"Notify forbidden ({chat_id}): {e}")
            return
        except Exception as ex:
            print(f"Notify fail ({chat_id}) attempt {attempt}: {ex}")
            await asyncio.sleep(delay)
            delay *= 2
    print(f"Notify ultimately failed after {max_attempts} attempts: chat {chat_id}")

def content_delta(message) -> int:
    if message.photo:
        return PTS_PHOTO
    if message.video:
        return PTS_VIDEO
    if message.document:
        return PTS_DOC
    if message.text and ("http://" in message.text.lower() or "https://" in message.text.lower()):
        return PTS_LINK
    if message.text:
        return 1
    return 0

def get_content_type(message) -> str:
    if message.photo:
        return "photo"
    if message.video:
        return "video"
    if message.document:
        return "document"
    if message.text and ("http://" in message.text.lower() or "https://" in message.text.lower()):
        return "link"
    return "text"

def award_coins(chat_id: int, user_id: int, amount: int, reason: str = "", reward_type: str = "coins"):
    multiplier = get_multiplier(chat_id, user_id, reward_type)
    final_amount = int(amount * multiplier)
    user_coins[chat_id][user_id] += final_amount
    return final_amount

def update_streak(chat_id: int, user_id: int):
    today = now_utc().date()
    last_post = last_post_date[chat_id].get(user_id)
    
    if last_post:
        last_date = last_post.date()
        days_diff = (today - last_date).days
        
        if days_diff == 1:
            user_streaks[chat_id][user_id] += 1
        elif days_diff == 0:
            pass
        else:
            user_streaks[chat_id][user_id] = 1
    else:
        user_streaks[chat_id][user_id] = 1
    
    last_post_date[chat_id][user_id] = now_utc()

async def process_referral_signup(context: ContextTypes.DEFAULT_TYPE, chat_id: int, referee_id: int, referrer_id: int):
    """Process a new referral signup"""
    # Award welcome bonus to new member
    welcome_coins = award_coins(chat_id, referee_id, COIN_REFERRAL_WELCOME, "Referral welcome bonus")
    
    # Award signup bonus to referrer
    signup_coins = award_coins(chat_id, referrer_id, COIN_REFERRAL_SIGNUP, "Referral signup bonus", "referral")
    
    # Update referral stats
    referral_stats[chat_id][referrer_id]["total_referrals"] += 1
    weekly_referral_count[chat_id][referrer_id] += 1
    
    # Store referral relationship
    referral_relationships[chat_id][referee_id] = referrer_id
    
    # Notify both users
    referrer_mention = await mention(context.application, chat_id, referrer_id)
    referee_mention = await mention(context.application, chat_id, referee_id)
    
    await safe_notify(
        context, 
        chat_id, 
        f"🤝 <b>Referral Success!</b>\n"
        f"• {referee_mention} joined using {referrer_mention}'s referral code!\n"
        f"• {referee_mention} earned {welcome_coins} welcome coins! 💰\n"
        f"• {referrer_mention} earned {signup_coins} referral coins! 🎉"
    )

async def check_referral_milestone(context: ContextTypes.DEFAULT_TYPE, chat_id: int, referee_id: int):
    """Check if a referred user has reached the activity milestone"""
    if referee_id not in referral_relationships[chat_id]:
        return
    
    referrer_id = referral_relationships[chat_id][referee_id]
    milestone_key = (referrer_id, referee_id)
    
    # Check if milestone already claimed
    if milestone_key in referral_milestones_claimed[chat_id]:
        return
    
    # Check if referee has reached the activity threshold
    total_posts = total_content_count[chat_id][referee_id]
    if total_posts >= REFERRAL_ACTIVITY_THRESHOLD:
        # Award milestone bonus to referrer
        milestone_coins = award_coins(chat_id, referrer_id, COIN_REFERRAL_MILESTONE, "Referral milestone bonus", "referral")
        
        # Update stats
        referral_stats[chat_id][referrer_id]["active_referrals"] += 1
        referral_milestones_claimed[chat_id].add(milestone_key)
        
        # Notify
        referrer_mention = await mention(context.application, chat_id, referrer_id)
        referee_mention = await mention(context.application, chat_id, referee_id)
        
        await safe_notify(
            context,
            chat_id,
            f"🎯 <b>Referral Milestone!</b>\n"
            f"{referee_mention} became an active member!\n"
            f"{referrer_mention} earned {milestone_coins} milestone coins! 🏆"
        )
        
        # Check for referral achievements
        active_referrals = referral_stats[chat_id][referrer_id]["active_referrals"]
        if active_referrals == 10:
            await grant_ach(context, chat_id, referrer_id, Ach.ReferralMaster, "🤝 <b>Referral Master</b> — 10 active referrals!")
            # Also unlock Referral Champion badge
            if "🤝 Referral Champion" not in achievements[chat_id][referrer_id]:
                achievements[chat_id][referrer_id].add("🤝 Referral Champion")
                await safe_notify(context, chat_id, f"🤝 {(await mention(context.application, chat_id, referrer_id))} unlocked badge: <b>Referral Champion</b> — 10+ active referrals! 🎉")
        if active_referrals == 25:
            await grant_ach(context, chat_id, referrer_id, Ach.CommunityBuilder, "🏗️ <b>Community Builder</b> — 25 active referrals!")
            # Also unlock Community Builder badge
            if "🏗️ Community Builder" not in achievements[chat_id][referrer_id]:
                achievements[chat_id][referrer_id].add("🏗️ Community Builder")
                await safe_notify(context, chat_id, f"🏗️ {(await mention(context.application, chat_id, referrer_id))} unlocked badge: <b>Community Builder</b> — 25+ active referrals! 🎉")

async def cmd_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    uid = update.effective_user.id
    
    parts = context.args 
    if not parts:
        # Show referral stats and code
        referral_code = get_user_referral_code(cid, uid)
        stats = referral_stats[cid][uid]
        
        # Get list of referred users
        referred_users = []
        for referee_id, referrer_id in referral_relationships[cid].items():
            if referrer_id == uid:
                try:
                    referee_mention = await mention(context.application, cid, referee_id)
                    posts = total_content_count[cid][referee_id]
                    status = "✅ Active" if posts >= REFERRAL_ACTIVITY_THRESHOLD else f"📊 {posts}/{REFERRAL_ACTIVITY_THRESHOLD} posts"
                    referred_users.append(f"  • {referee_mention} ({status})")
                except:
                    continue
        
        referred_text = "\n".join(referred_users) if referred_users else "  None yet"
        
        # Active boosts
        referral_boost = ""
        if has_active_boost(cid, uid, "referral_boost"):
            expiry = active_boosts[cid][uid]["referral_boost"]
            time_left = expiry - now_utc()
            referral_boost = f"\n🚀 <b>Referral Boost Active:</b> 2x rewards ({fmt_span(time_left)})"
        
        referral_text = (
            f"🤝 <b>Your Referral System</b>\n\n"
            f"📋 <b>Your Code:</b> <code>{referral_code}</code>\n"
            f"📊 <b>Stats:</b>\n"
            f"  • Total Referrals: {stats['total_referrals']}\n"
            f"  • Active Referrals: {stats['active_referrals']}\n"
            f"  • Weekly Referrals: {weekly_referral_count[cid][uid]}\n\n"
            f"👥 <b>Your Referrals:</b>\n{referred_text}\n\n"
            f"💰 <b>Rewards:</b>\n"
            f"  • Sign-up Bonus: {COIN_REFERRAL_SIGNUP} coins\n"
            f"  • Activity Milestone: {COIN_REFERRAL_MILESTONE} coins\n"
            f"  • New Member Welcome: {COIN_REFERRAL_WELCOME} coins\n\n"
            f"📝 <b>How to Use:</b>\n"
            f"Share your code with friends! When they join and use your code with "
            f"<code>/referral use {referral_code}</code>, you both get rewards!\n"
            f"💡 They must use it within 24 hours of joining."
            f"{referral_boost}"
        )
        
        await reply_in_same_topic(update, referral_text)
        
    elif len(parts) >= 2 and parts[0].lower() == "use":
        referral_code = parts[1].upper()
        
        # Check if user already used a referral code
        if uid in referral_relationships[cid]:
            await reply_in_same_topic(update, "❌ You have already used a referral code!")
            return
        
        # Check if user is trying to use their own code
        user_code = get_user_referral_code(cid, uid)
        if referral_code == user_code:
            await reply_in_same_topic(update, "❌ You cannot use your own referral code!")
            return
        
        # Find the referrer
        referrer_id = find_user_by_referral_code(cid, referral_code)
        if not referrer_id:
            await reply_in_same_topic(update, "❌ Invalid referral code!")
            return
        
        # Check if user joined recently (within 24 hours)
        if uid in user_join_dates[cid]:
            join_date = user_join_dates[cid][uid]
            time_since_join = now_utc() - join_date
            if time_since_join > timedelta(hours=24):
                await reply_in_same_topic(update, "❌ Referral codes must be used within 24 hours of joining!")
                return
        else:
            await reply_in_same_topic(update, "❌ Referral codes are only for new members!")
            return
        
        # Process the referral
        await process_referral_signup(context, cid, uid, referrer_id)
        
    else:
        await reply_in_same_topic(
            update,
            "🤝 <b>Referral System Usage</b>\n\n"
            "📋 <code>/referral</code> - View your referral code & stats\n"
            "🎯 <code>/referral use [CODE]</code> - Use someone's referral code\n\n"
            "💡 <b>Tips:</b>\n"
            "• Share your code with friends to earn rewards!\n"
            "• New members get welcome bonuses\n"
            "• You get milestone bonuses when they become active\n"
            "• Referral codes must be used within 24h of joining"
        )

async def cmd_streak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    uid = update.effective_user.id
    
    streak = user_streaks[cid][uid]
    
    protection = ""
    if has_active_boost(cid, uid, "streak_freeze"):  # Changed from "streak_protection" to match shop item
        expiry = active_boosts[cid][uid]["streak_freeze"]
        time_left = expiry - now_utc()
        protection = f" 🛡️ (Protected for {fmt_span(time_left)})"
    
    if streak == 0:
        await reply_in_same_topic(update, f"🔥 No active streak. Start posting daily to build a streak! 💪{protection}")
    else:
        emoji = "🚀" if streak >= 7 else "🔥" if streak >= 3 else "💪"
        await reply_in_same_topic(update, f"🔥 Current streak: <b>{streak} days</b> {emoji}{protection}")

async def cmd_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    uid = update.effective_user.id
    
    # Get user stats
    xp = xp_levels[cid][uid]
    level = calc_level(xp)
    coins = user_coins[cid][uid]
    title = get_user_title(cid, uid)
    streak = user_streaks[cid][uid]
    total_posts = total_content_count[cid][uid]
    weekly_posts = weekly_content_count[cid][uid]
    daily_posts = daily_content_count[cid][uid]
    
    # Achievement count
    user_achievements = achievements[cid][uid]
    achievement_count = len(user_achievements)
    
    # Referral stats
    referral_stats_user = referral_stats[cid][uid]
    referral_code = get_user_referral_code(cid, uid)
    
    # Content breakdown
    content_breakdown = []
    for content_type, count in content_type_count[cid][uid].items():
        if count > 0:
            emoji_map = {"photo": "📸", "video": "🎥", "document": "📄", "link": "🔗", "text": "💬"}
            content_breakdown.append(f"{emoji_map.get(content_type, '📄')} {count}")
    
    content_text = " | ".join(content_breakdown) if content_breakdown and all(count > 0 for count in content_type_count[cid][uid].values()) else "None yet"
    
    # Active boosts
    boosts = []
    for boost_type, expiry in active_boosts[cid][uid].items():
        if now_utc() < expiry:
            time_left = expiry - now_utc()
            boosts.append(f"{boost_type.replace('_', ' ').title()} ({fmt_span(time_left)})")
    
    boost_text = f"\n🚀 <b>Active Boosts:</b> " + ", ".join(boosts) if boosts else ""
    
    # Weekly challenges progress
    challenge_progress = []
    for challenge_id in current_weekly_challenges:
        if challenge_id in WEEKLY_CHALLENGES:
            challenge = WEEKLY_CHALLENGES[challenge_id]
            progress = weekly_challenge_progress[cid][uid][challenge_id]
            completed = challenge_id in weekly_challenge_completed[cid][uid]
            status = "✅" if completed else f"{progress}/{challenge['target']}"
            challenge_progress.append(f"{challenge['emoji']} {status}")
    
    challenge_text = "\n🎯 <b>Weekly Challenges:</b> " + " | ".join(challenge_progress) if challenge_progress else ""
    
    # Join date info
    join_info = ""
    if uid in user_join_dates[cid]:
        join_date = user_join_dates[cid][uid]
        days_member = (now_utc() - join_date).days
        join_info = f"\n📅 <b>Member for:</b> {days_member} days"
    
    # Referral info
    referral_info = (
        f"\n🤝 <b>Referrals:</b> {referral_stats_user['active_referrals']}/{referral_stats_user['total_referrals']} active\n"
        f"📋 <b>Your Code:</b> <code>{referral_code}</code>"
    )
    
    me = await mention(context.application, cid, uid)
    
    profile_text = (
        f"👤 <b>Profile: {me}</b>\n\n"
        f"⭐ <b>Level:</b> {level} (XP: {xp})\n"
        f"👑 <b>Title:</b> {title}\n"
        f"💰 <b>Coins:</b> {coins}\n"
        f"🔥 <b>Streak:</b> {streak} days\n"
        f"🏅 <b>Achievements:</b> {achievement_count}\n\n"
        f"📊 <b>Posts:</b> Today: {daily_posts} | Week: {weekly_posts} | Total: {total_posts}\n"
        f"📈 <b>Content:</b> {content_text}"
        f"{join_info}"
        f"{referral_info}"
        f"{boost_text}"
        f"{challenge_text}"
    )
    
    await reply_in_same_topic(update, profile_text)

# ========= ACHIEVEMENTS =========
async def grant_ach(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int, ach_name: str, announce: str):
    has = achievements[chat_id][user_id]
    if ach_name in has:
        return
    has.add(ach_name)
    coins_earned = award_coins(chat_id, user_id, 25, f"Achievement: {ach_name}")
    await safe_notify(context, chat_id, f"🏅 {(await mention(context.application, chat_id, user_id))} unlocked: {announce} (+{coins_earned} coins!)")

async def check_achievements(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int, content_type: str):
    total = total_content_count[chat_id][user_id]
    streak = user_streaks[chat_id][user_id]
    
    if total == 1:
        await grant_ach(context, chat_id, user_id, Ach.FirstPost, "🎉 <b>First Post</b> — nice start!")
    if total == 100:
        await grant_ach(context, chat_id, user_id, Ach.HundredUploads, "💯 <b>100 Uploads</b> — consistent grinder!")
    
    if streak == 3:
        await grant_ach(context, chat_id, user_id, Ach.StreakMaster3, "🔥 <b>3-Day Streak</b> — keep it up!")
    elif streak == 7:
        await grant_ach(context, chat_id, user_id, Ach.StreakMaster7, "🚀 <b>7-Day Streak</b> — you're on fire!")
    elif streak == 30:
        await grant_ach(context, chat_id, user_id, Ach.StreakMaster30, "👑 <b>30-Day Streak</b> — legendary dedication!")

    # Content type achievements
    content_type_count[chat_id][user_id][content_type] += 1
    
    if content_type == "photo" and content_type_count[chat_id][user_id]["photo"] == 50:
        await grant_ach(context, chat_id, user_id, Ach.PhotoMaster, "📸 <b>Photo Master</b> — 50 photos shared!")
    elif content_type == "video" and content_type_count[chat_id][user_id]["video"] == 25:
        await grant_ach(context, chat_id, user_id, Ach.VideoMaster, "🎥 <b>Video Master</b> — 25 videos shared!")
    elif content_type == "link" and content_type_count[chat_id][user_id]["link"] == 30:
        await grant_ach(context, chat_id, user_id, Ach.LinkMaster, "🔗 <b>Link Master</b> — 30 links shared!")
    
    # Time-based achievements
    current_hour = now_utc().hour
    if 6 <= current_hour <= 9:  # Early Bird (6 AM - 9 AM)
        if "EarlyBird" not in achievements[chat_id][user_id]:
            await grant_ach(context, chat_id, user_id, Ach.EarlyBird, "🌅 <b>Early Bird</b> — posted in the morning!")
    elif 22 <= current_hour or current_hour <= 4:  # Night Owl (10 PM - 4 AM)
        if "NightOwl" not in achievements[chat_id][user_id]:
            await grant_ach(context, chat_id, user_id, Ach.NightOwl, "🦉 <b>Night Owl</b> — posted late at night!")
    
    # Consistent Poster - posts for 7 consecutive days
    if streak >= 7:
        if "ConsistentPoster" not in achievements[chat_id][user_id]:
            await grant_ach(context, chat_id, user_id, Ach.ConsistentPoster, "📅 <b>Consistent Poster</b> — 7 days of posting!")
    
    # Check for badge unlocks
    weekly_posts = weekly_content_count[chat_id][user_id]
    
    # Content King badge (50+ weekly posts)
    if weekly_posts >= 50 and "👑 Content King" not in achievements[chat_id][user_id]:
        achievements[chat_id][user_id].add("👑 Content King")
        await safe_notify(context, chat_id, f"👑 {(await mention(context.application, chat_id, user_id))} unlocked badge: <b>Content King</b> — 50+ weekly posts! 🎉")
    
    # Consistency Champion badge (14+ day streak)
    if streak >= 14 and "🏆 Consistency Champion" not in achievements[chat_id][user_id]:
        achievements[chat_id][user_id].add("🏆 Consistency Champion")
        await safe_notify(context, chat_id, f"🏆 {(await mention(context.application, chat_id, user_id))} unlocked badge: <b>Consistency Champion</b> — 14+ day streak! 🎉")
    
    # Early Adopter badge (first 10 members)
    total_users = len(user_join_dates[chat_id])
    if total_users <= 10 and user_id in user_join_dates[chat_id] and "🚀 Early Adopter" not in achievements[chat_id][user_id]:
        achievements[chat_id][user_id].add("🚀 Early Adopter")
        await safe_notify(context, chat_id, f"🚀 {(await mention(context.application, chat_id, user_id))} unlocked badge: <b>Early Adopter</b> — among first 10 members! 🎉")
    
    # Check referral milestone after each post
    await check_referral_milestone(context, chat_id, user_id)

# ========= COMMANDS =========
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await reply_in_same_topic(update, HELP_TEXT)

async def cmd_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await reply_in_same_topic(update, RULES_TEXT)

async def cmd_chatid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await reply_in_same_topic(update, f"🆔 <b>Chat ID:</b> <code>{chat_id}</code>")

async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    top_posters = sorted(
        ((user_id, daily_content_count[cid][user_id]) for user_id in daily_content_count[cid]),
        key=lambda x: x[1], reverse=True
    )[:10]
    
    top_posters_text = ""
    if top_posters:
        poster_lines = []
        for user_id, count in top_posters:
            try:
                user_mention = await mention(context.application, cid, user_id)
                poster_lines.append(f"{user_mention}: {count} posts")
            except Exception as e:
                print(f"Error mentioning user {user_id}: {e}")
                poster_lines.append(f"User {user_id}: {count} posts")
        top_posters_text = "\n".join(poster_lines)
    else:
        top_posters_text = "No posts yet."

    today_utc = now_utc().strftime("%Y-%m-%d")
    
    total_posts_today = sum(daily_content_count[cid].values())
    active_users_today = len(daily_content_count[cid])
    
    await reply_in_same_topic(
        update,
        f"📊 <b>Today's Stats</b> (UTC: {today_utc})\n"
        f"Total Posts: {total_posts_today}\n"
        f"Active Users: {active_users_today}\n\n"
        f"🏆 <b>Top Posters Today</b>:\n{top_posters_text}"
    )

async def cmd_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    top_posters = sorted(
        ((user_id, daily_content_count[cid][user_id]) for user_id in daily_content_count[cid]),
        key=lambda x: x[1], reverse=True
    )[:5]
    
    if not top_posters:
        await reply_in_same_topic(update, "🏆 No posts today yet! Be the first to share something!")
        return
    
    top_text = []
    for i, (user_id, count) in enumerate(top_posters, 1):
        emoji = ["🥇", "🥈", "🥉", "🏅", "⭐"][min(i-1, 4)]
        try:
            name = await mention(context.application, cid, user_id)
            top_text.append(f"{emoji} {name}: <b>{count}</b> posts")
        except Exception as e:
            print(f"Error mentioning user {user_id}: {e}")
            top_text.append(f"{emoji} User {user_id}: <b>{count}</b> posts")
    
    await reply_in_same_topic(
        update,
        f"🏆 <b>Today's Top Posters</b>\n\n" + "\n".join(top_text)
    )

async def cmd_achievements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    uid = update.effective_user.id
    
    user_achievements = achievements[cid][uid]
    
    if not user_achievements:
        await reply_in_same_topic(update, "🏅 You haven't unlocked any achievements yet! Start posting to earn badges! 💪")
        return
    
    ach_text = "\n".join(f"🏅 {ach}" for ach in sorted(user_achievements))
    
    await reply_in_same_topic(
        update,
        f"🏅 <b>Your Achievements</b> ({len(user_achievements)} unlocked)\n\n{ach_text}"
    )

async def cmd_badges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    uid = update.effective_user.id
    
    user_achievements = achievements[cid][uid]
    
    badges_text = "🎖️ <b>Available Badges</b>\n\n"
    
    for badge_id, badge in AVAILABLE_BADGES.items():
        status = "✅ UNLOCKED" if badge["name"] in user_achievements else f"🔒 {badge['requirement']}"
        badges_text += f"{badge['emoji']} <b>{badge['name']}</b>\n   {badge['description']}\n   {status}\n\n"
    
    await reply_in_same_topic(update, badges_text)

async def cmd_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    
    weekly_leaders = sorted(
        ((user_id, weekly_content_count[cid][user_id]) for user_id in weekly_content_count[cid]),
        key=lambda x: x[1], reverse=True
    )[:10]
    
    if not weekly_leaders:
        await reply_in_same_topic(update, "📈 No posts this week yet! Be the first to climb the leaderboard!")
        return
    
    leaderboard_text = []
    for i, (user_id, count) in enumerate(weekly_leaders, 1):
        emoji = ["🏆", "🥈", "🥉"] + ["🏅"] * 7
        name = await mention(context.application, cid, user_id)
        leaderboard_text.append(f"{emoji[min(i-1, len(emoji)-1)]} {name}: <b>{count}</b> posts")
    
    await reply_in_same_topic(
        update,
        f"📈 <b>Weekly Leaderboard</b>\n\n" + "\n".join(leaderboard_text)
    )

async def cmd_reactions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    
    reaction_leaders = sorted(
        ((user_id, weekly_reaction_totals[cid][user_id]) for user_id in weekly_reaction_totals[cid]),
        key=lambda x: x[1], reverse=True
    )[:5]
    
    if not reaction_leaders:
        await reply_in_same_topic(update, "❤️ No reactions tracked this week yet! Start reacting to posts to spread the love!")
        return
    
    reaction_text = []
    for user_id, reactions in reaction_leaders:
        name = await mention(context.application, cid, user_id)
        reaction_text.append(f"❤️ {name}: <b>{reactions}</b> reactions received")
    
    await reply_in_same_topic(
        update,
        f"❤️ <b>Weekly Reaction Report</b>\n\n" + "\n".join(reaction_text)
    )

async def cmd_ranking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    
    all_time_leaders = sorted(
        ((user_id, total_content_count[cid][user_id]) for user_id in total_content_count[cid]),
        key=lambda x: x[1], reverse=True
    )[:10]
    
    if not all_time_leaders:
        await reply_in_same_topic(update, "🏅 No content posted yet! Be the first to earn a spot in the all-time rankings!")
        return
    
    ranking_text = []
    for i, (user_id, count) in enumerate(all_time_leaders, 1):
        emoji = ["👑", "🥈", "🥉"] + ["🏅"] * 7
        name = await mention(context.application, cid, user_id)
        level = calc_level(xp_levels[cid][user_id])
        ranking_text.append(f"{emoji[min(i-1, len(emoji)-1)]} {name}: <b>{count}</b> posts (Level {level})")
    
    await reply_in_same_topic(
        update,
        f"🏅 <b>All-Time Rankings</b>\n\n" + "\n".join(ranking_text)
    )

async def cmd_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    uid = update.effective_user.id
    
    parts = context.args
    if not parts:
        current_title = get_user_title(cid, uid)
        await reply_in_same_topic(
            update,
            f"👑 Your current title: <b>{current_title}</b>\n\n"
            f"Use <code>/title set [custom_title]</code> to set a custom title (requires Custom Title item)\n"
            f"Use <code>/title reset</code> to reset to level-based title"
        )
    elif len(parts) >= 2 and parts[0] == "set":
        if "Custom Title" in user_inventory[cid][uid]:
            custom_title = " ".join(parts[1:])[:30]  # Limit to 30 chars
            user_titles[cid][uid] = custom_title
            user_inventory[cid][uid].remove("Custom Title")
            await reply_in_same_topic(update, f"✅ Title set to: <b>{custom_title}</b>")
        else:
            await reply_in_same_topic(update, "❌ You need to purchase a Custom Title from the shop first!")
    elif len(parts) == 1 and parts[0] == "reset":
        if uid in user_titles[cid]:
            del user_titles[cid][uid]
            new_title = get_user_title(cid, uid)
            await reply_in_same_topic(update, f"✅ Title reset to: <b>{new_title}</b>")
        else:
            await reply_in_same_topic(update, "ℹ️ You already have the default level-based title!")

async def cmd_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    uid = update.effective_user.id
    coins = user_coins[cid][uid]
    me = await mention(context.application, cid, uid)
    
    boosts = []
    for boost_type, expiry in active_boosts[cid][uid].items():
        if now_utc() < expiry:
            time_left = expiry - now_utc()
            boosts.append(f"⚡ {boost_type.replace('_', ' ').title()} ({fmt_span(time_left)})")
    
    boost_text = f"\n\n<b>Active Boosts:</b>\n" + "\n".join(boosts) if boosts else ""
    boost_text = f"\n\n<b>Active Boosts:</b>\n" + ", ".join(boosts) if boosts else ""
    
    await reply_in_same_topic(update, f"💰 {me} — Balance: <b>{coins}</b> coins{boost_text}")

async def cmd_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    uid = update.effective_user.id
    
    parts = context.args
    if not parts:
        items_text = []
        for item_id, item in SHOP_ITEMS.items():
            items_text.append(f"{item['emoji']} <b>{item['name']}</b> — {item['price']} coins\n   {item['description']}")
        
        shop_text = (
            f"🛒 <b>Rewards Shop</b>\n"
            f"💰 Your balance: <b>{user_coins[cid][uid]}</b> coins\n\n"
            + "\n\n".join(items_text) + "\n\n"
            f"Use <code>/shop buy [item_name]</code> to purchase!\n"
            f"Example: <code>/shop buy xp_boost</code>"
        )
        await reply_in_same_topic(update, shop_text)
        
    elif len(parts) >= 2 and parts[0] == "buy":
        item_id = parts[1].lower()
        if item_id in SHOP_ITEMS:
            item = SHOP_ITEMS[item_id]
            user_balance = user_coins[cid][uid]
            
            if user_balance >= item["price"]:
                user_coins[cid][uid] -= item["price"]
                
                if item["type"] == "boost":
                    expiry = now_utc() + item["duration"]
                    active_boosts[cid][uid][item_id] = expiry
                    await reply_in_same_topic(
                        update,
                        f"✅ Purchased <b>{item['name']}</b>! Active for {fmt_span(item['duration'])}. "
                        f"Remaining balance: <b>{user_coins[cid][uid]}</b> coins."
                    )
                elif item["type"] == "title":
                    user_inventory[cid][uid].append(item["name"])
                    await reply_in_same_topic(
                        update,
                        f"✅ Purchased <b>{item['name']}</b>! Use <code>/title set [custom_title]</code> to use it. "
                        f"Remaining balance: <b>{user_coins[cid][uid]}</b> coins."
                    )
                elif item["type"] == "protection":
                    expiry = now_utc() + item["duration"]
                    active_boosts[cid][uid]["streak_freeze"] = expiry  # Changed from "streak_protection"
                    await reply_in_same_topic(
                        update,
                        f"✅ Purchased <b>{item['name']}</b>! Your streak is protected for {fmt_span(item['duration'])}. "
                        f"Remaining balance: <b>{user_coins[cid][uid]}</b> coins."
                    )
                elif item["type"] == "cosmetic":
                    user_inventory[cid][uid].append(item["name"])
                    await reply_in_same_topic(
                        update,
                        f"✅ Purchased <b>{item['name']}</b>! It has been added to your inventory. "
                        f"Remaining balance: <b>{user_coins[cid][uid]}</b> coins."
                    )
            else:
                await reply_in_same_topic(update, f"❌ Insufficient coins! You need <b>{item['price']}</b> coins but have <b>{user_balance}</b>.")
        else:
            await reply_in_same_topic(update, "❌ Item not found! Use <code>/shop</code> to see available items.")

async def cmd_challenges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    uid = update.effective_user.id
    
    if not current_weekly_challenges:
        await reply_in_same_topic(update, "🎯 No active challenges this week! Check back soon.")
        return
    
    challenge_text = "🎯 <b>Weekly Challenges</b>\n\n"
    
    for challenge_id in current_weekly_challenges:
        challenge = WEEKLY_CHALLENGES[challenge_id]
        progress = weekly_challenge_progress[cid][uid][challenge_id]
        completed = challenge_id in weekly_challenge_completed[cid][uid]
        
        status = "✅ COMPLETED" if completed else f"📊 Progress: {progress}/{challenge['target']}"
        
        challenge_text += (
            f"{challenge['emoji']} <b>{challenge['name']}</b>\n"
            f"   {challenge['description']}\n"
            f"   Reward: {challenge['reward']} coins\n"
            f"   {status}\n\n"
        )
    
    await reply_in_same_topic(update, challenge_text)

async def cmd_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    uid = update.effective_user.id
    
    xp = xp_levels[cid][uid]
    level = calc_level(xp)
    coins = user_coins[cid][uid]
    title = get_user_title(cid, uid)
    
    await reply_in_same_topic(
        update,
        f"⭐ {await mention(context.application, cid, uid)}\n"
        f"Level: <b>{level}</b> (XP: <b>{xp}</b>)\n"
        f"Coins: <b>{coins}</b>\n"
        f"Title: {title}"
    )

# ========= JOBS =========
async def job_new_member_enforcer(context: ContextTypes.DEFAULT_TYPE):
    now = now_utc()
    all_chats = list(known_chats)
    
    for chat_id in all_chats:
        try:
            overdue = []
            warn_list = []
            for uid, deadline in list(new_member_deadline[chat_id].items()):
                if now >= deadline:
                    overdue.append(uid)
                elif now >= deadline - NEW_MEMBER_WARN_BEFORE and uid not in new_member_warned[chat_id]:
                    warn_list.append(uid)
            
            # Warn new members before deadline
            for uid in warn_list:
                try:
                    name_link = await mention(context.application, chat_id, uid)
                    await safe_notify(context, chat_id, f"⚠️ {name_link} welcome! Please post something within 15 minutes to stay in the group.")
                    new_member_warned[chat_id].add(uid)
                except Exception as e:
                    print(f"Failed to warn new member {uid} in {chat_id}: {e}")
            
            # Remove overdue new members
            for uid in overdue:
                try:
                    await context.bot.ban_chat_member(chat_id, uid)
                    name_link = await mention(context.application, chat_id, uid)
                    await safe_notify(context, chat_id, f"👋 {name_link} was removed for not posting within the time limit.")
                    new_member_deadline[chat_id].pop(uid, None)
                    new_member_warned[chat_id].discard(uid)
                except Exception as e:
                    print(f"Failed to kick new member {uid} from {chat_id}: {e}")
                    
        except Exception as e:
            print(f"Error in new member enforcer for chat {chat_id}: {e}")

async def job_inactivity(context: ContextTypes.DEFAULT_TYPE):
    now = now_utc()
    all_chats = list(known_chats)
    
    for chat_id in all_chats:
        try:
            activity = last_activity_utc[chat_id]
            kick_list = []
            warn_list = []
            
            for uid, last_seen in list(activity.items()):
                if uid in new_member_deadline[chat_id]:
                    continue
                
                inactive_dur = now - last_seen
                if inactive_dur >= INACTIVITY_KICK_AT:
                    kick_list.append(uid)
                elif inactive_dur >= INACTIVITY_WARN_AT and uid not in warned_48h[chat_id]:
                    warn_list.append(uid)
            
            for uid in kick_list:
                try:
                    cm = await context.bot.get_chat_member(chat_id, uid)
                    if cm.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                        await context.bot.ban_chat_member(chat_id, uid)
                        name_link = await mention(context.application, chat_id, uid)
                        await safe_notify(context, chat_id, f"👋 {name_link} was removed for inactivity (72h).")
                        
                        activity.pop(uid, None)
                        warned_48h[chat_id].discard(uid)
                except Exception as e:
                    print(f"Failed to kick inactive user {uid} from {chat_id}: {e}")
            
            for uid in warn_list:
                try:
                    cm = await context.bot.get_chat_member(chat_id, uid)
                    if cm.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                        name_link = await mention(context.application, chat_id, uid)
                        await safe_notify(context, chat_id, f"⚠️ {name_link} you've been inactive for 48h! Post something within 24h or risk removal.")
                        warned_48h[chat_id].add(uid)
                except Exception as e:
                    print(f"Failed to warn inactive user {uid} in {chat_id}: {e}")
                    
        except Exception as e:
            print(f"Error in inactivity job for chat {chat_id}: {e}")

async def job_daily_top(context: ContextTypes.DEFAULT_TYPE):
    all_chats = list(known_chats)
    
    for chat_id in all_chats:
        try:
            daily = daily_content_count[chat_id]
            if daily:
                top_uid, top_score = max(daily.items(), key=lambda x: x[1])
                if top_score > 0:
                    await grant_ach(context, chat_id, top_uid, Ach.TopPosterDay, "🏆 <b>Top Poster (Daily)</b> — you dominated today!")
                    name_link = await mention(context.application, chat_id, top_uid)
                    await safe_notify(context, chat_id, f"🏆 <b>Daily Champion</b>\n{name_link} was today's top poster with <b>{top_score}</b> posts! 🎉")
            
            daily_content_count[chat_id].clear()
            
        except Exception as e:
            print(f"Error in daily top job for chat {chat_id}: {e}")

async def job_weekly_reset(context: ContextTypes.DEFAULT_TYPE):
    global current_weekly_challenges
    all_chats = list(known_chats)
    
    for chat_id in all_chats:
        try:
            weekly = weekly_content_count[chat_id]
            if weekly:
                top_uid, top_score = max(weekly.items(), key=lambda x: x[1])
                if top_score > 0:
                    await grant_ach(context, chat_id, top_uid, Ach.WeeklyWarrior, "⚔️ <b>Weekly Warrior</b> — you dominated this week!")
            
            weekly_content_count[chat_id].clear()
            weekly_reaction_totals[chat_id].clear()
            weekly_most_loved[chat_id].clear()
            weekly_challenge_progress[chat_id].clear()
            weekly_challenge_completed[chat_id].clear()
            weekly_referral_count[chat_id].clear()  # Clear weekly referral counts
            
        except Exception as e:
            print(f"Error in weekly reset job for chat {chat_id}: {e}")
    
    current_weekly_challenges = select_weekly_challenges()
    print(f"New weekly challenges selected: {current_weekly_challenges}")

async def job_streak_checker(context: ContextTypes.DEFAULT_TYPE):
    now = now_utc()
    today = now.date()
    all_chats = list(known_chats)
    
    for chat_id in all_chats:
        try:
            for uid, last_post in list(last_post_date[chat_id].items()):
                last_date = last_post.date()
                days_diff = (today - last_date).days
                
                if days_diff > 1:
                    if has_active_boost(chat_id, uid, "streak_freeze"):  # Changed from "streak_protection"
                        continue
                    else:
                        if user_streaks[chat_id][uid] > 0:
                            old_streak = user_streaks[chat_id][uid]
                            user_streaks[chat_id][uid] = 0
                            
                            if old_streak >= 7:
                                name_link = await mention(context.application, chat_id, uid)
                                await safe_notify(context, chat_id, f"💔 {name_link} your {old_streak}-day streak was broken due to inactivity. Start posting again to rebuild it! 💪")
                
        except Exception as e:
            print(f"Error in streak checker for chat {chat_id}: {e}")

# ========= REACTION HANDLERS =========
async def on_message_reaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle message reaction updates"""
    reaction_update = update.message_reaction
    if not reaction_update:
        return
    
    chat_id = reaction_update.chat.id
    message_id = reaction_update.message_id
    user_id = reaction_update.user.id
    
    if chat_id not in known_chats:
        return
    
    # Get the message author from our stored data
    if message_id not in message_authors[chat_id]:
        return
    
    author_id = message_authors[chat_id][message_id]
    
    # Skip if user is reacting to their own message
    if user_id == author_id:
        return
    
    # Calculate net reaction change
    old_reactions = reaction_update.old_reaction
    new_reactions = reaction_update.new_reaction
    
    old_count = len(old_reactions) if old_reactions else 0
    new_count = len(new_reactions) if new_reactions else 0
    
    reaction_delta = new_count - old_count
    
    if reaction_delta != 0:
        # Update reaction totals
        weekly_reaction_totals[chat_id][author_id] += reaction_delta
        
        # Track individual reaction counts for achievements
        if reaction_delta > 0:
            post_reactions[chat_id][message_id][user_id] += reaction_delta
            # Track for weekly most loved posts
            total_reactions_on_msg = sum(post_reactions[chat_id][message_id].values())
            weekly_most_loved[chat_id].append((message_id, author_id, total_reactions_on_msg, "❤️"))
        elif reaction_delta < 0:
            post_reactions[chat_id][message_id][user_id] = max(0, post_reactions[chat_id][message_id].get(user_id, 0) + reaction_delta)
        
        # Award coins for reactions received
        if reaction_delta > 0:
            coins_earned = award_coins(chat_id, author_id, COIN_REACTION_RECEIVED * reaction_delta, "Reaction received")
            
            # Update weekly challenge progress for social butterfly
            for challenge_id in current_weekly_challenges:
                if challenge_id == "social_butterfly":
                    weekly_challenge_progress[chat_id][author_id][challenge_id] += reaction_delta
                    
                    # Check if challenge completed
                    challenge = WEEKLY_CHALLENGES[challenge_id]
                    new_progress = weekly_challenge_progress[chat_id][author_id][challenge_id]
                    if new_progress >= challenge["target"] and challenge_id not in weekly_challenge_completed[chat_id][author_id]:
                        weekly_challenge_completed[chat_id][author_id].add(challenge_id)
                        challenge_coins = award_coins(chat_id, author_id, challenge["reward"], f"Challenge: {challenge['name']}")
                        await safe_notify(
                            context,
                            chat_id,
                            f"🎯 {(await mention(context.application, chat_id, author_id))} completed challenge: "
                            f"<b>{challenge['name']}</b>! Earned {challenge_coins} coins! 💰"
                        )
            
    # Check for reaction-related achievements
    total_reactions = weekly_reaction_totals[chat_id][author_id]
    if total_reactions >= 100:
        await grant_ach(context, chat_id, author_id, Ach.ReactionKing, "👑 <b>Reaction King</b> — 100+ reactions this week!")
        
        # Also check for Social Master badge (100+ weekly reactions)
        if "🌟 Social Master" not in achievements[chat_id][author_id]:
            achievements[chat_id][author_id].add("🌟 Social Master")
            await safe_notify(context, chat_id, f"🌟 {(await mention(context.application, chat_id, author_id))} unlocked badge: <b>Social Master</b> — 100+ weekly reactions! 🎉")            # Award Love Giver achievement to the reactor
            reactor_reactions_given = sum(1 for msg_reactions in post_reactions[chat_id].values() 
                                        for reactor, count in msg_reactions.items() if reactor == user_id and count > 0)
            if reactor_reactions_given >= 50:
                await grant_ach(context, chat_id, user_id, Ach.LoveGiver, "❤️ <b>Love Giver</b> — spread 50+ reactions!")

# ========= MESSAGE HANDLER (UPDATED) =========
async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user:
        return

    if chat.type not in ("group", "supergroup"):
        return

    known_chats.add(chat.id)

    # Store message author for reaction tracking
    if msg.message_id:
        message_authors[chat.id][msg.message_id] = user.id

    if msg.new_chat_members:
        for m in msg.new_chat_members:
            if m.is_bot:
                continue
            deadline = now_utc() + NEW_MEMBER_POST_WINDOW
            new_member_deadline[chat.id][m.id] = deadline
            user_join_dates[chat.id][m.id] = now_utc()  # Track join date

            name = m.first_name or m.username or "User"
            mention_html = f'<a href="tg://user?id={m.id}">{escape_html(name)}</a>'
            await reply_in_same_topic(
                update,
                f"👋 Welcome {mention_html}! Please post an <b>image</b>, <b>video</b>, <b>link</b> or <b>file</b> "
                f"within <b>{fmt_span(NEW_MEMBER_POST_WINDOW)}</b> or you'll be removed.\n\n"
                f"💡 <b>Pro tip:</b> If a friend referred you, use <code>/referral use [CODE]</code> to get bonus coins! 🤝"
            )
        return

    uid = user.id
    last_activity_utc[chat.id][uid] = now_utc()
    if uid in new_member_deadline[chat.id]:
        new_member_deadline[chat.id].pop(uid, None)
        new_member_warned[chat.id].discard(uid)
    warned_48h[chat.id].discard(uid)

    add = content_delta(msg)
    if add > 0:
        total_content_count[chat.id][uid] += add
        daily_content_count[chat.id][uid] += add
        weekly_content_count[chat.id][uid] += add
        
        update_streak(chat.id, uid)
        content_type = get_content_type(msg)
        
        coins_earned = award_coins(chat.id, uid, COIN_DAILY_POST, "Daily post")
        
        streak = user_streaks[chat.id][uid]
        if streak > 1:
            streak_bonus = award_coins(chat.id, uid, COIN_STREAK_BONUS, f"Streak bonus (Day {streak}")

        before_xp = xp_levels[chat.id][uid]
        xp_multiplier = get_multiplier(chat.id, uid, "xp")
        xp_gained = int(add * xp_multiplier)
        xp_levels[chat.id][uid] += xp_gained
        after_xp = xp_levels[chat.id][uid]
        before_lvl = calc_level(before_xp)
        after_lvl = calc_level(after_xp)
        
        if after_lvl > before_lvl:
            level_coins = award_coins(chat.id, uid, COIN_LEVEL_UP, f"Level up to {after_lvl}")
            await safe_notify(
                context,
                chat.id,
                f"🎉 {(await mention(context.application, chat.id, uid))} leveled up to <b>Level {after_lvl}</b>! "
                f"Earned {level_coins} coins! 💰"
            )

        # Update weekly challenge progress
        for challenge_id in current_weekly_challenges:
            if challenge_id in weekly_challenge_completed[chat.id][uid]:
                continue
                
            challenge = WEEKLY_CHALLENGES.get(challenge_id)
            if not challenge:
                continue
            
            progress = weekly_challenge_progress[chat.id][uid][challenge_id]
            
            if challenge["type"] == "posts":
                weekly_challenge_progress[chat.id][uid][challenge_id] += 1
            elif challenge["type"] == content_type:
                weekly_challenge_progress[chat.id][uid][challenge_id] += 1
            elif challenge["type"] == "streak" and streak >= challenge["target"]:
                weekly_challenge_progress[chat.id][uid][challenge_id] = streak
            elif challenge["type"] == "early_posts":
                current_hour = now_utc().hour
                if 6 <= current_hour <= 9:
                    weekly_challenge_progress[chat.id][uid][challenge_id] += 1
            elif challenge["type"] == "referrals":
                weekly_challenge_progress[chat.id][uid][challenge_id] = weekly_referral_count[chat.id][uid]
            
            # Check if challenge completed
            new_progress = weekly_challenge_progress[chat.id][uid][challenge_id]
            if new_progress >= challenge["target"] and challenge_id not in weekly_challenge_completed[chat.id][uid]:
                weekly_challenge_completed[chat.id][uid].add(challenge_id)
                challenge_coins = award_coins(chat.id, uid, challenge["reward"], f"Challenge: {challenge['name']}")
                await safe_notify(
                    context,
                    chat.id,
                    f"🎯 {(await mention(context.application, chat.id, uid))} completed challenge: "
                    f"<b>{challenge['name']}</b>! Earned {challenge_coins} coins! 💰"
                )

        await check_achievements(context, chat.id, uid, content_type)

# ========= MAIN APPLICATION =========
def main():
    """Run the bot."""
    global current_weekly_challenges
    
    # Initialize weekly challenges
    current_weekly_challenges = select_weekly_challenges()
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("rules", cmd_rules))
    application.add_handler(CommandHandler("chatid", cmd_chatid))
    application.add_handler(CommandHandler("stats", cmd_stats))
    application.add_handler(CommandHandler("achievements", cmd_achievements))
    application.add_handler(CommandHandler("top", cmd_top))
    application.add_handler(CommandHandler("badges", cmd_badges))
    application.add_handler(CommandHandler("leaderboard", cmd_leaderboard))
    application.add_handler(CommandHandler("reactions", cmd_reactions))
    application.add_handler(CommandHandler("ranking", cmd_ranking))
    application.add_handler(CommandHandler("level", cmd_level))
    application.add_handler(CommandHandler("streak", cmd_streak))
    application.add_handler(CommandHandler("profile", cmd_profile))
    application.add_handler(CommandHandler("coins", cmd_coins))
    application.add_handler(CommandHandler("shop", cmd_shop))
    application.add_handler(CommandHandler("challenges", cmd_challenges))
    application.add_handler(CommandHandler("title", cmd_title))
    application.add_handler(CommandHandler("referral", cmd_referral))
    
    # Register message handlers
    application.add_handler(MessageHandler(filters.ALL, on_message))
    application.add_handler(MessageReactionHandler(on_message_reaction))
    
    # Register job queue
    job_queue = application.job_queue
    
    # Schedule jobs
    job_queue.run_repeating(job_new_member_enforcer, interval=CHECK_INTERVAL, first=10)
    job_queue.run_repeating(job_inactivity, interval=CHECK_INTERVAL, first=30)
    job_queue.run_repeating(job_streak_checker, interval=STREAK_CHECK_INTERVAL, first=60)
    
    # Daily job at midnight UTC
    job_queue.run_daily(job_daily_top, time=time(0, 0, tzinfo=UTC))
    
    # Weekly job using run_repeating with 7-day interval (since run_weekly doesn't exist)
    job_queue.run_repeating(job_weekly_reset, interval=timedelta(days=7), first=timedelta(seconds=3600))  # Start after 1 hour
    
    print("Bot started! Press Ctrl+C to stop.")
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
