import * as THREE from 'three';

import { GUI } from 'three/addons/libs/lil-gui.module.min.js';

import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';

import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';

import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';

import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';



const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });

renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setClearColor(0x000000, 1.0); // Black background, full opacity
renderer.setClearAlpha(1.0);

document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(

	60,

	window.innerWidth / window.innerHeight,

	0.1,

	1000

);



const params = {

	red: 0,

	green: 0,

	blue: 1.0,

	threshold: 0.054,

	strength: 0.381,

	radius: 0.8

}

// Animation states
const states = {
	idle: {
		red: 0,
		green: 0.262,
		blue: 1.0,
		threshold: 0.20,
		strength: 0.60,
		radius: 0.8
	},
	processing: {
		red: 0,
		green: 0,
		blue: 1,
		threshold: 0.066,
		strength: 0.603,
		radius: 0.213
	},
	speaking: {
		red: 0.0,
		green: 0.115,
		blue: 1,
		threshold: 0.041,
		strength: 0.198,
		radius: 1.0
	}
}

let currentState = 'idle';
let targetColors = { ...states.idle };
let currentColors = { ...states.idle };
let simulatedFrequency = 0;
let targetFrequency = 0;



renderer.outputColorSpace = THREE.SRGBColorSpace;



const renderScene = new RenderPass(scene, camera);


const bloomPass = new UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight));

bloomPass.threshold = params.threshold;

bloomPass.strength = params.strength;

bloomPass.radius = params.radius;



const bloomComposer = new EffectComposer(renderer);

bloomComposer.addPass(renderScene);

bloomComposer.addPass(bloomPass);



const outputPass = new OutputPass();

bloomComposer.addPass(outputPass);



camera.position.set(50, 0, 20);

camera.lookAt(0, 0, 0);



const uniforms = {

	u_time: { type: 'f', value: 0.0 },

	u_frequency: { type: 'f', value: 0.0 },

	u_red: { type: 'f', value: 0 },

	u_green: { type: 'f', value: 0 },

	u_blue: { type: 'f', value: 1.0 }

}



const mat = new THREE.ShaderMaterial({

	uniforms,

	vertexShader: document.getElementById('vertexshader').textContent,

	fragmentShader: document.getElementById('fragmentshader').textContent

});



// Create icosahedron geometry
const geo = new THREE.IcosahedronGeometry(4, 10);

const mesh = new THREE.Mesh(geo, mat);

// Move ball up vertically
mesh.position.y = 5;

scene.add(mesh);

mesh.material.wireframe = true;

const listener = new THREE.AudioListener();
camera.add(listener);

const soundInputForVisualizer = new THREE.Audio(listener); 

const mainAnalyserAPI = new THREE.AudioAnalyser(soundInputForVisualizer, 256); 

if (!window.auraVisualizer) window.auraVisualizer = {};
window.auraVisualizer.soundForAnalysis = soundInputForVisualizer;
window.auraVisualizer.analyserAPI = mainAnalyserAPI;
window.auraVisualizer.audioListener = listener;

// Function to change animation state
window.auraVisualizer.setState = function(state) {
	if (states[state]) {
		currentState = state;
		targetColors = { ...states[state] };
		console.log('Animation state changed to:', state);
	}
}

// Set initial idle state
window.auraVisualizer.setState('idle');


// const gui = new GUI();



// const colorsFolder = gui.addFolder('Colors');

// colorsFolder.add(params, 'red', 0, 1).onChange(function (value) {

// 	uniforms.u_red.value = Number(value);

// });

// colorsFolder.add(params, 'green', 0, 1).onChange(function (value) {

// 	uniforms.u_green.value = Number(value);

// });

// colorsFolder.add(params, 'blue', 0, 1).onChange(function (value) {

// 	uniforms.u_blue.value = Number(value);

// });



// const bloomFolder = gui.addFolder('Bloom');

// bloomFolder.add(params, 'threshold', 0, 1).onChange(function (value) {

// 	bloomPass.threshold = Number(value);

// });

// bloomFolder.add(params, 'strength', 0, 3).onChange(function (value) {

// 	bloomPass.strength = Number(value);

// });

// bloomFolder.add(params, 'radius', 0, 1).onChange(function (value) {

// 	bloomPass.radius = Number(value);

// });



let mouseX = 0;

let mouseY = 0;

document.addEventListener('mousemove', function (e) {

	let windowHalfX = window.innerWidth / 2;

	let windowHalfY = window.innerHeight / 2;

	mouseX = (e.clientX - windowHalfX) / 100;

	mouseY = (e.clientY - windowHalfY) / 100;

});



const clock = new THREE.Clock();

function animate() {

	camera.position.x += (mouseX - camera.position.x) * .05;

	camera.position.y += (-mouseY - camera.position.y) * 0.5;

	camera.lookAt(scene.position);

	uniforms.u_time.value = clock.getElapsedTime();

	let freq = 0;
    if (window.auraVisualizer && window.auraVisualizer.analyserAPI) { // Check if it's ready
        freq = window.auraVisualizer.analyserAPI.getAverageFrequency();
    }
    
    // Handle frequency based on state
    if (currentState === 'processing') {
    	// Simulate pulsing frequency during processing
    	targetFrequency = 40 + Math.sin(clock.getElapsedTime() * 2) * 20;
    	simulatedFrequency += (targetFrequency - simulatedFrequency) * 0.1;
    	uniforms.u_frequency.value = simulatedFrequency;
    } else if (currentState === 'speaking') {
    	// Use actual audio frequency when speaking
    	uniforms.u_frequency.value = freq;
    	simulatedFrequency = freq; // Track for smooth transition
    } else if (currentState === 'idle') {
    	// Fade out frequency when returning to idle
    	targetFrequency = 0;
    	simulatedFrequency += (targetFrequency - simulatedFrequency) * 0.03;
    	uniforms.u_frequency.value = simulatedFrequency;
    }

	// Smooth color transitions
	const lerpSpeed = 0.05;
	currentColors.red += (targetColors.red - currentColors.red) * lerpSpeed;
	currentColors.green += (targetColors.green - currentColors.green) * lerpSpeed;
	currentColors.blue += (targetColors.blue - currentColors.blue) * lerpSpeed;
	currentColors.threshold += (targetColors.threshold - currentColors.threshold) * lerpSpeed;
	currentColors.strength += (targetColors.strength - currentColors.strength) * lerpSpeed;
	currentColors.radius += (targetColors.radius - currentColors.radius) * lerpSpeed;

	// Apply colors to uniforms and bloom
	uniforms.u_red.value = currentColors.red;
	uniforms.u_green.value = currentColors.green;
	uniforms.u_blue.value = currentColors.blue;
	bloomPass.threshold = currentColors.threshold;
	bloomPass.strength = currentColors.strength;
	bloomPass.radius = currentColors.radius;

	// Add pulsing effect for processing state
	if (currentState === 'processing') {
		const pulse = Math.sin(clock.getElapsedTime() * 3) * 0.2 + 1.0;
		bloomPass.strength = currentColors.strength * pulse;
	}

	// Add slow rotation when idle
	if (currentState === 'idle') {
		mesh.rotation.y += 0.002; // Slow spin on Y axis
		mesh.rotation.x += 0.001; // Slight tilt on X axis
	}

	bloomComposer.render();

	requestAnimationFrame(animate);

}

animate();



window.addEventListener('resize', function () {

	camera.aspect = window.innerWidth / window.innerHeight;

	camera.updateProjectionMatrix();

	renderer.setSize(window.innerWidth, window.innerHeight);

	bloomComposer.setSize(window.innerWidth, window.innerHeight);

});