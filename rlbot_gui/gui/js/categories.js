export default {
    all: {
        name: "All bots",
        categories: [
            {
                bots: "*",
                scripts: "*",
                includePsyonixBots: true,
            },
        ],
    },
    standard: {
        name: "Standard",
        categories: [
            {
                name: "Bots for 1v1",
                bots: "1v1",
            },
            {
                name: "Bots with teamplay",
                bots: "teamplay",
            },	
            {
                name: "Goalie bots",
                bots: "goalie",
            },	
        ],
    },
    extra: {
        name: "Extra modes",
        categories: [
            {
                name: "Hoops",
                bots: "hoops",
                scripts: "hoops",
            },
            {
                name: "Dropshot",
                bots: "dropshot",
                scripts: "dropshot",
            },
            {
                name: "Snow Day",
                bots: "snow-day",
                scripts: "snow-day",
            },
            {
                name: "Rumble",
                bots: "rumble",
                scripts: "rumble",
            },
            {
                name: "Spike Rush",
                bots: "spike-rush",
                scripts: "spike-rush",
            },
            {
                name: "Heatseeker",
                bots: "heatseeker",
                scripts: "heatseeker",
            },
        ],
    },
    special: {
        name: "Special bots/scripts",
        categories: [
            {
                bots: "memebot",
                displayScriptDependencies: true,
            },
        ],
    },
};