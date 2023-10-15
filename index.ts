import * as THREE from "three";
import * as CANNON from "cannon-es";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader";
import { OrbitControls } from "three/addons/controls/OrbitControls";

import sceneGltf from "./scene.gltf?url";

const canvas = document.querySelector("#app")!;

let camera = new THREE.PerspectiveCamera();
const scene = new THREE.Scene();
scene.background = new THREE.Color("grey");

const world = new CANNON.World();
world.gravity.set(0, -9.82, 0);
world.broadphase = new CANNON.SAPBroadphase(world);
world.defaultContactMaterial.friction = 0;

const groundMaterial = new CANNON.Material("ground");
// groundMaterial.friction = 0.25
// groundMaterial.restitution = 0.25

const getVec3Tuple = (
	vec3: Record<"x" | "y" | "z", number>,
): [x: number, y: number, z: number] => {
	const { x, y, z } = vec3;
	return [x, y, z];
};

const actors: {
	mesh: THREE.Mesh;
	body: CANNON.Body;
}[] = [];

{
	const url = sceneGltf;
	const gltfLoader = new GLTFLoader();
	gltfLoader.load(url, (gltf) => {
		console.log(gltf);

		camera = gltf.cameras[0];
		camera.aspect = canvas.clientWidth / canvas.clientHeight;
		camera.updateProjectionMatrix();

		const controls = new OrbitControls(camera, canvas);
		controls.update();

		gltf.scene.children.forEach((child) => {
			if (child.type === "Mesh") {
				const mesh = child as THREE.Mesh;

				if (!mesh.geometry.boundingBox) {
					return;
				}

				mesh.receiveShadow = true;

				const mass = child.name === "Plane" ? 0 : 1;

				const body = new CANNON.Body({ mass, material: groundMaterial });
				body.position.copy(mesh.position as unknown as CANNON.Vec3);
				const shape = new CANNON.Box(
					new CANNON.Vec3(
						...getVec3Tuple(
							mesh.geometry.boundingBox.max.divide(new THREE.Vector3(2, 1, 2)),
						),
					),
				);
				body.addShape(shape);
				world.addBody(body);

				actors.push({ mesh, body });
			}
		});

		console.log(actors);

		scene.add(gltf.scene);
	});
}

// const groundWheelContactMaterial = new CANNON.ContactMaterial(
//   groundMaterial,
//   wheelMaterial,
//   {
//     friction: 0.3,
//     restitution: 0,
//     contactEquationStiffness: 1000,
//   },
// );

// world.addContactMaterial(groundWheelContactMaterial);

// const wheelMaterial = new CANNON.Material('wheelMaterial')
// wheelMaterial.friction = 0.25
// wheelMaterial.restitution = 0.25

const renderer = new THREE.WebGLRenderer({ antialias: true, canvas });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setAnimationLoop(animation);

function animation(_dt: number) {
	world.fixedStep();

	actors.forEach(({ mesh, body }) => {
		mesh.position.copy(body.position as unknown as THREE.Vector3);
		mesh.quaternion.copy(body.quaternion as unknown as THREE.Quaternion);
	});

	renderer.render(scene, camera);
}

// camera
// {
//   const fov = 45;
//   const aspect = window.innerWidth / window.innerHeight;
//   const near = 0.01;
//   const far = 10;
//   const camera = new THREE.PerspectiveCamera(fov, aspect, near, far);
// }

// skylight
// {
//   const skyColor = 0xb1e1ff; // light blue
//   const groundColor = 0xb97a20; // brownish orange
//   const intensity = 2;
//   const light = new THREE.HemisphereLight(skyColor, groundColor, intensity);
//   scene.add(light);
// }
