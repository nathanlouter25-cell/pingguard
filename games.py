"""
games.py - Pre-loaded game definitions with TCP ping endpoints
Each game has multiple endpoint options to try, since many servers block ICMP.

Process names per platform:
  exe       = Windows (.exe)
  exe_mac   = macOS (inside .app bundle, as seen by psutil)
  exe_linux = Linux (native or Proton)
"""

DEFAULT_GAMES = [
    # FPS / Shooters
    {
        "name": "Valorant",
        "exe": "VALORANT-Win64-Shipping.exe",
        "exe_mac": "VALORANT-Win64-Shipping",
        "exe_linux": "VALORANT-Win64-Shipping",
        "icon": "🎯",
        "category": "FPS",
        "endpoints": [
            {"host": "euw1.pvp.net", "port": 443},
            {"host": "eu.api.riotgames.com", "port": 443},
        ],
        "region_note": "EU West"
    },
    {
        "name": "CS2",
        "exe": "cs2.exe",
        "exe_mac": "cs2",
        "exe_linux": "cs2",
        "icon": "🔫",
        "category": "FPS",
        "endpoints": [
            {"host": "steamcommunity.com", "port": 443},
            {"host": "api.steampowered.com", "port": 443},
        ],
        "region_note": "Steam servers"
    },
    {
        "name": "Apex Legends",
        "exe": "r5apex.exe",
        "exe_mac": "r5apex",
        "exe_linux": "r5apex",
        "icon": "🦅",
        "category": "FPS",
        "endpoints": [
            {"host": "eaassets-a.akamaihd.net", "port": 443},
            {"host": "159.153.64.1", "port": 37015},
        ],
        "region_note": "EU servers"
    },
    {
        "name": "Overwatch 2",
        "exe": "Overwatch.exe",
        "exe_mac": "Overwatch",
        "exe_linux": "Overwatch",
        "icon": "⚡",
        "category": "FPS",
        "endpoints": [
            {"host": "eu.battle.net", "port": 443},
            {"host": "us.battle.net", "port": 443},
        ],
        "region_note": "Battle.net EU"
    },
    {
        "name": "Call of Duty: Warzone",
        "exe": "cod.exe",
        "exe_mac": "cod",
        "exe_linux": "cod",
        "icon": "💥",
        "category": "FPS",
        "endpoints": [
            {"host": "eu.battle.net", "port": 443},
            {"host": "172.64.155.188", "port": 3074},
        ],
        "region_note": "EU servers"
    },

    # Battle Royale
    {
        "name": "Fortnite",
        "exe": "FortniteClient-Win64-Shipping.exe",
        "exe_mac": "FortniteClient-Mac-Shipping",
        "exe_linux": "FortniteClient-Win64-Shipping",
        "icon": "🏗️",
        "category": "Battle Royale",
        "endpoints": [
            {"host": "account-public-service-prod.ol.epicgames.com", "port": 443},
            {"host": "fortnite-public-service-prod11.ol.epicgames.com", "port": 443},
        ],
        "region_note": "Epic EU"
    },
    {
        "name": "PUBG",
        "exe": "TslGame.exe",
        "exe_mac": "TslGame",
        "exe_linux": "TslGame",
        "icon": "🪖",
        "category": "Battle Royale",
        "endpoints": [
            {"host": "prod-live-front.playbattlegrounds.com", "port": 443},
        ],
        "region_note": "EU servers"
    },

    # MMO / RPG
    {
        "name": "World of Warcraft",
        "exe": "Wow.exe",
        "exe_mac": "World of Warcraft",
        "exe_linux": "Wow",
        "icon": "⚔️",
        "category": "MMO",
        "endpoints": [
            {"host": "eu.battle.net", "port": 443},
            {"host": "eu.actual.battle.net", "port": 1119},
        ],
        "region_note": "EU servers"
    },
    {
        "name": "Final Fantasy XIV",
        "exe": "ffxiv_dx11.exe",
        "exe_mac": "ffxiv_dx11",
        "exe_linux": "ffxiv_dx11",
        "icon": "🌙",
        "category": "MMO",
        "endpoints": [
            {"host": "frontier.ffxiv.com", "port": 443},
            {"host": "patch-bootver.ffxiv.com", "port": 443},
        ],
        "region_note": "EU Chaos DC"
    },
    {
        "name": "Path of Exile",
        "exe": "PathOfExile.exe",
        "exe_mac": "PathOfExile",
        "exe_linux": "PathOfExile",
        "icon": "💀",
        "category": "ARPG",
        "endpoints": [
            {"host": "www.pathofexile.com", "port": 443},
            {"host": "45.33.26.109", "port": 20481},
        ],
        "region_note": "EU servers"
    },
    {
        "name": "Diablo IV",
        "exe": "Diablo IV.exe",
        "exe_mac": "Diablo IV",
        "exe_linux": "diablo4",
        "icon": "🔥",
        "category": "ARPG",
        "endpoints": [
            {"host": "eu.battle.net", "port": 443},
        ],
        "region_note": "Battle.net EU"
    },

    # MOBA
    {
        "name": "League of Legends",
        "exe": "League of Legends.exe",
        "exe_mac": "League of Legends",
        "exe_linux": "LeagueOfLegends",
        "icon": "🏆",
        "category": "MOBA",
        "endpoints": [
            {"host": "euw1.api.riotgames.com", "port": 443},
            {"host": "eu.api.riotgames.com", "port": 443},
        ],
        "region_note": "EUW"
    },
    {
        "name": "Dota 2",
        "exe": "dota2.exe",
        "exe_mac": "dota2",
        "exe_linux": "dota2",
        "icon": "🛡️",
        "category": "MOBA",
        "endpoints": [
            {"host": "steamcommunity.com", "port": 443},
            {"host": "api.steampowered.com", "port": 443},
        ],
        "region_note": "Steam servers"
    },

    # Sports / Racing
    {
        "name": "FIFA / EA FC",
        "exe": "FC25.exe",
        "exe_mac": "FC25",
        "exe_linux": "FC25",
        "icon": "⚽",
        "category": "Sports",
        "endpoints": [
            {"host": "ea.com", "port": 443},
            {"host": "api2.ea.com", "port": 443},
        ],
        "region_note": "EA servers"
    },
    {
        "name": "Rocket League",
        "exe": "RocketLeague.exe",
        "exe_mac": "RocketLeague",
        "exe_linux": "RocketLeague",
        "icon": "🚀",
        "category": "Sports",
        "endpoints": [
            {"host": "api.epicgames.dev", "port": 443},
            {"host": "account-public-service-prod.ol.epicgames.com", "port": 443},
        ],
        "region_note": "Epic EU"
    },

    # Other
    {
        "name": "Minecraft",
        "exe": "javaw.exe",
        "exe_mac": "java",
        "exe_linux": "java",
        "icon": "⛏️",
        "category": "Sandbox",
        "endpoints": [
            {"host": "session.minecraft.net", "port": 443},
            {"host": "api.minecraftservices.com", "port": 443},
        ],
        "region_note": "Mojang servers"
    },
    {
        "name": "GTA Online",
        "exe": "GTA5.exe",
        "exe_mac": "GTA5",
        "exe_linux": "GTA5",
        "icon": "🚗",
        "category": "Open World",
        "endpoints": [
            {"host": "prod.cloud.rockstargames.com", "port": 443},
        ],
        "region_note": "Rockstar EU"
    },
    {
        "name": "Rainbow Six Siege",
        "exe": "RainbowSix.exe",
        "exe_mac": "RainbowSix",
        "exe_linux": "RainbowSix",
        "icon": "🪟",
        "category": "FPS",
        "endpoints": [
            {"host": "uplaypc-s-ubisoft.cdn.ubi.com", "port": 443},
            {"host": "public-ubiservices.ubi.com", "port": 443},
        ],
        "region_note": "Ubisoft EU"
    },
    {
        "name": "Destiny 2",
        "exe": "destiny2.exe",
        "exe_mac": "destiny2",
        "exe_linux": "destiny2",
        "icon": "🌌",
        "category": "FPS",
        "endpoints": [
            {"host": "www.bungie.net", "port": 443},
        ],
        "region_note": "Bungie servers"
    },
    {
        "name": "Lost Ark",
        "exe": "LOSTARK.exe",
        "exe_mac": "LOSTARK",
        "exe_linux": "LOSTARK",
        "icon": "🗺️",
        "category": "ARPG",
        "endpoints": [
            {"host": "api.amazon.com", "port": 443},
        ],
        "region_note": "Amazon EU"
    },
]

# Ping quality thresholds (ms)
PING_THRESHOLDS = {
    "excellent": 30,
    "good": 60,
    "fair": 100,
    "poor": 150,
    # above 150 = critical
}

def get_ping_status(ms):
    """Return status label and color for a given ping value."""
    if ms is None:
        return "unknown", "#888888"
    if ms < PING_THRESHOLDS["excellent"]:
        return "excellent", "#00e676"
    elif ms < PING_THRESHOLDS["good"]:
        return "good", "#69f0ae"
    elif ms < PING_THRESHOLDS["fair"]:
        return "fair", "#ffeb3b"
    elif ms < PING_THRESHOLDS["poor"]:
        return "poor", "#ff9800"
    else:
        return "critical", "#f44336"
