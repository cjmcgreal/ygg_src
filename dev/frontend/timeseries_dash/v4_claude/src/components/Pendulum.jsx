import { useRef, useState, useEffect } from 'react'
import { useFrame } from '@react-three/fiber'
import { Sphere, Cylinder, Line } from '@react-three/drei'
import * as THREE from 'three'

export default function Pendulum({
  amplitude = 45,      // Starting angle in degrees
  length = 3,          // Length of pendulum
  gravity = 9.81,      // Gravity constant
  timeScale = 1,       // Animation speed multiplier
  bobSize = 0.3,       // Size of the bob
  bobColor = '#ff6b35',// Color of the bob
  ropeThickness = 0.02,// Thickness of the rope
  paused = false,      // Pause animation
  showTrail = true,    // Show motion trail
}) {
  // Physics state
  const [angle, setAngle] = useState((amplitude * Math.PI) / 180) // Convert to radians
  const [angularVelocity, setAngularVelocity] = useState(0)
  const [trail, setTrail] = useState([])

  // Refs for 3D objects
  const bobRef = useRef()
  const pivotRef = useRef()

  // Reset physics when amplitude changes
  useEffect(() => {
    setAngle((amplitude * Math.PI) / 180)
    setAngularVelocity(0)
    setTrail([]) // Clear trail
  }, [amplitude])

  // Clear trail when toggled off
  useEffect(() => {
    if (!showTrail) {
      setTrail([])
    }
  }, [showTrail])

  // Physics simulation using useFrame (runs every frame ~60fps)
  useFrame((state, delta) => {
    if (paused) return

    // Adjust delta time by timeScale
    const dt = delta * timeScale

    // Pendulum physics: angular acceleration = -(g/L) * sin(θ)
    const angularAcceleration = -(gravity / length) * Math.sin(angle)

    // Update angular velocity and angle
    const newAngularVelocity = angularVelocity + angularAcceleration * dt
    const newAngle = angle + newAngularVelocity * dt

    setAngularVelocity(newAngularVelocity)
    setAngle(newAngle)

    // Calculate bob position in world space for trail
    const x = length * Math.sin(newAngle)
    const y = -length * Math.cos(newAngle)

    // Update trail (record last 100 positions in world space)
    if (showTrail && state.clock.getElapsedTime() % 0.05 < dt) {
      setTrail(prevTrail => {
        const newTrail = [...prevTrail, new THREE.Vector3(x, y, 0)]
        return newTrail.slice(-100) // Keep last 100 points
      })
    }
  })

  return (
    <group ref={pivotRef}>
      {/* Pivot point (attachment at top) */}
      <Sphere args={[0.1, 16, 16]} position={[0, 0, 0]}>
        <meshStandardMaterial color="#888" metalness={0.8} roughness={0.2} />
      </Sphere>

      {/* Rope and Bob - rotate together */}
      <group rotation={[0, 0, -angle]}>
        {/* Rope/String - extends to center of bob */}
        <Cylinder
          args={[ropeThickness, ropeThickness, length + bobSize, 8]}
          position={[0, -(length + bobSize) / 2, 0]}
        >
          <meshStandardMaterial color="#444" />
        </Cylinder>

        {/* Bob (the swinging mass) - centered at end of rope */}
        <Sphere
          ref={bobRef}
          args={[bobSize, 32, 32]}
          position={[0, -length, 0]}
          castShadow
        >
          <meshStandardMaterial
            color={bobColor}
            metalness={0.3}
            roughness={0.4}
            emissive={bobColor}
            emissiveIntensity={0.2}
          />
        </Sphere>
      </group>

      {/* Motion trail */}
      {showTrail && trail.length > 1 && (
        <Line
          points={trail}
          color="#4ecdc4"
          lineWidth={2}
          opacity={0.6}
          transparent
        />
      )}

      {/* Reference line (vertical equilibrium) */}
      <Line
        points={[[0, 0, 0], [0, -length, 0]]}
        color="white"
        lineWidth={1}
        opacity={0.2}
        transparent
        dashed
        dashScale={50}
        dashSize={0.1}
        gapSize={0.1}
      />
    </group>
  )
}
