import * as THREE from "three";
import * as CANNON from "cannon-es";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader";
import { OrbitControls } from "three/addons/controls/OrbitControls";
import CannonDebugger from "cannon-es-debugger";

import * as scenes from "./scenes";

async function load() {
	const [level, cube, car] = await Promise.all([
		scenes.level.gltf,
		scenes.cube.gltf,
		scenes.cube.gltf,
	]);

	// camera
	const camera = level.cameras[0];
	if (camera instanceof THREE.PerspectiveCamera) {
		camera.aspect = canvas.clientWidth / canvas.clientHeight;
		camera.updateProjectionMatrix();
		const controls = new OrbitControls(camera, canvas);
		controls.update();
	}

	level.scene.children.forEach((child) => {
		if (child.type === "Mesh") {
			const mesh = child as THREE.Mesh;

			mesh.receiveShadow = true;

			// if (mesh.geometry.boundingBox) {
			// }

			const body = new CANNON.Body({ mass: 0, material: groundMaterial });
			body.position.copy(mesh.position as unknown as CANNON.Vec3);

			const vertices = mesh.geometry.attributes["position"]!
				.array as unknown as number[];
			const indices = mesh.geometry.index!.array as unknown as number[];
			const shape = new CANNON.Trimesh(vertices, indices);
			body.addShape(shape);

			// const shape = new CANNON.Box(
			//   new CANNON.Vec3(
			//     ...getVec3Tuple(
			//       mesh.geometry.boundingBox.max.divide(new THREE.Vector3(2, 1, 2)),
			//     ),
			//   ),
			// );

			world.addBody(body);

			physicsActors.push({ mesh, body });
		} else if (child.type === "Object3D") {
			const object = child;
			const actorType = child.userData.conduit_actor as string | undefined;
			if (actorType) {
				addActor(actorType, object);
			}
		}
	});
}

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

const physicsActors: {
	mesh: THREE.Mesh;
	body: CANNON.Body;
}[] = [];

type SceneID = keyof typeof scenes;
type ActorType = "car" | "cube";

const actors: Record<
	ActorType,
	{
		add: (object: THREE.Object3D) => void;
		remove: (object: THREE.Object3D) => void;
		objects: THREE.Object3D[];
	}
> = {
	cube: {
		add: (object) => {
			object.add(gltfs.cube.gltf.scene);
		},
		remove: (object) => {},
		objects: [],
	},
	car: {
		add: (object) => {},
		remove: (object) => {},
		objects: [],
	},
};

function addActor(actorType: string, object: THREE.Object3D): void {
	if (!(actorType in actors)) {
		console.warn(`unknown actor: ${actorType}`);
		return;
	}

	const actorRegistry = actors[actorType as ActorType];
	actorRegistry.objects.push(object);
	actorRegistry.add(object);
}

const loader = new GLTFLoader();
loader.load(gltfLevel, (gltf) => {
	console.log(gltfLevel, gltf);

	console.log(physicsActors);

	scene.add(gltf.scene);
});

loader.load(gltfCube, (gltf) => {
	console.log(gltfCube, gltf);
});

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

// DEBUG ONLY
const cannonDebugger = CannonDebugger(scene, world);

function animation(_dt: number) {
	world.fixedStep();
	cannonDebugger.update();

	physicsActors.forEach(({ mesh, body }) => {
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
