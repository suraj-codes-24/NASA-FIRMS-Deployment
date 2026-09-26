/**
 * Dashboard/StatsBar.jsx
 * 
 * Re-exports StatCards from Analytics as StatsBar for spec compliance.
 * The spec (§9.3) requires Dashboard/StatsBar.jsx — this bridges to
 * the actual implementation in Analytics/StatCards.jsx.
 */
export { default } from '../Analytics/StatCards';
