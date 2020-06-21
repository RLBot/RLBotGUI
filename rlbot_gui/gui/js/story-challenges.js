
import StoryUpgrades from './story-upgrades.js';
import StoryPickTeam from './story-pick-team.js';
import StoryRecruitList from './story-recruit-list.js';

const DEBUG = false;
const CITIES = {
    'INTRO': 1,
};

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
const CITY_DISPLAY_INFO = {
    'INTRO': {
        displayName: "Beginner's Park",
        message: "Shoddy field for shoddy players. No boost available.",
        overlayLocation: [390, 630],
        clickArea: "649,380,601,379,586,457,566,479,599,525,635,546,718,566,718,514",
        prereqs: [],
    },
    'URBAN': {
        displayName: 'Urban Central',
        message: 'Place to start making your name! People at this level know the value of Boost upgrades!',
        overlayLocation: [350, 700],
        clickArea: "650,3,671,141,585,221,643,354,724,509,801,437,829,221,779,9",
        prereqs: ['INTRO']
    },
    'WASTELAND': {
        displayName: 'Demolishing Wastelands',
        message: 'Don\'t expect politeness here. Home of the demo experts!',
        overlayLocation: [85, 155],
        clickArea: "4,59,109,5,268,62,199,269,166,532,3,547",
        prereqs: ['URBAN']
    },
    'CAMPANDSNIPE': {
        displayName: 'Commonwealth of Campandsnipe',
        message: 'This city is a little different. Boost is limitless but the ball seems a bit different!',
        overlayLocation: [300, 500],
        clickArea: "295,158,254,198,232,302,255,366,270,502,351,525,446,508,562,473,595,384,641,331,578,229,404,294,332,226,323,187,348,149,326,143",
        prereqs: ['URBAN']
    },
    'CHAMPIONSIAN': {
        displayName: 'Championsian Federation',
        message: 'You have made it far but this is the next level. The odds are stacked against you but if you win here, you will be the Champion of this world.',
        overlayLocation: [64, 540],
        clickArea: "401,92,334,176,405,285,579,217,668,125,637,4,469,21",
        prereqs: ['WASTELAND', 'CAMPANDSNIPE']
    }
};

export default {
    name: 'story-challenges',
    props: { saveState: Object },
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
                You have earned 1 currency!
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
                        v-bind:style="{top: city.overlayLocation[0] + 'px', left: city.overlayLocation[1] + 'px', postion: 'absolute'}" 
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
                        class="mt-2"
                        :title="'City: ' + cityDisplayInfo[selectedCityId].displayName"
                        bg-variant="dark"
                        text-variant="light"
                        >
                        <div>
                            <b-img
                                :src="'imgs/arenas/' + challenges[selectedCityId][0].map  +'.jpg'"
                                height="100px"/>
                            <p class="story-inline" style="max-width:400px; display:inline-block">
                            {{cityDisplayInfo[selectedCityId].message}}
                            </p>
                        </div>
                    </b-card>
 
                </b-col>
                <b-col class="mh-100" cols-xl="auto" style="min-width:200px; max-width:800px;">
                    <b-row class="h-50">
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
                            <b-tab title="Upgrades" >
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
            cityDisplayInfo: CITY_DISPLAY_INFO,
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
            let displayName = CITY_DISPLAY_INFO[city].displayName;

            const suffix = [
                'is still locked.',
                'is open to challenge!',
                'has been completed!'
            ];
            return displayName + ' ' + suffix[state];
        },
        handleCityClick: function (city) {
            if (this.getCityState(city) != CITY_STATE.LOCKED) {
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
        this.challenges = await eel.get_challenges_json()();
        this.bots_config = await eel.get_bots_json()();
        this.switchSelectedCityToBest();
    },
    watch: {

    }
};
