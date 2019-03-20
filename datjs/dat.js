var jsonparam;
const hash = location.hash;
if (hash.length > 0) {
  jsonparam = decodeURIComponent(hash.substr(1));
} else {
  jsonparam = jsontest;
}

///////////////////////////////////////////////////////////////////////////////

function zHex(i, length) {
  var sHex = i.toString(16);
  return "0".repeat(length - sHex.length) + sHex;
}

function hexii(c) {
  ESCAPE = {
    "\x07": "\\a", // BEL
    "\x08": "\\b", // BS
    "\x09": "\\t", // TAB
    "\x0A": "\\n", // LF
    "\x0B": "\\v", // VT
    "\x0C": "\\f", // FF
    "\x0D": "\\r", // CR
    "\x1B": "\\e"  // ESC
  };

  if (c in ESCAPE) {
    return ESCAPE[c];
  }

  v = c.charCodeAt(0);
  if (v >= " ".charCodeAt(0) && v <= "~".charCodeAt(0)) {
    return "." + c;
  }

  if (v < 8) {
    return "\\" + v;
  }

  return zHex(v, 2);
}

function mixedHex(strucOffset, lineOffset, lineLength, indexes) {
  const l = [];
  for (var i = 0; i < lineLength; i++) {
    if (contents.length - 1 < lineOffset + i) {
      break;
    }
    c = contents.substr(lineOffset + i, 1);
    if (indexes.has(i + lineOffset - strucOffset)) {
      l.push(hexii(c));
    } else {
      l.push(zHex(c.charCodeAt(0), 2).toUpperCase());
    }
  }
  return l.join(" ");
}

function getSizeIdx(struc, subEls, offset) {
  const indexes = new Set();
  var size;
  if (!(size in struc)) {
    size = 0;
  }
  for (i in subEls) {
    var el = subEls[i];
    if (el["offset"] < offset) {
      console.log("OMG, wrong offset", el);
    }
    // are empty leaves OK ?
    if (el["size"] == 0) {
      console.log("OMG, empty offset", el);
    }
    // collect nibbles to be printed as HexII
    size = Math.max(size, el["offset"] - offset + el["size"]);
    if ("ASCII" in el && el["ASCII"] == true) {
      for (var i = 0; i < el["size"]; i++) {
        indexes.add(el["offset"] - offset + i);
      }
    }
  }
  return [size, indexes];
}

const { align, expression, fill, geq, eq, fix, forEach } = albert;

const jData = JSON.parse(jsonparam);
const groups = [];

function compareOffsets(a, b) {
  return a.offset - b.offset;
}

function last(array) {
  return array[array.length - 1];
}

/**
 * Returns an value representing the width of a text table useful when comparing
 * tables to each other.
 *
 * This implementation is based on the width/fontSize ratios of each table row.
 */
function getWidth(textTable) {
  let max;
  const rowCount = textTable.getRowCount();
  for (let i = 0; i < rowCount; i++) {
    const width = textTable
      .getRow(i)
      .contents()
      .reduce((sum, cell) => sum + cell.ratios.width, 0);
    if (max === undefined || max < width) {
      max = width;
    }
  }
  return max;
}

/**
 * Returns the maximum element of an array determined by the passed in function.
 */
function maxBy(array, fn) {
  let maxEl = array[0];
  let maxValue = maxEl === undefined ? undefined : fn(maxEl, 0);
  for (let i = 1; i < array.length; i++) {
    const el = array[i];
    const value = fn(el, i);
    if (value > maxValue) {
      maxValue = value;
      maxEl = el;
    }
  }
  return maxEl;
}

function generate(svg) {
  contents = atob(jData.b64contents);
  offsetLen = contents.length.toString(16).length + 1;

  function makeFieldVal(fv) {
    const table = new albert.TextTable({
      id: "fieldVal",
      "font-family": theme.fvFont,
      "font-style": "fill:" + theme.hdrColor + ";",
      fill: theme.hdrColor
    });
    table.addRows(...fv);

    table.setSpacing({ x: 0.5, y: theme.hexYspace });

    table
      .getColumn(0)
      .setAttributes({
        "font-family": theme.hexFont,
        "font-style": theme.hex + ";",
        fill: theme.hex
      })
      .alignTo("right", "baseline");
    table.getColumn(1).alignTo("left", "baseline");
    table
      .getColumn(2)
      .alignTo("left", "baseline")
      .setAttributes({
        "font-family": theme.hexFont,
        "xml:space": "preserve"
      });
    svg.constrain(table.constraints());

    svg.append(table);
    return table;
  }

  function makeHexline(hex, i) {
    const hexline = new albert.TextTable({
      id: "hex" + i,
      "font-family": theme.hexFont,
      "xml:space": "preserve",
      "font-style": "fill:" + theme.dimColor + ";",
      fill: theme.dimColor
    });
    hexline.addRows(...hex);

    hexline.setSpacing({ x: 0.5, y: theme.hexYspace });

    hexline
      .getColumn(0)
      .setAttributes({
        "font-style": theme.hexColor + ";",
        fill: theme.hexColor
      })
      .alignTo("right", "baseline");
    hexline.getColumn(1).alignTo("left", "baseline");
    svg.constrain(hexline.constraints());
    svg.append(hexline);
    return hexline;
  }

  function makeHeader(s, i) {
    const text = new albert.Text(s, {
      id: "hdrColor" + i,
      "font-family": theme.hdrFont,
      "font-size": 1.5,
      "font-style": "fill:" + theme.hdrColor + ";",
      fill: theme.hdrColor
    });
    svg.constrain(fix(text.fontSize));
    svg.append(text);
    return text;
  }

  function drawEls(struct, leaves, headers, hexlines, fieldvals) {
    const { name, type, offset } = struct;
    const [size, indexesASCII] = getSizeIdx(struct, leaves, offset);
    const s_fieldvals = [];

    for (var i = 0; i < leaves.length; i++) {
      const leaf = leaves[i];
      const row = ["+" + zHex(leaf.offset - offset, 2), leaf.name, leaf.value];
      s_fieldvals.push(row);
    }
    const fieldval = makeFieldVal(s_fieldvals);
    fieldvals.push(fieldval);
    headers.push(makeHeader(name));

    const delta = offset % 16;
    const startOffset = offset - delta;
    const endOffset = offset + size - ((offset + size) % 16);

    const s_hexlines = [];
    for (var i = startOffset; i < offset + size; i += 16) {
      s_hexlines.push([
        zHex(i, offsetLen),
        mixedHex(offset, i, 16, indexesASCII)
      ]);
    }
    s_hexlines[0][1] = "   ".repeat(delta) + s_hexlines[0][1].substr(delta * 3);
    s_hexlines[s_hexlines.length - 1][1] = s_hexlines[
      s_hexlines.length - 1
    ][1].substr(0, 3 * ((offset + size) % 16));
    s_hexlines.push(["", " 0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F"]);

    const hexline = makeHexline(s_hexlines);

    var iColor = 0;
    for (var i = 0; i < leaves.length; i++) {
      var color = theme.valColors[iColor % theme.valColors.length];
      const offset = leaves[i].offset;
      const size = leaves[i].size;
      const lineColor = Math.floor((offset - startOffset) / 16);
      const startColor = offset % 16;

      function colorHex(line, start, end, color) {
        hexline
          .getCell(1, line)
          .format(3 * start, 3 * end, { style: "fill:" + color });
      }
      if ((offset % 16) + size <= 16) {
        colorHex(lineColor, startColor, (offset % 16) + size, color);
      } else {
        colorHex(lineColor, startColor, 16, color);
        colorHex(lineColor + 1, 0, ((offset + size) % 16) + 1, color);
      }
      fieldval.getCell(1, i).setAttributes({ style: "fill:" + color });
      fieldval.getCell(2, i).setAttributes({ style: "fill:" + color });

      iColor += 1;
    }
    hexlines.push(hexline);
  }

  function parseStruc(struct, headers, hexlines, fieldvals) {
    const leaves = [];
    const substructs = [];
    for (var i in struct.subEls.sort(compareOffsets)) {
      el = struct.subEls[i];
      if (el.hasOwnProperty("subEls")) {
        substructs.push(el);
      } else {
        leaves.push(el);
      }
    }
    if (leaves.length > 0) {
      drawEls(struct, leaves, headers, hexlines, fieldvals);
    }
    if (substructs.length > 0) {
      for (var i in substructs) {
        parseStruc(substructs[i], headers, hexlines, fieldvals);
      }
    }
  }

  const rect = new albert.Rect({
    id: "bg",
    fill: theme.bgColor
  });
  svg.constrain(fill(svg, rect));
  svg.append(rect);

  if (jData.length != contents.length) {
    console.log("Incorrect length");
  }
  const headers = [];
  const hexlines = [];
  const fieldvals = [];
  parseStruc(jData.struc, headers, hexlines, fieldvals);
  for (var i = 0; i < fieldvals.length; i++) {
    svg.constrain(
      eq(fieldvals[i].topEdge, hexlines[i].topEdge),
      align(hexlines[i].topEdge, headers[i].baseline, 0.5),
      align(fieldvals[i].leftEdge, hexlines[i].rightEdge, 2),
      align(hexlines[i].leftEdge, headers[i].leftEdge, 2)
    );
    hexlines[i]
      // last row of nibbles
      .getRow(hexlines[i].getRowCount() - 1)
      .setAttributes({ fill: theme.hexColor });
  }

  svg.constrain(
    align(headers[0].leftEdge, svg.leftEdge, 0.5),
    align(headers[0].topEdge, svg.topEdge, 0.5)
  );
  for (var i = 1; i < fieldvals.length; i++) {
    svg.constrain(
      eq(headers[i].leftEdge, headers[i - 1].leftEdge),
      align(headers[i].topEdge, hexlines[i - 1].bottomEdge, 1)
    );
  }

  // Allow Albert to determine the SVG height
  const bottommostTable = maxBy([last(fieldvals), last(hexlines)], table =>
    table.getRowCount()
  );
  svg.constrain(align(svg.bottomEdge, bottommostTable.bottomEdge, 0.5));

  // Find the widest fieldVal and use that to determine the SVG width
  const widestFieldVal = maxBy(fieldvals, val => getWidth(val));
  svg.constrain(align(svg.rightEdge, widestFieldVal.rightEdge, 0.5));
}
