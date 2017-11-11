var heatData = [];
var heatLabels = [];
var heatIndices = [];
var labelCount = 0;
var distValue = 0;
var boundaries = [];
var clickLock = false;
var thisLabel = '';
var bundleMask = [];
var bundleCount = 0;
var xData;
var yData;
var xFilename;
var yFilename;
var sectionList;
var selectedSections = {};
var myPlot = document.getElementById('myDiv');
var clickInfo = document.getElementById('clickText');
var popupDiv = document.getElementById('infopane');

function parseLabels(label) {

  var labelParts = String(label).split("_");
  var thisSection = labelParts[0];

  if (!(thisSection in selectedSections)) {
    selectedSections[thisSection] = true;
  }

  if (!selectedSections[thisSection]) {
    bundleMask.push(false);
    return;
  }
  bundleMask.push(true);

  if (thisLabel == '') {
    thisLabel = thisSection;
  } else if (thisLabel != thisSection) {
    thisLabel = thisSection;
    boundaries.push(labelCount);
  }

  heatLabels.push(label);
  heatIndices.push(labelCount);
  labelCount++;

}

function parseData(rowdata) {

  if (bundleMask[bundleCount]) {
    var newData = [];

    console.log("looking at bundle " + bundleCount);
    for (var i in rowdata) {
      if (bundleMask[i]) {
        newData.push(rowdata[i]);
      }
    }
    heatData.push(newData);
  }
  bundleCount++;

}

function sectionClicked(cbox) {

  var thisSection = cbox.id;

  if (selectedSections[thisSection]) {
    selectedSections[thisSection] = false;
  } else {
    selectedSections[thisSection] = true;
  }

}

function showSections() {

  sectionList = document.getElementById('sectionList');

  var thisHTML = '<fieldset><div><strong>Sections</strong></div>';

  for (var thisSection in selectedSections) {
    var checkedString = "";
    if (selectedSections[thisSection]) {
      checkedString = " checked";
    }
    thisHTML += '<div class="checkbox"><input type="checkbox" id="' + thisSection + '" name="' + thisSection + '" onclick="sectionClicked(this)"' + checkedString + '><label for="' + thisSection + '">' + thisSection + '</label></div>';
  }

  thisHTML += "</fieldset>";

  var reloadButton = document.createElement("BUTTON");
  var t = document.createTextNode("Reload");
  reloadButton.appendChild(t);
  reloadButton.onclick = function(){loadData()};

  var invertButton = document.createElement("BUTTON");
  var u = document.createTextNode("Invert");
  invertButton.appendChild(u);
  invertButton.onclick = function(){invertSelection()};

  sectionList.innerHTML = thisHTML;

  sectionList.appendChild(reloadButton);
  sectionList.appendChild(invertButton);

}

function invertSelection() {

  var qsa = document.querySelectorAll("input[type=checkbox]"),
      l = qsa.length, i;
  for( var i=0; i<l; i++) {
    var boxID = qsa[i].id;

    if (selectedSections[boxID]) {
      selectedSections[boxID] = false;
    } else {
      selectedSections[boxID] = true;
    }

    qsa[i].checked = !qsa[i].checked;
  }
}

function processReuse(error, idata) {

  console.log("processing text reuse data");

  itextData = idata;

  var totalMatches = 0;

  for (var m in idata["docs"]) {
    var match = idata["docs"][m];
    var sourceTitle = match['source_title'];
    var targetTitle = match['target_title'];

    totalMatches += 1;

    if (itextMatches.hasOwnProperty(sourceTitle)) {
      if (itextMatches[sourceTitle].hasOwnProperty(targetTitle)) {
        itextMatches[sourceTitle][targetTitle].push(match);
      } else {
        itextMatches[sourceTitle][targetTitle] = [match];
      }
    } else {
      itextMatches[sourceTitle] = {};
      itextMatches[sourceTitle][targetTitle] = [match];
    }
    if (itextMatches.hasOwnProperty(targetTitle)) {
      if (itextMatches[targetTitle].hasOwnProperty(sourceTitle)) {
        itextMatches[targetTitle][sourceTitle].push(match);
      } else {
        itextMatches[targetTitle][sourceTitle] = [match];
      }
    } else {
      itextMatches[targetTitle] = {};
      itextMatches[targetTitle][sourceTitle] = [match];
    }
  }
  console.log("Registered " + totalMatches + " text reuse matches");
}

function loadData() {

  heatData = [];
  heatLabels = [];
  heatIndices = [];
  labelCount = 0;
  distValue = 0;
  boundaries = [];
  clickLock = false;
  thisLabel = '';
  bundleMask = [];
  bundleCount = 0;
  clickInfo.innerHTML = "";
  popupDiv.innerHTML = "";

  myPlot.innerHTML = "<h3>Loading data. Please wait...</h3>";

  console.log("Loading labels and data...");

  d3.text("bin_labels.txt",
  function (lerror, ltext) {
    labelsData = d3.dsvFormat("\t").parseRows(ltext, parseLabels);
    console.log("Loaded labels data, now loading texts");

    showSections();

    d3.text("itext_sim.txt",
    function (error, text) {
      hData = d3.dsvFormat("\t").parseRows(text, parseData);
      console.log("Loaded matrix data, drawing map.");
      drawHeatmap();
    });

  });

}

function initialize() {

  // Could be set dynamically based on some value loaded from JSON files
  //document.title = "Interactive text reuse heatmap";
  //document.getElementById('pagetitle').innerHTML = "Interactive text reuse heatmap";

  loadData();

}

function drawHeatmap() {

console.log("Drawing heatmap");

console.log("number of labels is " + heatLabels.length);
console.log("first label is " + heatLabels[0]);
console.log("size of data array is " + heatData.length);

var data = [{
  x: heatLabels,
  y: heatLabels,
  z: heatData,
  type: 'heatmap',
  name: 'Text reuse heatmap',
  hoverinfo: "none",
  colorscale: 'Viridis',
  reversescale: true,
  zsmooth: "best",
  zmax: .5,
  zmin: .1,
  showscale: true
}];

var layout = {
  showlegend: false,
  width: 800,
  height: 800,
  margin: {
    l: 140,
    r: 0,
    t: 25,
    b: 100},
  autosize: true,
  xaxis: {
    type: 'category',
    categoryorder: 'array',
    categoryarray: heatLabels,
    range: heatIndices,
    ticks: '',
    showspikes: true,
    tick0: 0,
    tickangle: -45
  },
  yaxis: {
    type: 'category',
    categoryorder: 'array',
    categoryarray: heatLabels,
    range: heatIndices,
    ticks: '',
    showspikes: true,
    tick0: 0
  },
  shapes: []
};

var maxLine = heatData.length;

for (var b in boundaries) {
  var boundary = parseInt(boundaries[b])-1;

  /* Use this code to draw lines outlining the main sections of the text
   * groupings, as determined by the first part of the filename */
  // Horizontal lines
  layout['shapes'].push({type: 'line', xref: 'x', yref: 'y', x0: 0, y0: boundary, x1: maxLine, y1: boundary, opacity: 0.9, line: {color: '#ff0000', width: 1, dash: 'dash' }});

  // Vertical lines
//  layout['shapes'].push({type: 'line', xref: 'x', yref: 'y', x0: boundary, y0: 0, x1: boundary, y1: maxLine, opacity: 0.9, line: {color: '#ff0000', width: 1, dash: 'dash', }});
}

myPlot.innerHTML = "";

Plotly.newPlot(myDiv, data, layout);

function processXtext(error, bdata){

  xData = bdata;

  queue()   // queue function loads all external data files asynchronously
    .defer(d3.json, "binsJSON/" + yFilename)
    .await(processYtext);   // once all files are loaded,

}

function processYtext(error, bdata) {

  yData = bdata;

  var clickHTML = '<h2>Comparison details</h2>';
  hoverHTML = 'X axis (column) text bundle: ' + xData["label"] + '<br>';
  hoverHTML += 'Y axis (row) text bundle: ' + yData["label"] + '<br>';

  hoverHTML += '</p><p>Similarity between the text bundles (1=identical, 0=nothing in common):<br><b>' + distValue + '</b></p>';

  clickHTML += '<h3><font color="#ff0000">Texts in bundle ' + xData["label"] + '</font></h3>';
  clickHTML += textInfo(xData);

  clickHTML += '<h3><font color="#ff0000">Texts in bundle ' + yData["label"] + '</font></h3>';
  clickHTML += textInfo(yData);

  hoverHTML += formatMatches(xData["matches"], yData["matches"]);

  clickInfo.innerHTML = clickHTML;
  popupDiv.innerHTML = hoverHTML;

}

function textInfo(data) {
  var HTML = "";

  for (var d in data['docsInBin']) {
    var dID = data['docsInBin'][d];
    var thisDoc = data['docs'][dID];
    HTML += '<b>' + dID + ':</b> Title: ' + thisDoc['metadata']['title'] + ', Author: ' + thisDoc['metadata']['author'] + ', Year: ' + thisDoc['metadata']['publication_year'] + ' ';
    HTML += '<b><a href="' + thisDoc['metadata']['url'] + '">[link]</a></b><br>';
  }
  return HTML;
}

function formatMatches(xMatches, yMatches) {
  var matchHTML = "";

  for (var docXID in xMatches) {
    console.log("Checking matches for doc " + docXID);
    if (xMatches.hasOwnProperty(docXID)) {
      for (var docYID in xMatches[docXID]) {
        console.log("Found match doc " + docYID);
        if (xMatches[docXID].hasOwnProperty(docYID)) {
          if (docYID in yMatches) {
            if (matchHTML == "") {
              matchHTML = "<h4>Matches found:</h4>";
            }
            console.log(xMatches[docXID][docYID]);
            for (var m in xMatches[docXID][docYID]) {
              var match = xMatches[docXID][docYID][m];
              console.log("match: " + match);
              matchHTML += '<p><b>' + match["source_title"] + ' -> ' + match["target_title"] + ', similarity: ' + match['similarity'] + '</b></p>';
              matchHTML += '<p><b>' + match["source_title"] + ':</b> ' + match['source_prematch'] + ' <span style="background-color: #ffff00"><b>' + match['source_match'] + '</b></span> ' + match['source_postmatch'] + '</p>';
              matchHTML += '<p><b>' + match["target_title"] + ':</b> ' + match['target_prematch'] + ' <span style="background-color: #ffff00"><b>' + match['target_match'] + '</b></span> ' + match['target_postmatch'] + '</p>';
              matchHTML += '<p>&nbsp;</p>';
            }
          }
        }
      }
    }
  }
  return matchHTML;
}

function textStats(data) {

  var xVal = data.points[0].x;
  var yVal = data.points[0].y;
  var zVal = data.points[0].z;

  distValue = zVal;

  //console.log("Row: " + yVal + ", Column: " + xVal + ", Difference: " + zVal);

  var xaxis = data.points[0].xaxis;
  var yaxis = data.points[0].yaxis;

  xFilename = xVal.toString() + '.json';
  yFilename = yVal.toString() + '.json';

  var distX = xaxis.d2p(data.points[0].x);
  var distY = yaxis.d2p(data.points[0].y);

  queue()   // queue function loads all external data files asynchronously
    .defer(d3.json, "binsJSON/" + xFilename)
    .await(processXtext);   // once all files are loaded,

}

myPlot.on('plotly_hover', function(data){

  if (clickLock) {
    return;
  }

  textStats(data);

});

myPlot.on('plotly_click', function(data){

  if (!clickLock) {
    clickLock = true;
  } else {
    clickLock = false;
  }

  textStats(data);

});


myPlot.on('plotly_unhover', function(data){
});
}
