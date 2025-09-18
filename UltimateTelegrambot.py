#!/usr/bin/env python3
"""
Ultimate Telegram Bot - A comprehensive community bot with gamification features

Version: 1.0.0
Author: Community Contributors
License: MIT
Repository: https://github.com/realLuckyy/UltimateTelegramBot
Support: https://ko-fi.com/root

Features:
- Gamification with XP, levels, and achievements
- Economy system with coins and shop
- Referral program with bonuses
- Weekly challenges
- Community management and moderation
- Comprehensive statistics and leaderboards
"""

import asyncio
from datetime import datetime, timedelta, timezone, time
from collections import defaultdict
from typing import Dict, Set, List, Tuple
import random
import hashlib
import base64
import os

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
# Get token from environment variable or use placeholder
TOKEN = os.getenv('BOT_TOKEN', "PLEASE_SET_YOUR_BOT_TOKEN_HERE")

if TOKEN == "PLEASE_SET_YOUR_BOT_TOKEN_HERE":
    print("??  WARNING: Bot token not configured!")
    print("Please set your bot token by either:")
    print("1. Running: python setup.py")
    print("2. Setting environment variable: export BOT_TOKEN='your_token_here'")
    print("3. Editing this file and replacing TOKEN value")

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
    (0, "?? Newcomer"),
    (10, "?? Rookie"),
    (50, "? Regular"),
    (150, "?? Active"),
    (300, "?? Veteran"),
    (500, "?? Elite"),
    (1000, "?? Legend"),
    (2000, "?? Hall of Fame")
]

# Weekly challenges
WEEKLY_CHALLENGES = {
    "photo_spree": {
        "name": "?? Photo Spree",
        "description": "Share 20 photos this week",
        "target": 20,
        "type": "photo",
        "reward": 100,
        "emoji": "??"
    },
    "streak_keeper": {
        "name": "?? Streak Keeper",
        "description": "Maintain a 5+ day streak",
        "target": 5,
        "type": "streak",
        "reward": 75,
        "emoji": "??"
    },
    "social_butterfly": {
        "name": "?? Social Butterfly",
        "description": "Get 30 reactions on your posts",
        "target": 30,
        "type": "reactions",
        "reward": 80,
        "emoji": "??"
    },
    "content_creator": {
        "name": "?? Content Creator",
        "description": "Post 15 pieces of content",
        "target": 15,
        "type": "posts",
        "reward": 90,
        "emoji": "??"
    },
    "early_bird": {
        "name": "?? Early Bird",
        "description": "Post 5 times between 6-9 AM",
        "target": 5,
        "type": "early_posts",
        "reward": 60,
        "emoji": "??"
    },
    "referral_master": {
        "name": "?? Referral Master",
        "description": "Refer 3 new members this week",
        "target": 3,
        "type": "referrals",
        "reward": 150,
        "emoji": "??"
    }
}

# Shop items
SHOP_ITEMS = {
    "custom_badge": {
        "name": "??? Custom Badge",
        "description": "Get a personalized badge for your profile",
        "price": 200,
        "type": "cosmetic",
        "emoji": "???"
    },
    "xp_boost": {
        "name": "? XP Booster",
        "description": "2x XP for 24 hours",
        "price": 150,
        "type": "boost",
        "duration": timedelta(hours=24),
        "emoji": "?"
    },
    "title_unlock": {
        "name": "?? Custom Title",
        "description": "Unlock a special custom title",
        "price": 300,
        "type": "title",
        "emoji": "??"
    },
    "streak_freeze": {
        "name": "?? Streak Freeze",
        "description": "Protect your streak for 2 days",
        "price": 100,
        "type": "protection",
        "duration": timedelta(days=2),
        "emoji": "??"
    },
    "coin_boost": {
        "name": "?? Coin Multiplier",
        "description": "2x coins for 12 hours",
        "price": 120,
        "type": "boost",
        "duration": timedelta(hours=12),
        "emoji": "??"
    },
    "referral_boost": {
        "name": "?? Referral Booster",
        "description": "2x referral rewards for 48 hours",
        "price": 180,
        "type": "boost",
        "duration": timedelta(hours=48),
        "emoji": "??"
    }
}

# Available badges to unlock
AVAILABLE_BADGES = {
    "social_master": {
        "name": "?? Social Master",
        "description": "Get 100+ reactions in a week",
        "requirement": "100 weekly reactions",
        "emoji": "??"
    },
    "content_king": {
        "name": "?? Content King",
        "description": "Post 50+ times in a week", 
        "requirement": "50 weekly posts",
        "emoji": "??"
    },
    "early_adopter": {
        "name": "?? Early Adopter",
        "description": "One of the first 10 members",
        "requirement": "Be among first 10 members",
        "emoji": "??"
    },
    "consistency_champion": {
        "name": "?? Consistency Champion",
        "description": "Maintain 14+ day streak",
        "requirement": "14+ day posting streak",
        "emoji": "??"
    },
    "referral_champion": {
        "name": "?? Referral Champion",
        "description": "Successfully refer 10+ members",
        "requirement": "Refer 10+ active members",
        "emoji": "??"
    },
    "community_builder": {
        "name": "??? Community Builder",
        "description": "Refer 25+ members",
        "requirement": "Refer 25+ active members",
        "emoji": "???"
    }
}

# Text blocks
RULES_TEXT = (
    "?? <b>Rules</b>\n"
    "1?? Post Real content (images, videos, links, etc).\n"
    "2?? No selling / trading.\n"
    "3?? Respect other members.\n"
    "4?? Inactivity = warning ? kick.\n"
    "5?? This is a 18+ group.\n\n"
    "?? Stay active or you may be removed."
)

HELP_TEXT = (
    "?? <b>Strictly????Bot Commands</b>\n\n"
    "?? /rules ? Show group rules\n"
    "?? /chatid ? Display this group's Chat ID\n"
    "?? /stats ? Show daily stats & top posters\n"
    "?? /achievements ? Show your unlocked badges\n"
    "?? /top ? Show today's top posters\n"
    "? /level ? Show your XP & Level\n"
    "?? /streak ? Show your posting streak\n"
    "??? /badges ? Show available badges to unlock\n"
    "?? /leaderboard ? Show weekly leaderboard\n"
    "?? /reactions ? Show weekly reaction reports\n"
    "?? /profile ? Show complete user profile\n"
    "?? /ranking ? Show all-time rankings\n"
    "?? /coins ? Show your coin balance\n"
    "?? /shop ? Browse the rewards shop\n"
    "?? /challenges ? View weekly challenges\n"
    "?? /title ? Manage your title\n"
    "?? /referral ? Manage your referral code & stats\n"
    "?? /help ? Show this help menu\n\n"
    "?? Activity Rules:\n"
    "- New members must post within 1h or risk removal.\n"
    "- Inactive = Warn at 48h ? Kick at 72h.\n"
    "- Keep daily streaks for special rewards!\n"
    "- Complete challenges to earn coins! ??\n"
    "- React to posts to spread the love! ??\n"
    "- Invite friends with your referral code! ??\n"
    "- 18+ group only. Stay active!\n\n"
    "? <b>Support the Bot:</b> <a href='https://ko-fi.com/root'>Buy me a coffee</a> ?"
)