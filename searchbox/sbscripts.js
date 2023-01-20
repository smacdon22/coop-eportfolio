function newTab(evt, tabName, labelName) {
		var i, tabcontent, tablinks, tablabels;
		tabcontent = document.getElementsByClassName("tabcontent");
		for (i = 0; i < tabcontent.length; i++) {
			tabcontent[i].style.display = "none";
			}
		tablinks = document.getElementsByClassName("tablinks");
		for (i = 0; i < tablinks.length; i++) {
			tablinks[i].className = tablinks[i].className.replace(" active", "");
			}
		tablabels = document.getElementsByClassName("libel");
		for (i = 0; i < tablabels.length; i++) {
			tablabels[i].style.display = "none";
		}
		document.getElementById(tabName).style.display = "block";
		document.getElementById(labelName).style.display = "block";
		evt.currentTarget.className = "tablinks active";
		var curwidth = document.getElementById("stfxLibrarySearchBar").clientWidth;
		if ((tabName == "StFX Scholar") || (tabName == "Digital Collections") || (tabName == "Dataverse") || (tabName == "Archives") || ((tabName == "Course Reserves") && (curwidth <= 750)) || (((tabName == "Subject Guides") || (tabName == "FAQ")) && (curwidth <= 605)) || ((tabName == "Google Scholar") && (curwidth <= 430))) {document.getElementsByClassName("dropbtn")[0].style.backgroundColor = "#ffffff";}
		else {document.getElementsByClassName("dropbtn")[0].style.backgroundColor = "#ffffff00";}
	}

	function noSymbol(nterm, nspec, nscope){
		var term = encodeURIComponent(nterm);
		var spec = nspec;
		var scope = nscope;
		var url = "https://stfx.novanet.ca/discovery/search?query=any,contains,"+term+scope+"1NOVA_STFX:STFX"+spec+"&lang=en&offset=0";
		window.open(url);
		return false;
	}
