
import StoryUpgrades from './story-upgrades.js';
import StoryPickTeam from './story-pick-team.js';
import StoryRecruitList from './story-recruit-list.js';

const DEBUG = false;

const CITY_STATE = {
    'LOCKED': 0,
    'OPEN': 1,
    'DONE': 2
};

const CITY_ICON_MAP = [
    'imgs/story/lock-100px.png', // LOCKED
    '',
    'imgs/story/checkmark-100px.png' // DONE
];

// clickArea's generated using https://www.image-map.net/
const CITY_MAP_INFO = {
    'INTRO': {
        displayName: "Beginner's Park",
        overlayLocation: [229, 92], 
        clickArea: "45,181,53,319,79,347,97,329,141,335,144,277,121,183,70,169",
    },
    'TRYHARD': {
        displayName: "City-State of Tryhard",
        overlayLocation: [205, 225],
        clickArea: "124,182,146,335,281,321,289,237,241,172,149,126,115,147",
    },
    'PBOOST': {
        displayName: "Principality of Boost",
        overlayLocation: [367, 209],
        clickArea: "74,346,61,381,83,461,137,532,266,526,328,455,286,392,255,349,254,323,152,338,98,332",
    },
    'WASTELAND': {
        displayName: "Demolishing Wastelands",
        overlayLocation: [123, 616],
        clickArea: "582,71,558,291,666,296,726,251,812,266,754,85",
    },
    'CAMPANDSNIPE': {
        displayName: "Commonwealth of Campandsnipe",
        overlayLocation: [369, 724],
        clickArea: "556,297,537,377,673,412,749,391,821,332,820,261,725,253,665,301",
    },
    'CHAMPIONSIAN': {
        displayName: "Championsian Federation",
        overlayLocation: [193, 520],
        clickArea: "227,160,293,237,284,317,267,355,280,377,425,336,487,321,557,232,559,160,417,106,222,113",
    }
};

export default {
    name: 'story-challenges',
    props: {
        saveState: Object,
        debugMode: Boolean
    },
    components: {
        "story-upgrades": StoryUpgrades,
        "story-pick-team": StoryPickTeam,
        "story-recruit-list": StoryRecruitList
    },
    template: /*html*/`
    <div class="pt-2" v-if="challenges">
        <story-pick-team
            ref="pickTeamPopup"
            :challenge="{}"
            :teammates="saveState.teammates"
            :botInfo="bots_config"
            @teamPicked="launchChallenge($event.id, $event.pickedTeammates)">
        </story-pick-team>
        
        <!-- Popup after completing a game -->
        <b-button v-if="${DEBUG}" @click="$bvModal.show('game_completed_popup')">Open Modal</b-button>
        <b-modal id="game_completed_popup" ok-only
            v-bind:title="game_completed.completed ? 'Congratulations!' : 'Try again!'"
            v-bind:header-bg-variant="game_completed.completed ? 'success' : 'danger'"
            @hide="closeGameCompletedPopup"
            header-text-variant="light">
            <div class="d-block text-center">
            <div v-if="game_completed.completed && all_challenges_done">
                <b-img src="imgs/story/victory-160px.png" />
                <p>
                Woah! You have completed all the challenges!
                </p>
                <p>
                You are the Champion of this Rocket League Story!
                </p>
            </div>
            <div v-if="game_completed.completed && !all_challenges_done">
                <b-img src="imgs/story/coin.png" />
                <p>
                Congrats on finishing the challenge! 
                You have earned 2 currency!
                </p>
                <p>
                You can use it to recruit previous opponents, 
                customize teammates or purchase upgrades.
                </p>
            </div>
            <div v-if="!game_completed.completed">
                <b-img src="imgs/story/exit-160px.png" />
                <p>
                Whoops! Looks like you failed.
                Try again!
                </p>
                <p>
                You can also play previous matches to earn extra currency.
                </p>
            </div>
            </div>
        </b-modal>
        <b-overlay :show="game_in_progress.name" rounded="sm" variant="dark">

            <!-- Intro message-->
            <b-card v-if="showIntroPopup()" class="mx-auto story-card-text" 
                style="width: 600px;"
                title="Are you ready?">
                <b-card-text>
                So you've got some wheels. You think that gives you the right to compete with the
                best? <strong>Your car doesn't even have boost!</strong>
                </b-card-text>

                <b-card-text>
                You are going to have to earn some cred by beating some nobody's like you first.
                </b-card-text>

                <b-button block @click="launchChallenge('INTRO-1')" variant="primary">
                Let's do it!
                </b-button>
            </b-card>

            <!-- Main UI -->
            <b-container fluid v-if="!showIntroPopup()" >
                <b-row>
                <b-col cols="auto">
                    <!-- Map and overlays -->
                   <img 
                        src="imgs/story/story-mode-map.png"
                        usemap="#story-image-map">
                    <img v-for="(city, cityId) in cityDisplayInfo"
                        class="story-map-icon"
                        v-bind:src="getOverlayForCity(cityId)"
                        v-bind:style="{top: city.overlayLocation[0] - 20 + 'px', left: city.overlayLocation[1] + 'px', postion: 'absolute'}" 
                        v-if="getCityState(cityId) !== ${CITY_STATE.OPEN}" />

                    <map name="story-image-map">
                        <area v-for="(city, cityId) in cityDisplayInfo"
                            class="story-clicky"
                            @click.prev="handleCityClick(cityId)"
                            v-bind:id="cityId.toLowerCase() + '-area'"
                            v-bind:alt="city.displayName"
                            v-bind:title="city.displayName"
                            v-bind:coords="city.clickArea"
                            shape="poly">
                    </map>

                    <b-tooltip v-for="(city, cityId) in cityDisplayInfo"
                        v-bind:target="cityId.toLowerCase() + '-area'"
                        triggers="hover">
                        {{getCityStateTooltip(cityId)}}
                    </b-tooltip>
                    <b-card 
                        class="mt-2 ml-0 mr-0 mb-0 settings-card"
                        :title="'City: ' + cityDisplayInfo[selectedCityId].displayName"
                        bg-variant="dark"
                        text-variant="light"
                        >
                        <div>
                            <b-img
                                :src="'imgs/arenas/' + challenges[selectedCityId][0].map  +'.jpg'"
                                height="100px"
                                class="mr-2 float-left" />
                            <p class="story-inline" style="max-width:700px;">
                            {{cityDisplayInfo[selectedCityId].message}}
                            </p>
                        </div>
                    </b-card>
 
                </b-col>
                <b-col class="mh-100" cols-xl="auto" style="min-width:200px; max-width:800px;">
                    <b-row style="overflow-y: auto; height: 380px">
                    <!-- Selecting the challenge -->
                        <b-card 
                            :title="cityDisplayInfo[selectedCityId].displayName"
                            bg-variant="light" text-variant="dark" class="w-100">
                        <b-list-group flush v-if="selectedCityId" class="story-card-text">
                            <b-list-group-item
                                v-bind:variant="challengeCompleted(challenge.id) ? 'success' : 'default'"
                                v-for="challenge in challenges[selectedCityId]">
                                <b-button block
                                    @click="$refs.pickTeamPopup.show(challenge)"
                                    v-bind:variant="challengeCompleted(challenge.id)? 'outline-dark' : 'outline-primary' ">
                                    {{challenge.display}}
                                </b-button>
                            </b-list-group-item>
                        </b-list-group>
                        </b-card>
                    </b-row>
                    <!-- Currency, upgrades and recruiting -->
                    <b-row>
                        <div show variant="primary"
                            class="d-flex justify-content-between align-items-center w-100 mt-1 p-3 bg-info text-white">
                            <div>Currency</div>
                            <div>{{saveState.upgrades.currency}} <b-img src="imgs/story/coin.png" height="30px"/></div>
                        </div>
                    </b-row>
                    <b-row class="mt-1 overflow-auto" style="max-height: 300px; min-height:300px">
                    <b-card no-body class="w-100">
                        <b-tabs content-class="mt-3" fill class="story-card-text">
                            <b-tab title="Upgrades">
                                <story-upgrades 
                                    v-bind:upgradeSaveState="saveState.upgrades"
                                    @purchase_upgrade="$emit('purchase_upgrade', $event)">
                                </story-upgrades>
                            </b-tab>
                            <b-tab active title="Teammates">
                                <story-recruit-list 
                                    v-bind:recruitables="recruit_list"
                                    v-bind:currency="saveState.upgrades.currency"
                                    @recruit="$emit('recruit', {id: $event, currentCurrency: saveState.upgrades.currency})"
                                >
                                </story-recruit-list>
                            </b-tab>
                        </b-tabs>
                    </b-card>
                    </b-row>
                </b-col>
                </b-row>
            </b-container>
        </b-overlay>
    </div>
    `,
    data() {
        return {
            bots_config: {},
            game_in_progress: {},
            cityDisplayInfo: {},
            challenges: null,
            selectedCityId: 'INTRO',
        };
    },
    computed: {
        all_challenges_done: function() {
            for (let city of Object.keys(this.challenges)) {
                for (let challenge of this.challenges[city]) {
                    console.log(challenge.id)
                    if (!this.challengeCompleted(challenge.id)) {
                        return false;
                    }
                }
            }
            return true;

        },
        game_completed: function () {
            // True if a recent on going match finished
            let result = {};
            if (this.game_in_progress.name) {
                let name = this.game_in_progress.name;
                let status = this.saveState.challenges_attempts[name];
                if (status && status.length == this.game_in_progress.target_count) {
                    let results = status[this.game_in_progress.target_count - 1];
                    result = {
                        name: name,
                        completed: results.challenge_completed
                    };
                    this.$bvModal.show('game_completed_popup');
                }
            }
            return result;
        },
        recruit_list: function () {
            const completed = this.saveState.challenges_completed;
            let recruits = {};

            for (let city of Object.keys(this.challenges)) {
                if (this.getCityState(city) != CITY_STATE.DONE) {
                    continue;
                }
                for (let challenge of this.challenges[city]) {
                    // This challenge was completed so opponents are available
                    const botIds = challenge.opponentBots;
                    for (let botId of botIds) {
                        let bot = Object.assign({}, this.bots_config[botId]);
                        bot.recruited = this.saveState.teammates.includes(botId);
                        bot.id = botId;
                        recruits[botId] = bot;
                    }
                }
            }
            return Object.values(recruits);
        },
    },
    methods: {
        closeGameCompletedPopup: function () {
            this.game_in_progress = {};
            this.switchSelectedCityToBest();
        },
        switchSelectedCityToBest: function () {
            let cur = this.selectedCityId;
            if (this.getCityState(cur) == CITY_STATE.OPEN || this.all_challenges_done) {
                // current city is stll open, that's fine
                return;
            }
            else {
                let open_cities = Object.keys(
                    this.cityDisplayInfo).filter((city) =>
                        this.getCityState(city) == CITY_STATE.OPEN);

                let random = open_cities[Math.floor(Math.random() * open_cities.length)];
                console.log(random);
                this.selectedCityId = random;
            }
        },
        challengeCompleted: function (id) {
            return this.saveState.challenges_completed[id] != undefined;
        },
        getCityStateTooltip: function (city) {
            let state = this.getCityState(city);
            let displayName = this.cityDisplayInfo[city].displayName;

            const suffix = [
                'is still locked.',
                'is open to challenge!',
                'has been completed!'
            ];
            return displayName + ' ' + suffix[state];
        },
        handleCityClick: function (city) {
            if (this.getCityState(city) != CITY_STATE.LOCKED || this.debugMode) {
                this.selectedCityId = city;
            }
        },
        showIntroPopup: function () {
            return !this.challengeCompleted("INTRO-1");
        },
        getCityState: function (city) {
            let state = CITY_STATE.LOCKED;

            let prereqs = this.cityDisplayInfo[city].prereqs;
            if (prereqs.every(c => (this.getCityState(c) === CITY_STATE.DONE))) {
                state = CITY_STATE.OPEN;

                // only need to check completion of challenges if we are open
                let cityChallenges = this.challenges[city];
                if (cityChallenges.every(c => this.challengeCompleted(c.id))) {
                    state = CITY_STATE.DONE;
                }
            }
            return state;
        },
        getOverlayForCity: function (city) {
            return CITY_ICON_MAP[this.getCityState(city)];
        },
        launchChallenge: function (challengeId, pickedTeammates = []) {
            let attempts = this.saveState.challenges_attempts[challengeId];
            this.game_in_progress = {
                name: challengeId,
                target_count: (attempts ? attempts.length : 0) + 1
            };
            this.$emit('launch_challenge', { id: challengeId, pickedTeammates });
            console.log(this.game_in_progress);
        }
    },
    created: async function () {
        console.log(this.saveState)
        let cities = await eel.get_cities_json(this.saveState.story_config)();
        this.bots_config = await eel.get_bots_json(this.saveState.story_config)();
        this.challenges = {}
        for (let city of Object.keys(cities)) {
            this.challenges[city] = cities[city].challenges
            this.cityDisplayInfo[city] = cities[city].description
            Object.assign(this.cityDisplayInfo[city], CITY_MAP_INFO[city])
        }
        this.switchSelectedCityToBest();
    },
    watch: {

    }
};
