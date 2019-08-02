Vue.use(VueMaterial.default);

const app = new Vue({
    el: '#app',
    data: {
        repos: [],
        showProgressSpinner: false,
    },
    created: function () {
        downloadRepos();
    },
    methods: {
    	downloadBot: function (repo) {
            eel.download_bot(repo.url, repo.name)(function() {
				repo.is_installed = true;
			})
		},
        deleteBot: function (repo) {
            eel.delete_bot(repo.name)(function() {
				repo.is_installed = false;
            })
        }
	}
});


async function downloadRepos() {
	await fetch('https://raw.githubusercontent.com/ard1998/RLBot-repos/master/trusted.json')
		.then(function(response) {
			return response.json();
		})
		.then(function(myJson) {
			app.repos = myJson.repos;
			addPackageData(myJson);
		});
}

async function addPackageData(json) {
	for (var index = 0; index < json.repos.length; index++) {
		var repo = json.repos[index];

		var urlPart = "";

		if (urlPart.indexOf("tree") === -1) {
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
			.then(function(myJson) {
				app.repos[index].testedFrameworkVersion = myJson.testedFrameworkVersion;
				app.repos[index].version = myJson.version;
				app.repos[index].categories = myJson.categories;
				app.repos[index].gamemodes = myJson.gamemodes;
			});
	}
}
