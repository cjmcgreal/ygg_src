import { Canvas } from '@react-three/fiber'
import { OrbitControls, Grid, Sky } from '@react-three/drei'
import { useControls } from 'leva'
import Pendulum from './components/Pendulum'
import './App.css'

function App() {
  // Leva controls for pendulum parameters
  const controls = useControls({
    // Physics parameters
    amplitude: { value: 45, min: 0, max: 90, step: 1, label: 'Swing Amplitude (°)' },
    length: { value: 3, min: 1, max: 10, step: 0.1, label: 'Pendulum Length' },
    gravity: { value: 9.81, min: 1, max: 20, step: 0.1, label: 'Gravity (m/s²)' },
    timeScale: { value: 1, min: 0, max: 3, step: 0.1, label: 'Animation Speed' },

    // Visual parameters
    bobSize: { value: 0.3, min: 0.1, max: 1, step: 0.05, label: 'Bob Size' },
    bobColor: { value: '#ff6b35', label: 'Bob Color' },
    ropeThickness: { value: 0.02, min: 0.01, max: 0.1, step: 0.01, label: 'Rope Thickness' },

    // Animation control
    paused: { value: false, label: 'Pause' },
    showTrail: { value: true, label: 'Show Trail' },
  })

  return (
    <div style={{ width: '100vw', height: '100vh', background: '#1a1a2e' }}>
      {/* Header */}
      <div style={{
        position: 'absolute',
        top: '20px',
        left: '20px',
        zIndex: 1000,
        color: 'white',
        fontFamily: 'system-ui, sans-serif'
      }}>
        <h1 style={{ margin: 0, fontSize: '2rem', fontWeight: 'bold' }}>
          ⚡ Epic 3D Pendulum Simulator
        </h1>
        <p style={{ margin: '5px 0', opacity: 0.8 }}>
          Drag to rotate • Scroll to zoom • Right-click to pan
        </p>
      </div>

      {/* 3D Canvas */}
      <Canvas
        camera={{ position: [5, 3, 8], fov: 50 }}
        shadows
      >
        {/* Lighting */}
        <ambientLight intensity={0.4} />
        <directionalLight
          position={[10, 10, 5]}
          intensity={1}
          castShadow
          shadow-mapSize-width={2048}
          shadow-mapSize-height={2048}
        />
        <pointLight position={[-10, 10, -10]} intensity={0.5} color="#4ecdc4" />

        {/* Sky background */}
        <Sky sunPosition={[100, 20, 100]} />

        {/* Grid for reference */}
        <Grid
          args={[20, 20]}
          cellSize={1}
          cellThickness={0.5}
          cellColor="#6366f1"
          sectionSize={5}
          sectionThickness={1}
          sectionColor="#8b5cf6"
          fadeDistance={30}
          fadeStrength={1}
          position={[0, -0.01, 0]}
        />

        {/* The Pendulum */}
        <Pendulum {...controls} />

        {/* Camera controls */}
        <OrbitControls
          enableDamping
          dampingFactor={0.05}
          minDistance={3}
          maxDistance={20}
          maxPolarAngle={Math.PI / 2}
        />
      </Canvas>

      {/* Instructions */}
      <div style={{
        position: 'absolute',
        bottom: '20px',
        left: '20px',
        color: 'white',
        fontFamily: 'system-ui, sans-serif',
        background: 'rgba(0,0,0,0.5)',
        padding: '15px',
        borderRadius: '8px',
        fontSize: '0.9rem'
      }}>
        <strong>🎮 Controls (top-right panel):</strong>
        <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
          <li>Adjust swing amplitude (angle)</li>
          <li>Change pendulum length</li>
          <li>Modify gravity strength</li>
          <li>Control animation speed</li>
          <li>Customize appearance</li>
        </ul>
      </div>
    </div>
  )
}

export default App
