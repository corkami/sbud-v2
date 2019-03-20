const tLightAnsi = {
  name:"Ansi (Light)",
  hexColor: "DarkGreen",
  hdrColor: "Black",
  bgColor: "White",
  dimColor: "#A0A0A0",
  valColors: ["Blue", "Red", "Cyan", "Magenta", "Black"]
};

const tDarkAnsi = {
  name:"Ansi (Dark)",
  hexColor: "DarkGreen",
  hdrColor: "White",
  bgColor: "Black",
  dimColor: "#303030",
  valColors: ["Cyan", "Red", "Yellow", "Magenta", "White"]
};

/* Dracula
https://github.com/dracula/dracula-theme#color-palette
Background   #282a36 black
Current Line #44475a gray 1
Selection    #44475a gray 2
Foreground   #f8f8f2 dim white
Comment      #6272a4 electric gray

Cyan         #8be9fd
Green        #50fa7b
Orange       #ffb86c
Pink         #ff79c6
Purple       #bd93f9
Red          #ff5555
Yellow       #f1fa8c
*/

const tDracula = {
  name:"Dracula",
  hexColor: "#6272a4", // comment
  hdrColor: "#f8f8f2", // foreground -- H74 Cobra
  bgColor: "#282a36",  // background
  dimColor: "#44475a", // current line / selection
  valColors: [
    "#ff5555", // Red
    "#8be9fd", // Cyan
    "#50fa7b", // Green
    "#ffb86c", // Orange
    "#f1fa8c", // Yellow
    "#ff79c6", // Pink
    "#bd93f9"  // Purple
  ]
};

/* Solarized
https://en.wikipedia.org/wiki/Solarized_(color_scheme)#Colors

                  light      dark
"#002b36", base03             bg
"#073642", base02             bgHi

"#586e75", base01  emphasize  secondary
"#657b83", base00  primary
"#839496", base0              primary
"#93a1a1", base1   secondary  emphasize

"#eee8d5", base2   bgHi
"#fdf6e3", base3   bg

(original order)
"#b58900", yellow
"#cb4b16", orange
"#dc322f", red
"#d33682", magenta
"#6c71c4", violet
"#268bd2", blue
"#2aa198", cyan
"#859900", green
*/

const palSolarized = [
  "#dc322f", // red
  "#2aa198", // cyan
  "#859900", // green
  "#b58900", // yellow
  "#268bd2", // blue
  "#cb4b16", // orange
  "#6c71c4", // violet
  "#d33682"  // magenta
];

const tSolarizedLight = {
  name:"Solarized (Light)",
  // 586e75 emphasize
  // 93a1a1 secondary
  // 657b83 primary
  // fdf6e3 bg
  // eee8d5 bghi
  hexColor: "#93a1a1",
  hdrColor: "#586e75",
  bgColor: "#fdf6e3",
  dimColor: "#eee8d5",
  valColors: palSolarized
};

const tSolarizedDark = {
  name:"Solarized (Dark)",
  // 93a1a1 emphasize
  // 586e75 secondary
  // 839496 primary
  // 002b36 bg
  // 073642 bghi
  hexColor: "#586e75",
  hdrColor: "#93a1a1",
  bgColor: "#002b36",
  dimColor: "#073642",
  valColors: palSolarized
};

/* Shades of Purple
https://github.com/ahmadawais/shades-of-purple-vscode#sops-syntax-colors

Background        #2D2B55 deep purple :p
Background Dark   #1E1E3F metal purple :)
Foreground        #A599E9 purple
Hover Background  #4D21FC blue
Contrast          #FAD000 Yellow
Contrast Lite     #FFEE80 Yellow
Contrast Lite II  #FAEFA5 Yellow
Highlight         #FF7200 Orange
Comment           #B362FF light purple
Constants         #FF628C pink
Keywords          #FF9D00 orange
Other             #9EFFFF cyan
Strings           #A5FF90 light green
Templates         #3AD900 green
Definitions       #FB94FF pink
*Alpha*
Invalid           #EC3A37F5 some red
Diff Added        #00FF009A lime
Diff Removed      #FF000D81 red
*/

const tShadesOfPurple = {
  name:"Shades Of Purple",
  hdrFont: 'Eurocorp',
  hexColor: "#A599E9",
  hdrColor: "#B362FF",
  bgColor: "#2D2B55",
  dimColor: "#1E1E3F",
  valColors: [
    "#FF628C", // pink
    "#4D21FC", // Hover Background
    "#FAD000", // Yellow
    "#A5FF90", // light green
    "#FF9D00", // orange
    "#9EFFFF", // cyan
    "#3AD900", // green
    "#FB94FF" // pink
  ]
};

/* C64 colors
Black #000000
Cyan       #AAFFEE
Light blue #0088FF
Blue       #0000AA
Orange #DD8855
Brown  #664400
Green       #00CC55
Light green #AAFF66
Grey       #777777
Light grey #BBBBBB
Dark grey  #333333
Red       #880000
Light red #FF7777
purple    #CC44CC
Yellow #EEEE77
White #FFFFFF
*/

const tC64 = {
  name:"Commodore 64",
  hdrFont:"'Pet Me 64'",
  hexFont:"'Pet Me 64'",
  fvFont: "'Pet Me 64'",
  hexYspace: .5,
  hexColor: "#0088FF",
  hdrColor: "#FFFFFF",
  bgColor:  "#0000AA",
  valColors: ["#AAFFEE", "#880000", "#EEEE77", "#CC44CC"]
};
///////////////////////////////////////////////////////////////////////////////

const themes = {
  tLightAnsi,
  tDarkAnsi,
  tC64,
  tDracula,
  tShadesOfPurple,
  tSolarizedLight,
  tSolarizedDark
};

var themeEL = document.getElementById("theme");
for (var key in themes) {
  var option = document.createElement("option");
  option.text = themes[key].name;
  option.setAttribute("value", key);
  themeEL.add(option);
}

const tDefault = {
  hdrFont:"'Aracne Regular', Arial",
  hexFont:"mononoki,Consolas,monospace",
  fvFont: "Arial",
  hexYspace: 0,
}

function mergeDefaults(t) {
  const theme = Object.assign({}, tDefault, t);
  theme.hexFont = (t.hexFont) ? t.hexFont + "," + tDefault.hexFont : tDefault.hexFont;
  theme.hdrFont = (t.hdrFont) ? t.hdrFont + "," + tDefault.hdrFont: tDefault.hdrFont;
  theme.fvFont  = (t.fvFont)  ? t.fvFont + "," + tDefault.fvFont: tDefault.fvFont;
  return theme;
}
