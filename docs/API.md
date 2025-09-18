# ?? API Reference & Command Guide

Complete reference for all commands, parameters, and API interactions.

## ?? Bot Commands Reference

### Basic Commands

#### `/help`
**Description**: Display comprehensive help menu with all available commands  
**Usage**: `/help`  
**Permissions**: All users  
**Response**: Multi-section help text with command categories  

#### `/rules`
**Description**: Show group rules and policies  
**Usage**: `/rules`  
**Permissions**: All users  
**Response**: Formatted rules text with activity requirements  

#### `/chatid`
**Description**: Display the current chat's unique identifier  
**Usage**: `/chatid`  
**Permissions**: All users  
**Response**: `?? Chat ID: -1001234567890`  

---

### User Profile & Statistics

#### `/profile`
**Description**: Show complete user profile with all statistics  
**Usage**: `/profile`  
**Permissions**: All users  
**Response Format**:
```
?? Profile: @username
? Level: 15 (XP: 225)
?? Title: ? Regular
?? Coins: 450
?? Streak: 7 days
?? Achievements: 8
?? Posts: Today: 3 | Week: 21 | Total: 156
?? Content: ?? 45 | ?? 12 | ?? 23 | ?? 76
?? Member for: 45 days
?? Referrals: 3/5 active
?? Your Code: REF123ABCDEF
```

#### `/level`
**Description**: Show current XP and level information  
**Usage**: `/level`  
**Permissions**: All users  
**Response**: Level, XP, coins, and current title  

#### `/coins`
**Description**: Show coin balance and active boosts  
**Usage**: `/coins`  
**Permissions**: All users  
**Response**: Current balance and any active multipliers/boosts  

#### `/streak`
**Description**: Show current posting streak  
**Usage**: `/streak`  
**Permissions**: All users  
**Response**: Current streak count and any active protection  

---

### Achievements & Badges

#### `/achievements`
**Description**: Show all unlocked achievements  
**Usage**: `/achievements`  
**Permissions**: All users  
**Response**: List of unlocked achievements with count  

#### `/badges`
**Description**: Show available badges and unlock requirements  
**Usage**: `/badges`  
**Permissions**: All users  
**Response**: All badges with unlock status and requirements  

---

### Statistics & Leaderboards

#### `/stats`
**Description**: Show daily group statistics and activity  
**Usage**: `/stats`  
**Permissions**: All users  
**Response Format**:
```
?? Today's Stats (UTC: 2024-01-15)
Total Posts: 45
Active Users: 12

?? Top Posters Today:
?? @user1: 8 posts
?? @user2: 6 posts
?? @user3: 5 posts
```

#### `/top`
**Description**: Show today's top 5 posters  
**Usage**: `/top`  
**Permissions**: All users  
**Response**: Ranked list of daily top contributors  

#### `/leaderboard`
**Description**: Show weekly top 10 posters  
**Usage**: `/leaderboard`  
**Permissions**: All users  
**Response**: Weekly rankings with post counts  

#### `/ranking`
**Description**: Show all-time top 10 contributors  
**Usage**: `/ranking`  
**Permissions**: All users  
**Response**: All-time rankings with levels and total posts  

#### `/reactions`
**Description**: Show weekly reaction statistics  
**Usage**: `/reactions`  
**Permissions**: All users  
**Response**: Top users by reactions received this week  

---

### Economy & Shop

#### `/shop`
**Description**: Browse and purchase items from the shop  
**Usage**: 
- `/shop` - Browse all items
- `/shop buy [item_id]` - Purchase specific item

**Available Items**:
- `xp_boost` - ? XP Booster (150 coins)
- `coin_boost` - ?? Coin Multiplier (120 coins)
- `referral_boost` - ?? Referral Booster (180 coins)
- `streak_freeze` - ?? Streak Freeze (100 coins)
- `custom_badge` - ??? Custom Badge (200 coins)
- `title_unlock` - ?? Custom Title (300 coins)

**Examples**:
```
/shop
/shop buy xp_boost
/shop buy title_unlock
```

**Permissions**: All users  
**Response**: Shop interface or purchase confirmation  

---

### Challenges

#### `/challenges`
**Description**: View active weekly challenges and progress  
**Usage**: `/challenges`  
**Permissions**: All users  
**Response**: Current challenges with progress and rewards  

**Challenge Types**:
- `photo_spree` - ?? Photo Spree (20 photos)
- `streak_keeper` - ?? Streak Keeper (5+ day streak)
- `social_butterfly` - ?? Social Butterfly (30 reactions)
- `content_creator` - ?? Content Creator (15 posts)
- `early_bird` - ?? Early Bird (5 morning posts)
- `referral_master` - ?? Referral Master (3 referrals)

---

### Title Management

#### `/title`
**Description**: Manage custom titles  
**Usage**:
- `/title` - Show current title
- `/title set [custom_title]` - Set custom title (requires Custom Title item)
- `/title reset` - Reset to level-based title

**Examples**:
```
/title
/title set Community Leader
/title reset
```

**Permissions**: All users  
**Requirements**: Custom Title item for setting custom titles  

---

### Referral System

#### `/referral`
**Description**: Manage referral system and view statistics  
**Usage**:
- `/referral` - View code and stats
- `/referral use [CODE]` - Use someone's referral code

**Examples**:
```
/referral
/referral use REF123ABCDEF
```

**Permissions**: All users  
**Time Limit**: Codes must be used within 24 hours of joining  

**Response Format**:
```
?? Your Referral System

?? Your Code: REF123ABCDEF
?? Stats:
  • Total Referrals: 5
  • Active Referrals: 3
  • Weekly Referrals: 2

?? Your Referrals:
  • @user1 (? Active)
  • @user2 (?? 8/10 posts)
  • @user3 (? Active)

?? Rewards:
  • Sign-up Bonus: 50 coins
  • Activity Milestone: 100 coins
  • New Member Welcome: 25 coins
```

---

## ?? Automated Systems

### Job Schedulers

#### New Member Enforcement
**Frequency**: Every 15 minutes  
**Function**: Check new member deadlines and enforce posting requirements  
**Actions**:
- Warn members 15 minutes before deadline
- Remove members who miss deadline
- Clear enforcement data after action

#### Inactivity Management
**Frequency**: Every 15 minutes  
**Function**: Monitor user activity and enforce inactivity policy  
**Actions**:
- Warn users after 48 hours of inactivity
- Remove users after 72 hours of inactivity
- Skip administrators and owners

#### Daily Reset
**Frequency**: Daily at midnight UTC  
**Function**: Reset daily statistics and announce top poster  
**Actions**:
- Identify and announce daily top poster
- Grant "Top Poster (Daily)" achievement
- Clear daily post counters

#### Weekly Reset
**Frequency**: Weekly (configurable day)  
**Function**: Reset weekly statistics and select new challenges  
**Actions**:
- Announce weekly top poster
- Grant "Weekly Warrior" achievement
- Clear weekly counters
- Select new weekly challenges
- Reset challenge progress

#### Streak Checker
**Frequency**: Every 6 hours  
**Function**: Verify posting streaks and handle streak breaks  
**Actions**:
- Check for broken streaks
- Respect streak freeze protection
- Notify users of streak breaks
- Reset streak counters

---

## ?? Automatic Triggers

### Message Processing
Every message triggers automatic processing:

#### Content Analysis
- Detect content type (photo, video, document, link, text)
- Award appropriate XP and coins
- Update daily/weekly/total counters
- Track content type statistics

#### Streak Management
- Check if message maintains or starts streak
- Award streak bonuses
- Update last post date
- Handle streak calculations

#### Achievement Checking
- Scan for newly unlocked achievements
- Grant achievement rewards
- Announce achievement unlocks
- Update badge status

#### Challenge Progress
- Update relevant challenge progress
- Check for challenge completion
- Award challenge rewards
- Announce completions

#### Referral Tracking
- Check for referral milestone progress
- Award milestone bonuses
- Update referral statistics

### Reaction Processing
Reaction updates trigger:

#### Reaction Tracking
- Count reactions per message and user
- Update weekly reaction totals
- Track most loved posts
- Award coins for reactions received

#### Social Achievements
- Check for reaction-based achievements
- Update social engagement metrics
- Award "Reaction King" and similar achievements

#### Challenge Updates
- Update "Social Butterfly" challenge progress
- Check for challenge completion

---

## ?? Configuration API

### Customizable Constants

#### Time Windows
```python
NEW_MEMBER_POST_WINDOW = timedelta(hours=1)      # New member deadline
NEW_MEMBER_WARN_BEFORE = timedelta(minutes=15)   # Warning timing
INACTIVITY_WARN_AT = timedelta(hours=48)         # Inactivity warning
INACTIVITY_KICK_AT = timedelta(hours=72)         # Inactivity removal
CHECK_INTERVAL = timedelta(minutes=15)           # Job frequency
DAILY_WINDOW = timedelta(hours=24)               # Daily reset window
WEEKLY_WINDOW = timedelta(days=7)                # Weekly reset window
STREAK_CHECK_INTERVAL = timedelta(hours=6)       # Streak check frequency
```

#### Reward Values
```python
PTS_PHOTO = 1                                   # Points for photos
PTS_VIDEO = 1                                   # Points for videos
PTS_DOC = 1                                     # Points for documents
PTS_LINK = 1                                    # Points for links
COIN_DAILY_POST = 10                           # Coins per post
COIN_STREAK_BONUS = 5                          # Streak bonus coins
COIN_REACTION_RECEIVED = 2                     # Coins per reaction
COIN_CHALLENGE_COMPLETE = 50                   # Challenge completion bonus
COIN_LEVEL_UP = 25                             # Level up bonus
COIN_REFERRAL_SIGNUP = 50                      # Referral signup bonus
COIN_REFERRAL_WELCOME = 25                     # Welcome bonus for new users
COIN_REFERRAL_MILESTONE = 100                  # Referral milestone bonus
REFERRAL_ACTIVITY_THRESHOLD = 10               # Posts needed for active referral
```

#### Achievement Thresholds
```python
DAILY_STREAK_THRESHOLD = 1                     # Posts per day for streak
WEEKLY_STREAK_THRESHOLD = 5                    # Posts per week for streak
TITLE_THRESHOLDS = [                           # XP thresholds for titles
    (0, "?? Newcomer"),
    (10, "?? Rookie"),
    (50, "? Regular"),
    (150, "?? Active"),
    (300, "?? Veteran"),
    (500, "?? Elite"),
    (1000, "?? Legend"),
    (2000, "?? Hall of Fame")
]
```

---

## ?? Integration Points

### Adding Custom Commands
```python
async def cmd_custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Custom command handler"""
    await reply_in_same_topic(update, "Custom response")

# Register in main():
application.add_handler(CommandHandler("custom", cmd_custom))
```

### Adding Custom Achievements
```python
# Add to Ach class:
class Ach:
    CustomAchievement = "?? Custom Achievement"

# Add checking logic:
async def check_custom_achievement(context, chat_id, user_id):
    if condition_met:
        await grant_ach(context, chat_id, user_id, Ach.CustomAchievement, "?? Custom Achievement unlocked!")
```

### Adding Custom Shop Items
```python
SHOP_ITEMS["custom_item"] = {
    "name": "?? Custom Item",
    "description": "Custom item description",
    "price": 150,
    "type": "custom",
    "emoji": "??"
}

# Add purchase logic in cmd_shop function
```

### Adding Custom Challenges
```python
WEEKLY_CHALLENGES["custom_challenge"] = {
    "name": "?? Custom Challenge",
    "description": "Complete custom objective",
    "target": 10,
    "type": "custom",
    "reward": 100,
    "emoji": "??"
}
```

---

## ??? Error Handling

### Graceful Error Management
The bot includes comprehensive error handling:

#### Network Errors
- Automatic retry with exponential backoff
- Rate limit respect (RetryAfter handling)
- Timeout handling for slow connections
- Forbidden access graceful handling

#### Permission Errors
- Check user permissions before actions
- Handle missing admin rights gracefully
- Provide helpful error messages

#### Data Validation
- Validate all user inputs
- Sanitize HTML content
- Check parameter formats
- Handle edge cases

#### API Limits
- Respect Telegram rate limits
- Queue messages when necessary
- Handle large group operations efficiently
- Monitor API usage

---

This API reference provides complete documentation for integrating with, customizing, and extending the Ultimate Telegram Bot system.