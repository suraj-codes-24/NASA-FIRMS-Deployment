import React from 'react';
import { CircleMarker, Popup, Circle } from 'react-leaflet';

const FACILITY_COLOR = '#3b82f6'; // Blue
const BUFFER_RADIUS = 2000; // 2km buffer zone

/**
 * Renders industrial facility markers with 2km buffer circles on the map.
 * Each facility shows its type, name, and OSM ID on click.
 */
export default function FacilityOverlay({ facilities = [] }) {
  if (!facilities.length) return null;

  return (
    <>
      {facilities.map((f, idx) => {
        const lat = f.latitude || f.lat;
        const lng = f.longitude || f.lon;
        if (!lat || !lng) return null;

        return (
          <React.Fragment key={f.id || idx}>
            {/* 2km buffer zone */}
            <Circle
              center={[lat, lng]}
              radius={BUFFER_RADIUS}
              pathOptions={{
                color: FACILITY_COLOR,
                fillColor: FACILITY_COLOR,
                fillOpacity: 0.08,
                weight: 1,
                dashArray: '5, 5',
              }}
            />
            {/* Facility marker */}
            <CircleMarker
              center={[lat, lng]}
              radius={6}
              pathOptions={{
                color: '#fff',
                fillColor: FACILITY_COLOR,
                fillOpacity: 0.9,
                weight: 2,
              }}
            >
              <Popup>
                <div style={{ minWidth: 180 }}>
                  <strong style={{ fontSize: '0.9rem' }}>🏭 {f.name || 'Industrial Facility'}</strong>
                  <hr style={{ margin: '6px 0', opacity: 0.2 }} />
                  <div style={{ fontSize: '0.8rem' }}>
                    <div><b>Type:</b> {f.facility_type || f.type || '—'}</div>
                    <div><b>OSM ID:</b> {f.osm_id || '—'}</div>
                    <div><b>Buffer:</b> 2 km radius</div>
                  </div>
                </div>
              </Popup>
            </CircleMarker>
          </React.Fragment>
        );
      })}
    </>
  );
}
