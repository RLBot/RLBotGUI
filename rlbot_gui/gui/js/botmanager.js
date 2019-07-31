var globalJson

	async function downloadRepos() {
		await fetch('https://raw.githubusercontent.com/ard1998/RLBot-repos/master/stableThrusted.json');
		.then(function(response) {
			return response.json();
		})
		.then(function(myJson) {
			globalJson = myJson;
			addPackageData(myJson);
		});
	}

	async function addPackageData(json) {
		for (var index = 0; index < json.repos.length; index++) {
			var repo = json.repos[index];

			var urlPart = "";

			if (urlPart.indexOf("tree")==-1) {
				urlPart = repo.url.substr(18)+"/master";
			}
			else {
				var part = repo.url.substr(18);
				var link = part.substr(0, part.indexOf("/tree"));
				var branch = part.substr(part.indexOf("/tree")+5);
				urlPart = link + branch;
			}
			var url = 'https://raw.githubusercontent.com' + urlPart + '/' + repo.name + '/botpackage.json'
			await fetch(url)
				.then(function(response) {
					return response.json();
				})
				.then(function(myJson) {
					globalJson.repos[index].testedFrameworkVersion = myJson.testedFrameworkVersion;
					globalJson.repos[index].version = myJson.version;
					globalJson.repos[index].categories = myJson.categories;
					globalJson.repos[index].gamemodes = myJson.gamemodes;
					globalJson = json;
				});
		}

		displayRepoData();

	}

	async function displayRepoData() {
		document.getElementById('main').innerHTML = '';
		//make bot ui elements out of json data
		for (var i = 0; i < globalJson.repos.length; i++) {
			repo = globalJson.repos[i];
			display = true;

			//fill gamemode filters
			var gamemodeFilters = [];
			for (var j = document.getElementsByName('gamemode').length - 1; j >= 0; j--) {
				if(document.getElementsByName('gamemode')[j].checked) {
					arrLen = gamemodeFilters.length;
					gamemodeFilters[arrLen] = document.getElementsByName('gamemode')[j].value;
				}
			}

			var gamemodeNotFoundCount = 0;
			if (gamemodeFilters.length != 0) {
				//if any active gamemode gamemodeFilters, apply them
				var gamemodeNotFoundCount = gamemodeFilters.length;
				for (var gamemodeFilterIndex = gamemodeFilters.length - 1; gamemodeFilterIndex >= 0; gamemodeFilterIndex--) {
					for (var j = repo.gamemodes.length - 1; j >= 0; j--) {
						if (repo.gamemodes[j].name.toLowerCase() == gamemodeFilters[gamemodeFilterIndex].toLowerCase()) {
							--gamemodeNotFoundCount;
						}
					}
				}
			}
			if (gamemodeNotFoundCount != 0 || repo.name.toLowerCase().indexOf(document.getElementById('searchBotName').value.toLowerCase())==-1) {
				display = false
			}

			if (display) {
				gamemodeString = '';
				for (var index = repo.gamemodes.length - 1; index >= 0; index--) {
					gamemodeString+=repo.gamemodes[index].name;
					if (index!=0) {
						gamemodeString += ', ';
					}
				}

				categoryString = '';
				for (var index = repo.categories.length - 1; index >= 0; index--) {
					categoryString+=repo.categories[index].name;
					if (index!=0) {
						categoryString += ', ';
					}
				}



				//Filling in template and inserting it
				var html = '';

				html +=	"<div class=\"md-card settings-card md-theme-default\">";
				html +=		"<div class=\"md-card-header\">";
				html += 		"<div class=\"md-title\">"+repo.name+"</div>";
				html +=		"</div>";
				html +=		"<div class=\"md-card-content\">";
				html += 		"<div class=\"center-flex\">";
				html += 			"<div class=\"md-layout md-gutter\">";
				html += 			    "<div class=\"md-layout-item\"><label for=\"gamemodes-0\">gamemode</label>";
				html += 					"<p id=\"gamemodes-0\" class=\"managerInfo\">"+gamemodeString+"</p>";
				html += 			    "</div>";
				html += 			    "<div class=\"md-layout-item\"><label for=\"type-0\">Category</label>";
				html += 					"<p id=\"type-0\" class=\"managerInfo\">"+categoryString+"</p>";
				html += 			    "</div>";
				html += 			"</div> ";
				html += 			"<span style=\"flex-grow: 1;\"></span> ";
				html += 			"<button type=\"button\" class=\"md-button md-primary md-raised md-theme-default\">";
				html += 				"<div id=\"button"+i+"\" class=\"md-ripple\">";

				if (await eel.is_bot_installed(repo.name)()) {
					config = JSON.parse(await eel.get_bot_packaging(repo.name)());
					if (config.version==repo.version) {
						html +=				"<div class=\"md-button-content\" onclick=\"eel.delete_bot('"+repo.name+"')(buttonReplaceToDownload("+i+", '"+repo.name+"', '"+repo.url+"'))\">Delete</div>";
					}
					else {
						html +=				"<div class=\"md-button-content\" onclick=\"eel.delete_bot('"+repo.name+"'); eel.download_bot('"+repo.url+"', '"+repo.name+"')(buttonReplaceToDelete("+i+", '"+repo.name+"', '"+repo.url+"'))\">Update</div>";	
					}
				}
				else {
					html +=					"<div class=\"md-button-content\" onclick=\"eel.download_bot('"+repo.url+"', '"+repo.name+"')(buttonReplaceToDelete("+i+", '"+repo.name+"', '"+repo.url+"'))\">Download</div>";	
				}
				html += 				"</div>"
				html += 			"</button> ";
				/*html += 			"<button type=\"button\" class=\"md-button md-raised md-theme-default\">";
				html += 				"<div class=\"md-ripple\">";
				html += 					"<div class=\"md-button-content\">More info</div>";
				html += 				"</div>";
				html += 			"</button>";
				html += 			"<button type=\"button\" class=\"md-button md-raised md-theme-default\">";
				html += 				"<div class=\"md-ripple\">";
				html += 					"<div class=\"md-button-content\">Configure bot</div>";
				html += 				"</div>";
				html += 			"</button>";*/
				html += 		"</div>";
				html +=		"</div>";
				html +=	"</div>";

				document.getElementById('main').innerHTML += html;
			}
		}
	}

	function buttonReplaceToDownload(index, name, url) {
		document.getElementById('button'+index).innerHTML = "<div class=\"md-button-content\" onclick=\"eel.download_bot('"+url+"', '"+repo.name+"')(buttonReplaceToDelete("+index+", '"+name+"', '"+url+"'))\">Download</div>";	
	}

	function buttonReplaceToDelete(index, name, url) {
		document.getElementById('button'+index).innerHTML = "<div class=\"md-button-content\" onclick=\"eel.delete_bot('"+name+"')(buttonReplaceToDownload("+index+", '"+name+"', '"+url+"'))\">Delete</div>";
	}
