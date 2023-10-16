import * as THREE from "three";
import * as CANNON from "cannon-es";
import { OrbitControls } from "three/addons/controls/OrbitControls";
import CannonDebugger from "cannon-es-debugger";

import * as scenes from "./scenes";

const V3 = {
	toTHREE: (vec: CANNON.Vec3) => vec as unknown as THREE.Vector3,
	toCANNON: (vec: THREE.Vector3) => vec as unknown as CANNON.Vec3,
	toTuple: (
		vec: Record<"x" | "y" | "z", number>,
	): [x: number, y: number, z: number] => {
		const { x, y, z } = vec;
		return [x, y, z];
	},
};

(async () => {
	const [level, cube, car] = await Promise.all([
		scenes.level.gltf,
		scenes.cube.gltf,
		scenes.car.gltf,
	]);

	console.log({ level, cube, car });

	const canvas = document.querySelector("#app")!;

	const camera = (() => {
		const camera = level.cameras[0];
		if (camera instanceof THREE.PerspectiveCamera) {
			return camera;
		}
		return new THREE.PerspectiveCamera();
	})();

	camera.aspect = document.body.clientWidth / document.body.clientHeight;
	camera.updateProjectionMatrix();
	const controls = new OrbitControls(camera, canvas);
	controls.update();

	const renderer = new THREE.WebGLRenderer({
		antialias: true,
		canvas: canvas,
	});
	renderer.setSize(window.innerWidth, window.innerHeight);
	renderer.setAnimationLoop(animation);

	const scene = new THREE.Scene();
	scene.background = new THREE.Color("grey");

	const world = new CANNON.World();
	world.gravity.set(0, -9.82, 0);
	world.broadphase = new CANNON.SAPBroadphase(world);
	world.defaultContactMaterial.friction = 0;

	type Actor = { object: THREE.Object3D };
	const actors = {
		cube: [] as Actor[],
		car: [] as Actor[],
	};

	const bodies: { object: THREE.Object3D; body: CANNON.Body }[] = [];

	const materials = {
		ground: new CANNON.Material("ground"),
	};

	level.scene.children.forEach((object) => {
		if (object instanceof THREE.Mesh) {
			const mesh = object;
			mesh.receiveShadow = true;

			type Geometry = THREE.BufferGeometry<{ position: THREE.BufferAttribute }>;
			const indices = (mesh.geometry as Geometry).index!
				.array as unknown as number[];
			const vertices = (mesh.geometry as Geometry).attributes.position
				.array as unknown as number[];
			const shape = new CANNON.Trimesh(vertices, indices);

			const body = new CANNON.Body({
				mass: 0,
				shape,
				material: materials.ground,
				position: V3.toCANNON(mesh.position),
			});

			world.addBody(body);
			bodies.push({ object: mesh, body });
		} else if (object.type === "Object3D") {
			const actorType = object.userData["conduit_actor"] as string | undefined;
			if (actorType && actorType in actors) {
				actors[actorType as keyof typeof actors].push({ object });
			}
		}
	});

	{
		const body = new CANNON.Body({ mass: 0, shape: new CANNON.Plane() });
		body.quaternion.setFromEuler(-Math.PI / 2, 0, 0);
		world.addBody(body);
	}

	scene.add(level.scene);

	{
		const mesh = cube.scene.children[0];
		if (mesh instanceof THREE.Mesh) {
			const shape = new CANNON.Box(
				new CANNON.Vec3(...V3.toTuple(mesh.geometry.boundingBox.max)),
			);

			actors.cube.forEach(({ object }) => {
				const body = new CANNON.Body({
					mass: 1,
					shape,
					material: materials.ground,
					position: V3.toCANNON(object.position),
				});
				world.addBody(body);
				object.add(mesh.clone());
				bodies.push({ object, body });
			});
		}
	}

	{
		const instance: {
			parent: THREE.Object3D;
			collider: THREE.Mesh | undefined;
		} = { parent: new THREE.Object3D(), collider: undefined };

		car.scene.children.forEach((object) => {
			if (object.userData["collider"] && object instanceof THREE.Mesh) {
				instance.collider = object;
			} else {
				instance.parent.add(object.clone());
			}
		});

		const mesh = instance.collider;
		if (mesh) {
			const shape = new CANNON.Box(
				new CANNON.Vec3(...V3.toTuple(mesh.geometry.boundingBox!.max)),
			);

			actors.car.forEach(({ object }) => {
				const body = new CANNON.Body({
					mass: 1,
					shape,
					material: materials.ground,
					position: V3.toCANNON(object.position),
				});
				world.addBody(body);
				object.add(instance.parent);
				bodies.push({ object, body });
			});
		}
	}

	const cannonDebugger = CannonDebugger(scene, world);

	function animation(_dt: number) {
		world.fixedStep();
		cannonDebugger.update();

		bodies.forEach(({ object, body }) => {
			object.position.copy(body.position as unknown as THREE.Vector3);
			object.quaternion.copy(body.quaternion as unknown as THREE.Quaternion);
		});

		renderer.render(scene, camera);
	}
})();

// groundMaterial.friction = 0.25
// groundMaterial.restitution = 0.25

// function addActor(actorType: string, object: THREE.Object3D): void {
//   if (!(actorType in actors)) {
//     console.warn(`unknown actor: ${actorType}`);
//     return;
//   }

//   const actorRegistry = actors[actorType as ActorType];
//   actorRegistry.objects.push(object);
//   actorRegistry.add(object);
// }

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
