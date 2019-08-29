Vue.use(VueMaterial.default);

const repolists = ['https://raw.githubusercontent.com/ard1998/RLBot-repos/master/trusted.json',
				   'https://raw.githubusercontent.com/ard1998/RLBot-repos/master/unferifiedCommunity.json'];
var init = true

const app = new Vue({
    el: '#app',
    data: {
        repos: [],
        showProgressSpinner: false,
        init: true,
        filterChangeCount: 0,
        highestCardID: -1
    },
    created: function () {
    	if (init) {
	        downloadRepos();
	        init = false;
	    }
    },
    methods: {
    	downloadBot: async function (repo, update=false) {
    		if (!repo.safe && !update) {
    			if (!confirm('This download is from an unferified source and may contain unsafe code. Do you really want to download this')) {
    				return false;
    			}
    		}
            await eel.download_bot(repo.repoName, repo.url, repo.name)(async function() {
				var botpackage = await eel.get_bot_packaging(repo.repoName, repo.name)()

				repo.is_installed = true;
				repo.localVersion = JSON.parse(botpackage).version
				
				app.highestCardID += 1;
				repo.ID = app.highestCardID;

				repo.push();
			})
		},
        deleteBot: function (repo, update=false) {
            eel.delete_bot(repo.repoName, repo.name)(function() {
            	if (!update) {
					repo.is_installed = false;

					app.highestCardID += 1;
					repo.ID = app.highestCardID;
					
					repo.push();
				}
            })
        },
        updateBot(repo){
        	delete_bot(repo, true)
        	download_bot(repo, true)
        }
	}
});

async function downloadRepos() {
	for (var i = 0; i < repolists.length; i++) {
		await fetch(repolists[i])
			.then(function(response) {
				return response.json();
			})
			.then(async function(myJson) {
				await addPackageData(i, myJson);
			});
	}
}

async function addPackageData(repoListIndex, json) {
	repoUrlArr = repolists[repoListIndex].split('/');
	repoName = repoUrlArr[repoUrlArr.length-1];
	repoNameLength = repoName.length-5;
	repoName = repoName.substr(0, repoNameLength);

	for (var index = 0; index < json.repos.length; index++) {
		var repo = json.repos[index];

		var urlPart = "";

		if (repo.url.indexOf("tree") === -1) {
			urlPart = repo.url.substr(18)+"/master";
		}
		else {
			var part = repo.url.substr(18);
			var link = part.substr(0, part.indexOf("/tree"));
			var branch = part.substr(part.indexOf("/tree")+5);
			urlPart = link + branch;
		}
		var url = 'https://raw.githubusercontent.com' + urlPart + '/' + repo.name + '/botpackage.json';
		await fetch(url)
			.then(function(response) {
				return response.json();
			})
			.then(async function(myJson) {
				app.highestCardID+=1;

				cardData = []
				cardData.ID = app.highestCardID;
				cardData.name = myJson.name;
				cardData.description = myJson.description.length<=100?myJson.description:myJson.description.substr(0, 100) + '...';
				cardData.url =  repo.url;
				cardData.repoName = repoName;
				cardData.localVersion = JSON.parse(await eel.get_bot_packaging(repoName, repo.name)()).version
				cardData.onlineVersion = myJson.version;
				cardData.testedFrameworkVersion = myJson.testedFrameworkVersion;
				cardData.botLanguage = myJson.botLanguage;
				cardData.gamemodes = myJson.gamemodes;
				cardData.categories = myJson.categories;
				cardData.display=true
				cardData.is_installed = await eel.is_bot_installed(repoName, repo.name)();
				cardData.display=true;
				cardData.safe=repoListIndex<1?true:false

				app.repos.push(cardData);
			});
	}
}

function reloadCards(){
	for (var i = app.repos.length - 1; i >= 0; i--) {
		var repo = app.repos[i];
		
		//fill gamemode filters
		var gamemodeFilters = [];
		for (var j = document.getElementsByName('gamemode').length - 1; j >= 0; j--) {
			if (document.getElementsByName('gamemode')[j].checked) {
				arrLen = gamemodeFilters.length;
				gamemodeFilters[arrLen] = document.getElementsByName('gamemode')[j].value.toLowerCase();
			}
		}

		var gamemodeNotFoundCount = 0;
		if (gamemodeFilters.length != 0) {
			//if any active gamemode gamemodeFilters, apply them
			var gamemodeNotFoundCount = gamemodeFilters.length;
			for (var gamemodeFilterIndex = repo.gamemodes.length - 1; gamemodeFilterIndex >= 0; gamemodeFilterIndex--) {
				if (gamemodeFilters.includes(repo.gamemodes[gamemodeFilterIndex].name.toLowerCase())) {
					--gamemodeNotFoundCount;
				}
			}
		}

		//fill repo filters
		var repoFilterPass = false;
		var repoFilter = '';
		for (var j = document.getElementsByName('source').length - 1; j >= 0; j--) {
			if (document.getElementsByName('source')[j].checked) {
				repoFilter = document.getElementsByName('source')[j].value.toLowerCase();
			}
		}
		if (repo.repoName.toLowerCase() === repoFilter || repoFilter === 'all') {
			repoFilterPass = true;
		}

		//display or hide cards
		if (repoFilterPass && gamemodeNotFoundCount === 0 && repo.name.toLowerCase().indexOf(document.getElementById('searchBotName').value.toLowerCase())!==-1) {
			app.repos[i].display=true;
		}
		else{
			app.repos[i].display=false;
		}

		app.repos[1].push()
	}
}