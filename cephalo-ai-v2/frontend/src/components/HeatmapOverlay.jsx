
// import React from "react";
// import { getFileUrl } from "../services/api";

// const HeatmapOverlay = ({
//   heatmaps = [],
//   selectedIndex,
//   imageWidth,
//   imageHeight,
//   visible = true,
//   opacity = 0.45,
// }) => {
//   if (
//     !visible ||
//     selectedIndex === null ||
//     selectedIndex === undefined ||
//     !imageWidth ||
//     !imageHeight
//   ) {
//     return null;
//   }

//   const selectedHeatmap = heatmaps.find(
//     (heatmap) => heatmap.index === selectedIndex
//   );

//   if (!selectedHeatmap?.url) {
//     return null;
//   }

//   const heatmapUrl = getFileUrl(selectedHeatmap.url);

//   return (
//     <image
//       href={heatmapUrl}
//       x="0"
//       y="0"
//       width={imageWidth}
//       height={imageHeight}
//       preserveAspectRatio="none"
//       opacity={opacity}
//       style={{
//         pointerEvents: "none",
//         mixBlendMode: "screen",
//       }}
//     />
//   );
// };

// export default HeatmapOverlay;

import React from "react";
import { getFileUrl } from "../services/api";

const getConfidenceColor = (confidence) => {
  if (confidence === null || confidence === undefined) {
    return "#ffffff";
  }

  let value = Number(confidence);

  if (!Number.isFinite(value)) return "#ffffff";

  // Support both 0-1 and 0-100 confidence formats.
  if (value <= 1) value *= 100;

  if (value < 40) return "#dc4545";  // Red
  if (value < 60) return "#f39a38";  // Orange
  if (value < 75) return "#f2d447";  // Yellow

  return "#36bd79";                 // Green
};

const hexToRgb = (hex) => {
  const value = hex.replace("#", "");

  return {
    r: parseInt(value.substring(0, 2), 16) / 255,
    g: parseInt(value.substring(2, 4), 16) / 255,
    b: parseInt(value.substring(4, 6), 16) / 255,
  };
};

const HeatmapOverlay = ({
  heatmaps = [],
  landmarks = [],
  selectedIndex,
  imageWidth,
  imageHeight,
  visible = true,
  opacity = 0.45,
}) => {
  if (
    !visible ||
    !imageWidth ||
    !imageHeight ||
    !Array.isArray(heatmaps) ||
    heatmaps.length === 0
  ) {
    return null;
  }

  const hasSelection =
    selectedIndex !== null &&
    selectedIndex !== undefined;

  return (
    <>
      <defs>
        {heatmaps.map((heatmap) => {
          const point = landmarks.find(
            (p) => Number(p.index) === Number(heatmap.index)
          );

          const color = getConfidenceColor(point?.confidence);
          const rgb = hexToRgb(color);

          return (
            <filter
              key={`filter-${heatmap.index}`}
              id={`confidence-heatmap-${heatmap.index}`}
              colorInterpolationFilters="sRGB"
            >
              <feColorMatrix
                type="matrix"
                values={`
                  0 0 0 0 ${rgb.r}
                  0 0 0 0 ${rgb.g}
                  0 0 0 0 ${rgb.b}
                  0.2126 0.7152 0.0722 0 0
                `}
              />
            </filter>
          );
        })}
      </defs>

      {heatmaps.map((heatmap) => {
        if (!heatmap?.url) return null;

        const isSelected =
          hasSelection &&
          Number(heatmap.index) === Number(selectedIndex);

        const layerOpacity = hasSelection
          ? isSelected
            ? opacity
            : opacity * 0.12
          : opacity * 0.3;

        return (
          <image
            key={heatmap.index}
            href={getFileUrl(heatmap.url)}
            x="0"
            y="0"
            width={imageWidth}
            height={imageHeight}
            preserveAspectRatio="none"
            opacity={layerOpacity}
            filter={`url(#confidence-heatmap-${heatmap.index})`}
            style={{
              pointerEvents: "none",
              mixBlendMode: "screen",
            }}
          />
        );
      })}
    </>
  );
};

export default HeatmapOverlay;
