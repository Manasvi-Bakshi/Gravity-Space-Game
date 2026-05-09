# Gravity Snake

An atmospheric orbital survival game built with Pygame. Navigate a plasma-ribbon snake through the gravitational pull of a binary star system, collecting energy fragments to grow while maintaining resonance with the orbital ecosystem.


## Core Gameplay
- **Orbital Navigation**: Master momentum-based flight within complex gravity wells.
- **Growth & Inertia**: Collecting fragments increases your length, but also your mass, making movement more deliberate and skillful.
- **Resonance System**: Stay close to the planetary system to maintain signal. Drifting too far into the void causes resonance to decay.
- **Atmospheric Failure**: Elegant, non-violent disintegration states for self-collision, planetary impact, and signal loss.

## Controls
- **W**: Forward Thrust
- **S**: Stabilization / Reverse Thrust
- **A / D**: Rotate Left / Right
- **Q / E**: Lateral Strafe Thrusters
- **SPACE**: Engine Boost (while thrusting) / Restart (on failure)
- **ESC**: Exit

## Installation

### Prerequisites
- Python 3.10 or higher
- [pygame-ce](https://pyga.me/) (Cross-Edition)

### Setup
1. Clone the repository or download the source code.


## Technical Highlights
- **Inverse-Square Gravity**: Real physics-based superposition from multiple planetary bodies.
- **Cinematic Camera**: Smooth interpolation with speed-sensitive zoom and tactile feedback.
- **Plasma Ribbon**: Path-history interpolation for fluid, high-performance tail movement.
- **Additive Rendering**: Custom glow pipeline for vibrant, atmospheric visuals.

## Project Philosophy
Gravity Snake focuses on **flow-state movement** and **minimalist presentation**. The goal was to create a "meditative survival" experience where the challenge comes from mastering orbital mechanics rather than combat or chaotic effects.

## Future Improvements
- **Multiple Systems**: Procedurally generated binary or ternary star systems.
- **Hostile Phenomena**: Black holes or solar flares that distort the ribbon.
- **Advanced HUD**: Integrated diagnostic data displays for orbital velocity.

*Created as a prototype for atmospheric orbital gameplay.*
