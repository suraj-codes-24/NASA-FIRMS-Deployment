/**
 * IGNIS — Frontend Constants
 * 
 * Classification types, colors, and configuration constants.
 * Must stay in sync with backend/app/utils/constants.py
 */

export const FIRE_TYPES = {
  INDUSTRIAL_FIRE: 'industrial_fire',
  FOREST_FIRE: 'forest_fire',
  GAS_FLARE: 'gas_flare',
  AGRICULTURAL_BURN: 'agricultural_burn',
  MINING_THERMAL: 'mining_thermal',
  UNCLASSIFIED: 'unclassified',
}

export const FIRE_COLORS = {
  [FIRE_TYPES.INDUSTRIAL_FIRE]: '#e74c3c',
  [FIRE_TYPES.FOREST_FIRE]: '#e67e22',
  [FIRE_TYPES.GAS_FLARE]: '#eab308',
  [FIRE_TYPES.AGRICULTURAL_BURN]: '#2ecc71',
  [FIRE_TYPES.MINING_THERMAL]: '#3498db',
  [FIRE_TYPES.UNCLASSIFIED]: '#95a5a6',
}

export const FIRE_LABELS = {
  [FIRE_TYPES.INDUSTRIAL_FIRE]: 'Industrial Fire',
  [FIRE_TYPES.FOREST_FIRE]: 'Forest / Wildfire',
  [FIRE_TYPES.GAS_FLARE]: 'Gas Flare',
  [FIRE_TYPES.AGRICULTURAL_BURN]: 'Agricultural Burn',
  [FIRE_TYPES.MINING_THERMAL]: 'Mining / Thermal',
  [FIRE_TYPES.UNCLASSIFIED]: 'Unclassified',
}

export const FIRE_EMOJIS = {
  [FIRE_TYPES.INDUSTRIAL_FIRE]: '🔴',
  [FIRE_TYPES.FOREST_FIRE]: '🟠',
  [FIRE_TYPES.GAS_FLARE]: '🟡',
  [FIRE_TYPES.AGRICULTURAL_BURN]: '🟢',
  [FIRE_TYPES.MINING_THERMAL]: '🔵',
  [FIRE_TYPES.UNCLASSIFIED]: '⚪',
}

export const SEVERITY_COLORS = {
  critical: '#e74c3c',
  high: '#e67e22',
  medium: '#eab308',
  low: '#3498db',
}

// India map center and default zoom
export const INDIA_CENTER = [22.5, 82.0]
export const DEFAULT_ZOOM = 5

// ESRI Dark Gray Base tile layer
export const MAP_TILE_URL = 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}'
export const MAP_TILE_ATTRIBUTION = 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ'
