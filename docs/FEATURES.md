# ?? Features Documentation

Comprehensive guide to all features available in the Ultimate Telegram Bot.

## ?? Gamification System

### XP & Levels
Users earn experience points (XP) through various activities and level up automatically.

#### XP Sources
- **Daily Posts**: Base XP for each content post
- **Content Types**: Different content may have different XP values
- **Streaks**: Bonus XP for maintaining posting streaks
- **Achievements**: XP rewards for unlocking achievements

#### Level Calculation
```python
level = int((xp ** 0.5) // 1)
```
- Level 1: 1 XP
- Level 2: 4 XP  
- Level 3: 9 XP
- Level 10: 100 XP
- Level 20: 400 XP

#### Level Benefits
- Automatic title updates
- Social status in community
- Access to higher-tier rewards
- Special recognition in leaderboards

### Streak System
Tracks consecutive days of posting activity.

#### Streak Rules
- **Daily Posts**: At least one post per day to maintain streak
- **UTC Timezone**: Uses UTC for day calculation
- **Streak Protection**: Can be purchased from shop
- **Automatic Reset**: Streaks reset after missing a day (unless protected)

#### Streak Benefits
- Daily bonus coins
- Achievement unlocks at milestone streaks
- Special recognition and titles
- Streak protection items available in shop

#### Streak Commands
- `/streak` - View current streak
- Purchase "Streak Freeze" from shop for protection

### Achievement System
Unlock badges and achievements through various activities.

#### Achievement Categories

##### **Milestone Achievements**
- ?? **First Post** - Make your first post
- ?? **100 Uploads** - Share 100 pieces of content
- ?? **Hall of Fame** - Reach extreme milestones

##### **Streak Achievements** 
- ?? **Streak Master (3 days)** - Maintain 3-day streak
- ?? **Streak Master (7 days)** - Maintain 7-day streak  
- ?? **Streak Master (30 days)** - Maintain 30-day streak

##### **Content Achievements**
- ?? **Photo Master** - Share 50 photos
- ?? **Video Master** - Share 25 videos
- ?? **Link Master** - Share 30 links

##### **Social Achievements**
- ?? **Reaction King** - Receive 100+ reactions in a week
- ?? **Love Giver** - Give 50+ reactions to others
- ?? **Social Butterfly** - High engagement rates

##### **Time-based Achievements**
- ?? **Early Bird** - Post during morning hours (6-9 AM)
- ?? **Night Owl** - Post during late hours (10 PM - 4 AM)
- ?? **Consistent Poster** - Post for 7+ consecutive days

##### **Competition Achievements**
- ?? **Top Poster (Daily)** - Be the day's top poster
- ?? **Weekly Warrior** - Be the week's top poster

##### **Referral Achievements**
- ?? **Referral Master** - Successfully refer 10+ members
- ??? **Community Builder** - Successfully refer 25+ members

#### Special Badges
Unlock special badges for exceptional achievements:

- ?? **Social Master** - 100+ weekly reactions
- ?? **Content King** - 50+ weekly posts
- ?? **Early Adopter** - Among first 10 members
- ?? **Consistency Champion** - 14+ day streak
- ?? **Referral Champion** - 10+ active referrals
- ??? **Community Builder** - 25+ active referrals

## ?? Economy System

### Coin Sources
Multiple ways to earn coins in the community:

#### **Daily Activities**
- **Posts**: 10 coins per post (configurable)
- **Streaks**: 5 coins bonus for streak maintenance
- **Reactions**: 2 coins per reaction received
- **Level Up**: 25 coins when reaching new level

#### **Achievements**
- **Badge Unlock**: 25 coins per achievement
- **Challenge Complete**: 50+ coins per challenge
- **Special Milestones**: Variable coin rewards

#### **Referral System**
- **Signup Bonus**: 50 coins when someone uses your code
- **Welcome Bonus**: 25 coins for new members using codes
- **Milestone Bonus**: 100 coins when referred user becomes active

### Coin Multipliers
Boost your coin earning with shop items:

- **Coin Multiplier**: 2x coins for 12 hours (120 coins)
- **Referral Booster**: 2x referral rewards for 48 hours (180 coins)
- **XP Booster**: 2x XP earnings for 24 hours (150 coins)

### Shop System
Spend coins on various items and boosts:

#### **Boost Items**
- ? **XP Booster** (150 coins) - Double XP for 24 hours
- ?? **Coin Multiplier** (120 coins) - Double coins for 12 hours  
- ?? **Referral Booster** (180 coins) - Double referral rewards for 48 hours

#### **Protection Items**
- ?? **Streak Freeze** (100 coins) - Protect streak for 2 days

#### **Cosmetic Items**
- ??? **Custom Badge** (200 coins) - Personalized profile badge
- ?? **Custom Title** (300 coins) - Set custom title instead of level-based

#### **Usage**
```
/shop - Browse available items
/shop buy xp_boost - Purchase specific item
/coins - Check balance and active boosts
```

## ?? Referral System

### How It Works
Each user gets a unique referral code to invite friends.

#### **Getting Your Code**
```
/referral - View your code and stats
```

#### **Using a Code**
New members can use referral codes within 24 hours of joining:
```
/referral use REF123ABCDEF
```

#### **Referral Benefits**

##### **For Referrer (Inviter)**
- 50 coins when someone signs up with their code
- 100 coins when referred user becomes active (10+ posts)
- Achievement unlocks for referral milestones
- Special badges for successful referrers

##### **For Referee (New Member)**
- 25 coins welcome bonus
- Immediate coin boost to start their journey

#### **Tracking & Stats**
- Total referrals made
- Active referrals (users who became engaged)
- Weekly referral progress
- Milestone tracking and rewards

#### **Referral Achievements**
- ?? **Referral Master** - 10 active referrals
- ??? **Community Builder** - 25 active referrals
- Plus special badges and recognition

### Advanced Features
- **Activity Threshold**: Referred users must post 10+ times to count as "active"
- **Time Limit**: Codes must be used within 24 hours of joining
- **Boost Compatibility**: Referral boosters double all referral rewards
- **Weekly Challenges**: Referral-based challenges available

## ?? Weekly Challenges

### Challenge Types
New challenges rotate weekly, offering variety and engagement:

#### **Content Challenges**
- ?? **Photo Spree** - Share 20 photos this week (100 coins)
- ?? **Content Creator** - Post 15 pieces of content (90 coins)

#### **Social Challenges**  
- ?? **Social Butterfly** - Get 30 reactions on posts (80 coins)
- ?? **Referral Master** - Refer 3 new members (150 coins)

#### **Consistency Challenges**
- ?? **Streak Keeper** - Maintain 5+ day streak (75 coins)
- ?? **Early Bird** - Post 5 times between 6-9 AM (60 coins)

### Challenge Mechanics
- **Weekly Rotation**: 3 random challenges each week
- **Progress Tracking**: Real-time progress updates
- **Completion Rewards**: Bonus coins for completion
- **One-time Rewards**: Each challenge can only be completed once per week

### Viewing Challenges
```
/challenges - View active weekly challenges
/profile - See challenge progress in your profile
```

## ?? Statistics & Leaderboards

### Statistics Tracking
Comprehensive data tracking for community insights:

#### **Individual Stats**
- Daily, weekly, and all-time post counts
- Content type breakdown (photos, videos, links, text)
- Reaction statistics
- Streak histories
- Achievement counts
- Referral performance

#### **Community Stats**
- Daily group activity
- Top posters across different timeframes
- Most engaging content
- Weekly reaction leaders
- All-time rankings

### Leaderboard Types

#### **Daily Leaderboards**
- `/top` - Today's top 5 posters
- `/stats` - Daily community overview
- Reset daily at midnight UTC

#### **Weekly Leaderboards**  
- `/leaderboard` - Weekly top 10 posters
- `/reactions` - Weekly reaction leaders
- Reset weekly (configurable day)

#### **All-Time Rankings**
- `/ranking` - All-time top contributors
- Shows total posts and current levels
- Permanent historical record

### Profile System
Comprehensive user profiles showing:

```
/profile - Complete user overview including:
```
- Current level and XP
- Coin balance and active boosts
- Posting streaks and statistics
- Achievement and badge counts
- Referral statistics and code
- Weekly challenge progress
- Content type breakdown
- Membership duration

## ??? Community Management

### New Member Enforcement
Automatic system to ensure new members engage:

#### **Enforcement Rules**
- New members must post within 1 hour (configurable)
- 15-minute warning before deadline
- Automatic removal if deadline missed
- Welcome message with clear instructions

#### **Content Requirements**
New members must post:
- Photos, videos, documents, or links
- Plain text messages don't count
- Any substantial content contribution

### Inactivity Management
Automated system to maintain active community:

#### **Inactivity Policy**
- Warning after 48 hours of inactivity
- Removal after 72 hours of inactivity  
- Administrators and owners are exempt
- Clear warning messages before removal

#### **Activity Tracking**
- Tracks all message activity
- Updates last-seen timestamps
- Monitors posting patterns
- Identifies inactive members

### Content Moderation
Built-in tools for content management:

#### **Content Types**
- Photo recognition and tracking
- Video content monitoring  
- Document and file tracking
- Link detection and categorization
- Text message processing

#### **Engagement Monitoring**
- Reaction tracking on all posts
- Popular content identification
- User engagement patterns
- Community health metrics

## ?? Customization Options

### Configuration Variables
Easily customizable settings:

#### **Time Windows**
```python
NEW_MEMBER_POST_WINDOW = timedelta(hours=1)
INACTIVITY_WARN_AT = timedelta(hours=48)
INACTIVITY_KICK_AT = timedelta(hours=72)
```

#### **Reward Values**
```python
COIN_DAILY_POST = 10
COIN_STREAK_BONUS = 5
COIN_REACTION_RECEIVED = 2
PTS_PHOTO = 1
```

#### **Check Intervals**
```python
CHECK_INTERVAL = timedelta(minutes=15)
STREAK_CHECK_INTERVAL = timedelta(hours=6)
```

### Adding Custom Features

#### **New Achievements**
1. Add to `Ach` class
2. Implement checking logic
3. Add to achievement granting system

#### **New Shop Items**
1. Add to `SHOP_ITEMS` dictionary
2. Implement purchase logic
3. Add usage mechanics

#### **New Commands**
1. Create command function
2. Register with application
3. Add to help menu

---

This feature set creates a comprehensive community engagement system that encourages participation, rewards activity, and maintains healthy group dynamics through automated moderation and gamification.