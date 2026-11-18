
// import React, {
//   useEffect,
//   useRef,
//   useState,
// } from "react";

// import LandmarkMarker from "./LandmarkMarker";
// import LandmarkTooltip from "./LandmarkTooltip";
// import HeatmapOverlay from "./HeatmapOverlay";


// const XrayCanvas = ({
//   imageUrl,
//   imageWidth,
//   imageHeight,
//   landmarks = [],
//   heatmaps = [],
//   selectedIndex,
//   onSelect,
//   onUpdateLandmark,
// }) => {
//   const containerRef = useRef(null);
//   const svgRef = useRef(null);

//   const [hoveredIndex, setHoveredIndex] = useState(null);
//   const [tooltipPosition, setTooltipPosition] = useState(null);

//   const [displayPoints, setDisplayPoints] = useState(landmarks);

//   const [draggingIndex, setDraggingIndex] = useState(null);
//   const [dragPosition, setDragPosition] = useState(null);

//   const dragMovedRef = useRef(false);
//   const originalPointRef = useRef(null);
//   const [showHeatmap, setShowHeatmap] = useState(false);
//   const [heatmapOpacity, setHeatmapOpacity] = useState(0.45);
//   // Keep local marker positions synchronized with backend data.
//   useEffect(() => {
//     if (draggingIndex === null) {
//       setDisplayPoints(landmarks);
//     }
//   }, [landmarks, draggingIndex]);

//   // Convert screen coordinates into original image coordinates.
//   const getImageCoordinates = (event) => {
//     const svg = svgRef.current;

//     if (!svg) return null;

//     const point = svg.createSVGPoint();

//     point.x = event.clientX;
//     point.y = event.clientY;

//     const matrix = svg.getScreenCTM();

//     if (!matrix) return null;

//     const transformed = point.matrixTransform(
//       matrix.inverse()
//     );

//     return {
//       x: Math.max(0, Math.min(imageWidth, transformed.x)),
//       y: Math.max(0, Math.min(imageHeight, transformed.y)),
//     };
//   };

//   // Position tooltip relative to the canvas.
//   const updateTooltipPosition = (event) => {
//     const container = containerRef.current;

//     if (!container) return;

//     const rect = container.getBoundingClientRect();

//     const x = event.clientX - rect.left;
//     const y = event.clientY - rect.top;

//     const tooltipWidth = 260;
//     const tooltipHeight = 190;

//     setTooltipPosition({
//       x: Math.max(
//         8,
//         Math.min(x + 16, rect.width - tooltipWidth - 8)
//       ),
//       y: Math.max(
//         8,
//         Math.min(y + 16, rect.height - tooltipHeight - 8)
//       ),
//     });
//   };

//   const handleHover = (index, event) => {
//     if (draggingIndex !== null) return;

//     setHoveredIndex(index);

//     if (index === null) {
//       setTooltipPosition(null);
//       return;
//     }

//     updateTooltipPosition(event);
//   };

//   // Start dragging a selected landmark.
//   const handlePointerDown = (event, index) => {
//     if (event.button !== 0) return;

//     const coordinates = getImageCoordinates(event);

//     if (!coordinates) return;

//     event.preventDefault();

//     const svg = svgRef.current;

//     svg?.setPointerCapture(event.pointerId);

//     dragMovedRef.current = false;
//     originalPointRef.current = landmarks[index];

//     setDraggingIndex(index);
//     setDragPosition(coordinates);
//     setHoveredIndex(index);
//   };

//   // Update marker position while dragging.
//   const handlePointerMove = (event) => {
//     if (draggingIndex !== null) {
//       const coordinates = getImageCoordinates(event);

//       if (!coordinates) return;

//       dragMovedRef.current = true;

//       setDragPosition(coordinates);

//       setDisplayPoints((previous) =>
//         previous.map((point, index) =>
//           index === draggingIndex
//             ? {
//                 ...point,
//                 x: coordinates.x,
//                 y: coordinates.y,
//               }
//             : point
//         )
//       );

//       return;
//     }

//     if (hoveredIndex !== null) {
//       updateTooltipPosition(event);
//     }
//   };

//   // Save corrected coordinates when dragging ends.
//   const handlePointerUp = async (event) => {
//     if (draggingIndex === null) return;

//     const index = draggingIndex;
//     const coordinates = getImageCoordinates(event);

//     const svg = svgRef.current;

//     if (svg?.hasPointerCapture(event.pointerId)) {
//       svg.releasePointerCapture(event.pointerId);
//     }

//     setDraggingIndex(null);
//     setDragPosition(null);
//     setHoveredIndex(null);
//     setTooltipPosition(null);

//     if (!coordinates || !dragMovedRef.current) {
//       setDisplayPoints(landmarks);
//       return;
//     }

//     try {
//       await onUpdateLandmark?.(
//         index,
//         coordinates.x,
//         coordinates.y
//       );
//     } catch (error) {
//       // Restore the original marker if the backend update fails.
//       setDisplayPoints((previous) =>
//         previous.map((point, pointIndex) =>
//           pointIndex === index
//             ? originalPointRef.current
//             : point
//         )
//       );

//       console.error("Landmark correction failed:", error);
//     } finally {
//       dragMovedRef.current = false;
//       originalPointRef.current = null;
//     }
//   };

//   const handlePointerCancel = () => {
//     if (draggingIndex === null) return;

//     setDisplayPoints(landmarks);
//     setDraggingIndex(null);
//     setDragPosition(null);
//     setHoveredIndex(null);
//     setTooltipPosition(null);

//     dragMovedRef.current = false;
//     originalPointRef.current = null;
//   };

//   if (!imageUrl || !imageWidth || !imageHeight) {
//     return (
//       <div className="xray-empty">
//         <div className="xray-empty-icon">＋</div>
//         <h3>No X-ray loaded</h3>
//         <p>Upload a cephalometric X-ray to begin analysis.</p>
//       </div>
//     );
//   }

//   const hoveredPoint =
//     hoveredIndex !== null
//       ? displayPoints[hoveredIndex]
//       : null;

//   return (
//     <div
//       className="xray-canvas"
//       ref={containerRef}
//     >
//       <div className="heatmap-controls">
//   <label>
//     <input
//       type="checkbox"
//       checked={showHeatmap}
//       onChange={(event) => setShowHeatmap(event.target.checked)}
//     />
//     Show heatmap
//   </label>

//   <label>
//     Opacity
//     <input
//       type="range"
//       min="0.1"
//       max="1"
//       step="0.05"
//       value={heatmapOpacity}
//       onChange={(event) =>
//         setHeatmapOpacity(Number(event.target.value))
//       }
//       disabled={!showHeatmap}
//     />
//   </label>
// </div>
//       <svg
//         ref={svgRef}
//         className="xray-svg"
//         viewBox={`0 0 ${imageWidth} ${imageHeight}`}
//         preserveAspectRatio="xMidYMid meet"
//         onPointerMove={handlePointerMove}
//         onPointerUp={handlePointerUp}
//         onPointerCancel={handlePointerCancel}
//         onPointerLeave={() => {
//           if (draggingIndex === null) {
//             setHoveredIndex(null);
//             setTooltipPosition(null);
//           }
//         }}
//       >
//         {/* Actual uploaded X-ray */}
//         <image
//           href={imageUrl}
//           x="0"
//           y="0"
//           width={imageWidth}
//           height={imageHeight}
//           preserveAspectRatio="none"
//         />
//         <HeatmapOverlay
//           heatmaps={heatmaps}
//           landmarks={displayPoints}
//           selectedIndex={selectedIndex}
//           imageWidth={imageWidth}
//           imageHeight={imageHeight}
//           visible={showHeatmap}
//           opacity={heatmapOpacity}
//         />
//         {/* Landmark markers */}
//         {displayPoints.map((point, index) => (
//           <LandmarkMarker
//             key={point.id ?? index}
//             point={point}
//             index={index}
//             selected={selectedIndex === index}
//             hovered={hoveredIndex === index}
//             onSelect={onSelect}
//             onHover={(hovered) => {
//               if (draggingIndex !== null) return;

//               if (hovered === null) {
//                 setHoveredIndex(null);
//                 setTooltipPosition(null);
//               } else {
//                 setHoveredIndex(hovered);
//               }
//             }}
//             onPointerDown={handlePointerDown}
//           />
//         ))}
//       </svg>

//       {/* Hover tooltip */}
//       {hoveredPoint && tooltipPosition && (
//         <LandmarkTooltip
//           point={hoveredPoint}
//           index={hoveredIndex}
//           position={tooltipPosition}
//         />
//       )}

//       {/* Canvas information */}
//       <div className="xray-canvas-info">
//         <span>
//           {imageWidth} × {imageHeight} px
//         </span>

//         <span>
//           {displayPoints.length} landmarks
//         </span>
//       </div>
//     </div>
//   );
// };

// export default XrayCanvas;

import React, {
  useEffect,
  useRef,
  useState,
} from "react";

import LandmarkMarker from "./LandmarkMarker";
import LandmarkTooltip from "./LandmarkTooltip";

const XrayCanvas = ({
  imageUrl,
  imageWidth,
  imageHeight,
  landmarks = [],
  heatmaps = [],
  heatmapOverlayUrl,
  selectedIndex,
  onSelect,
  onUpdateLandmark,
}) => {
  const containerRef = useRef(null);
  const svgRef = useRef(null);

  const [hoveredIndex, setHoveredIndex] = useState(null);
  const [tooltipPosition, setTooltipPosition] = useState(null);

  const [displayPoints, setDisplayPoints] = useState(landmarks);

  const [draggingIndex, setDraggingIndex] = useState(null);
  const [dragPosition, setDragPosition] = useState(null);

  const dragMovedRef = useRef(false);
  const originalPointRef = useRef(null);

  const [showHeatmap, setShowHeatmap] = useState(false);
  const [heatmapOpacity, setHeatmapOpacity] = useState(0.45);

  // Keep local marker positions synchronized with backend data.
  useEffect(() => {
    if (draggingIndex === null) {
      setDisplayPoints(landmarks);
    }
  }, [landmarks, draggingIndex]);

  // Convert screen coordinates into original image coordinates.
  const getImageCoordinates = (event) => {
    const svg = svgRef.current;

    if (!svg) return null;

    const point = svg.createSVGPoint();

    point.x = event.clientX;
    point.y = event.clientY;

    const matrix = svg.getScreenCTM();

    if (!matrix) return null;

    const transformed = point.matrixTransform(
      matrix.inverse()
    );

    return {
      x: Math.max(0, Math.min(imageWidth, transformed.x)),
      y: Math.max(0, Math.min(imageHeight, transformed.y)),
    };
  };

  // Position tooltip relative to the canvas.
  const updateTooltipPosition = (event) => {
    const container = containerRef.current;

    if (!container) return;

    const rect = container.getBoundingClientRect();

    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    const tooltipWidth = 260;
    const tooltipHeight = 190;

    setTooltipPosition({
      x: Math.max(
        8,
        Math.min(x + 16, rect.width - tooltipWidth - 8)
      ),
      y: Math.max(
        8,
        Math.min(y + 16, rect.height - tooltipHeight - 8)
      ),
    });
  };

  const handleHover = (index, event) => {
    if (draggingIndex !== null) return;

    setHoveredIndex(index);

    if (index === null) {
      setTooltipPosition(null);
      return;
    }

    updateTooltipPosition(event);
  };

  // Start dragging a selected landmark.
  const handlePointerDown = (event, index) => {
    if (event.button !== 0) return;

    const coordinates = getImageCoordinates(event);

    if (!coordinates) return;

    event.preventDefault();

    const svg = svgRef.current;

    svg?.setPointerCapture(event.pointerId);

    dragMovedRef.current = false;
    originalPointRef.current = landmarks[index];

    setDraggingIndex(index);
    setDragPosition(coordinates);
    setHoveredIndex(index);
  };

  // Update marker position while dragging.
  const handlePointerMove = (event) => {
    if (draggingIndex !== null) {
      const coordinates = getImageCoordinates(event);

      if (!coordinates) return;

      dragMovedRef.current = true;

      setDragPosition(coordinates);

      setDisplayPoints((previous) =>
        previous.map((point, index) =>
          index === draggingIndex
            ? {
                ...point,
                x: coordinates.x,
                y: coordinates.y,
              }
            : point
        )
      );

      return;
    }

    if (hoveredIndex !== null) {
      updateTooltipPosition(event);
    }
  };

  // Save corrected coordinates when dragging ends.
  const handlePointerUp = async (event) => {
    if (draggingIndex === null) return;

    const index = draggingIndex;
    const coordinates = getImageCoordinates(event);

    const svg = svgRef.current;

    if (svg?.hasPointerCapture(event.pointerId)) {
      svg.releasePointerCapture(event.pointerId);
    }

    setDraggingIndex(null);
    setDragPosition(null);
    setHoveredIndex(null);
    setTooltipPosition(null);

    if (!coordinates || !dragMovedRef.current) {
      setDisplayPoints(landmarks);
      return;
    }

    try {
      await onUpdateLandmark?.(
        index,
        coordinates.x,
        coordinates.y
      );
    } catch (error) {
      // Restore the original marker if the backend update fails.
      setDisplayPoints((previous) =>
        previous.map((point, pointIndex) =>
          pointIndex === index
            ? originalPointRef.current
            : point
        )
      );

      console.error("Landmark correction failed:", error);
    } finally {
      dragMovedRef.current = false;
      originalPointRef.current = null;
    }
  };

  const handlePointerCancel = () => {
    if (draggingIndex === null) return;

    setDisplayPoints(landmarks);
    setDraggingIndex(null);
    setDragPosition(null);
    setHoveredIndex(null);
    setTooltipPosition(null);

    dragMovedRef.current = false;
    originalPointRef.current = null;
  };

  if (!imageUrl || !imageWidth || !imageHeight) {
    return (
      <div className="xray-empty">
        <div className="xray-empty-icon">＋</div>
        <h3>No X-ray loaded</h3>
        <p>Upload a cephalometric X-ray to begin analysis.</p>
      </div>
    );
  }

  const hoveredPoint =
    hoveredIndex !== null
      ? displayPoints[hoveredIndex]
      : null;

  return (
    <div
      className="xray-canvas"
      ref={containerRef}
    >
      <div className="heatmap-controls">
        <label>
          <input
            type="checkbox"
            checked={showHeatmap}
            onChange={(event) =>
              setShowHeatmap(event.target.checked)
            }
          />
          Show heatmap
        </label>

        <label>
          Opacity
          <input
            type="range"
            min="0.1"
            max="1"
            step="0.05"
            value={heatmapOpacity}
            onChange={(event) =>
              setHeatmapOpacity(Number(event.target.value))
            }
            disabled={!showHeatmap || !heatmapOverlayUrl}
          />
        </label>
      </div>

      <svg
        ref={svgRef}
        className="xray-svg"
        viewBox={`0 0 ${imageWidth} ${imageHeight}`}
        preserveAspectRatio="xMidYMid meet"
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerCancel={handlePointerCancel}
        onPointerLeave={() => {
          if (draggingIndex === null) {
            setHoveredIndex(null);
            setTooltipPosition(null);
          }
        }}
      >
        {/* Original X-ray */}
        <image
          href={imageUrl}
          x="0"
          y="0"
          width={imageWidth}
          height={imageHeight}
          preserveAspectRatio="none"
        />

        {/* Combined backend-generated colour overlay */}
        {showHeatmap && heatmapOverlayUrl && (
          <image
            href={heatmapOverlayUrl}
            x="0"
            y="0"
            width={imageWidth}
            height={imageHeight}
            preserveAspectRatio="none"
            opacity={heatmapOpacity}
            pointerEvents="none"
          />
        )}

        {/* Landmark markers */}
        {displayPoints.map((point, index) => (
          <LandmarkMarker
            key={point.id ?? index}
            point={point}
            index={index}
            selected={selectedIndex === index}
            hovered={hoveredIndex === index}
            onSelect={onSelect}
            onHover={(hovered) => {
              if (draggingIndex !== null) return;

              if (hovered === null) {
                setHoveredIndex(null);
                setTooltipPosition(null);
              } else {
                setHoveredIndex(hovered);
              }
            }}
            onPointerDown={handlePointerDown}
          />
        ))}
      </svg>

      {/* Hover tooltip */}
      {hoveredPoint && tooltipPosition && (
        <LandmarkTooltip
          point={hoveredPoint}
          index={hoveredIndex}
          position={tooltipPosition}
        />
      )}

      {/* Canvas information */}
      <div className="xray-canvas-info">
        <span>
          {imageWidth} × {imageHeight} px
        </span>

        <span>
          {displayPoints.length} landmarks
        </span>
      </div>
    </div>
  );
};

export default XrayCanvas;
